import os

import pyotp
from base.utils import check
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import HttpResponseRedirect, get_object_or_404
from django_redis import get_redis_connection
from rest_framework import generics, permissions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rooms.serializers import EmptySerializer
from users.models import UserProfile
from users.permissions import IsAdminOrOwner
from users.schemas import TOTPSchema, UserDetailSchema, UserSignInSchema, UsersOnlineSchema
from users.serializers import (PasswordSerializer, ResendVerificationSerializer, TokenSerializer, TOTPSerializer,
                               UpdateUserSerializer, UserListSerializer, UserRoomsSerializer, UserSerializer,
                               UsersOnlineDictSerializer, UserTokenSerializer)


class GoogleCallback(generics.GenericAPIView):
    schema = AutoSchema(tags=['users'])
    serializer_class = EmptySerializer
    authentication_classes = (SessionAuthentication, )

    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return Response({'message': 'Authorize via google'})

        token, _ = Token.objects.get_or_create(user=request.user)
        request.session.clear()

        return HttpResponseRedirect(f"{os.getenv('FRONTEND_REDIRECT')}?token={token.key}")


class UserSignUp(generics.CreateAPIView):
    schema = AutoSchema(tags=['users'])
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = get_object_or_404(UserProfile, id=response.data['id'])
        link = f"{os.getenv('VERIFICATION_LINK')}?user={user.id}&token={default_token_generator.make_token(user)}"

        send_mail('Email verification', f'Follow this link to verify your email: {link}',
                  from_email=settings.EMAIL_HOST_USER, recipient_list=[response.data['email']])

        return response


class EmailVerification(generics.GenericAPIView):
    schema = AutoSchema(tags=['users'])
    serializer_class = EmptySerializer

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(UserProfile, id=request.query_params['user'])

        token = request.query_params['token']
        if not default_token_generator.check_token(user, token):
            return Response({'message': 'Link is invalid or expired. Please, request another confirmation email'},
                            status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.save()
        return Response({'message': 'Email successfully verified'})


class ResendVerification(generics.GenericAPIView):
    schema = AutoSchema(tags=['users'])
    serializer_class = ResendVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(UserProfile, email=serializer.data['email'])
        link = f"{os.getenv('VERIFICATION_LINK')}?user={user.id}&token={default_token_generator.make_token(user)}"

        send_mail('Email verification (repeated)', f'Follow this link to verify your email: {link}',
                  from_email=settings.EMAIL_HOST_USER, recipient_list=[user.email])

        return Response(serializer.data)


class UserSignIn(ObtainAuthToken):
    schema = UserSignInSchema(tags=['users'])
    serializer_class = TokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = TokenSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)

        return Response(UserTokenSerializer({'user': user, 'token': token.key}).data)


class UserList(generics.ListAPIView):
    schema = AutoSchema(tags=['users'])
    serializer_class = UserRoomsSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        check(self.request.query_params.dict().keys(), UserProfile.query_params())

        params = {f'{k}__contains': v for k, v in self.request.query_params.dict().items()}
        return UserProfile.objects.prefetch_related('rooms', 'rooms__room').filter(**params)[:10]


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    schema = UserDetailSchema(tags=['users'])
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        if self.request.method == 'GET':
            return UserProfile.objects.prefetch_related('rooms', 'rooms__room').all()
        return UserProfile.objects.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return permissions.IsAuthenticated(),
        return IsAdminOrOwner(),

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserRoomsSerializer
        return UpdateUserSerializer

    def get_object(self):
        if self.kwargs['pk'] == 'me':
            self.kwargs['pk'] = self.request.user.pk
        return super().get_object()


class ChangePassword(generics.GenericAPIView):
    schema = AutoSchema(tags=['users'])
    queryset = UserProfile.objects.all()
    serializer_class = PasswordSerializer
    permission_classes = (IsAdminOrOwner, )

    def get_object(self):
        if self.kwargs['pk'] == 'me':
            self.kwargs['pk'] = self.request.user.pk
        return super().get_object()

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class TurnTOTP(generics.CreateAPIView):
    schema = TOTPSchema(tags=['users'])
    serializer_class = TOTPSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        user = request.user
        user.secret = pyotp.random_base32() if not user.secret else None
        user.save()

        totp = pyotp.TOTP(user.secret).provisioning_uri()
        return Response(self.get_serializer({'secret': totp}).data)


class UsersOnline(generics.GenericAPIView):
    schema = UsersOnlineSchema(tags=['users'])
    serializer_class = UserListSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        conn = get_redis_connection('default')
        users_online = {}
        for user in serializer.data['users']:
            users_online[user] = conn.sismember(os.getenv('CACHE_USERS_ONLINE'), user)

        return Response(UsersOnlineDictSerializer({'users': users_online}).data)
