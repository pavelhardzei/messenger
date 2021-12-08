from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.views import Token
from .models import UserProfile
from datetime import datetime


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('email', 'user_name', 'full_name', 'date_of_birth')

    def validate_date_of_birth(self, value):
        if (datetime.now() - datetime.strptime(str(value), '%Y-%m-%d')).days < 0:
            raise ValidationError({'error_message': 'Invalid age'})
        return value


class UserSerializer(UpdateUserSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'email', 'user_name', 'full_name', 'date_of_birth', 'date_joined', 'password')

        extra_kwargs = {'password': {'write_only': True},
                        'date_joined': {'read_only': True}}

    def create(self, validated_data):
        user = UserProfile(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        Token.objects.create(user=user)
        return user


class PasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    password_rep = serializers.CharField(write_only=True)

    class Meta:
        model = UserProfile
        fields = ('old_password', 'password', 'password_rep')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_rep']:
            raise ValidationError({'message_error': 'Passwords did not match'})
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise ValidationError({'message_error': 'Old password is not correct'})
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class TokenSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    user_name = serializers.CharField(required=False)
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        user_name = attrs.get('user_name')
        password = attrs.get('password')

        if email and user_name or not password or not email and not user_name:
            raise ValidationError({'error_message': 'Must include email + pwd or user_name + pwd'})

        if email:
            user = get_object_or_404(UserProfile, email=email)
        else:
            user = get_object_or_404(UserProfile, user_name=user_name)

        user = authenticate(email=user.email, password=password)
        if user:
            if not user.is_active:
                raise ValidationError({'error_message': 'User account is disabled'})
        else:
            raise ValidationError({'error_message': 'Unable to log in with provided credentials'})

        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        super().create(validated_data)

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
