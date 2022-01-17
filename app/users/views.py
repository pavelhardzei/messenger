from base.utils import check
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from users.models import UserProfile
from users.permissions import IsAdminOrOwner
from users.schemas import UserDetailSchema, UserSignInSchema
from users.serializers import (PasswordSerializer, TokenSerializer, UpdateUserSerializer, UserRoomsSerializer,
                               UserSerializer)


class UserSignUp(generics.CreateAPIView):
    schema = AutoSchema(tags=['users'])
    serializer_class = UserSerializer


class UserSignIn(ObtainAuthToken):
    schema = UserSignInSchema(tags=['users'])
    serializer_class = TokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = TokenSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        return Response({'token': token.key, 'user_id': user.pk, 'email': user.email, 'user_name': user.user_name})


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


class ChangePassword(generics.UpdateAPIView):
    schema = AutoSchema(tags=['users'])
    queryset = UserProfile.objects.all()
    serializer_class = PasswordSerializer
    permission_classes = (IsAdminOrOwner, )

    def get_object(self):
        if self.kwargs['pk'] == 'me':
            self.kwargs['pk'] = self.request.user.pk
        return super().get_object()

    def patch(self, request, *args, **kwargs):
        return Response({'detail': 'Method "PATCH" not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
