from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from users.models import UserProfile
from users.permissions import IsAdminOrOwner
from users.serializers import (PasswordSerializer, TokenSerializer,
                               UpdateUserSerializer, UserSerializer)


class UserSignUp(generics.CreateAPIView):
    serializer_class = UserSerializer


class UserSignIn(ObtainAuthToken):
    serializer_class = TokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = TokenSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'user_name': user.user_name
        })


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return permissions.IsAuthenticated(),
        return IsAdminOrOwner(),

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return UpdateUserSerializer

    def get_object(self):
        if self.kwargs['pk'] == 'me':
            self.kwargs['pk'] = self.request.user.pk
        return super().get_object()


class ChangePassword(generics.UpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = PasswordSerializer
    permission_classes = (IsAdminOrOwner, )

    def get_object(self):
        if self.kwargs['pk'] == 'me':
            self.kwargs['pk'] = self.request.user.pk
        return super().get_object()

    def patch(self, request, *args, **kwargs):
        return Response({'detail': f'Method "PATCH" not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
