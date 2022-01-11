import datetime

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from rest_framework.exceptions import ValidationError


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, user_name, full_name, date_of_birth, password, **extra_fields):
        user = self.model(
            email=self.normalize_email(email),
            user_name=user_name,
            full_name=full_name,
            date_of_birth=date_of_birth,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, user_name, full_name, date_of_birth, password, **extra_fields):
        return self._create_user(email, user_name, full_name, date_of_birth, password, **extra_fields)

    def create_superuser(self, email, user_name, full_name, date_of_birth, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValidationError({'error_message': 'Superuser must have is_staff=True'})
        if extra_fields.get('is_superuser') is not True:
            raise ValidationError({'error_message': 'Superuser must have is_superuser=True'})

        return self._create_user(email, user_name, full_name, date_of_birth, password, **extra_fields)


class UserProfile(AbstractBaseUser):
    email = models.EmailField(unique=True)
    user_name = models.CharField(max_length=30, unique=True)
    full_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    date_joined = models.DateField(default=datetime.date.today)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('user_name', 'full_name', 'date_of_birth')

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def get_full_name(self):
        return f'{self.full_name}'

    def __str__(self):
        return self.email

    @staticmethod
    def query_params():
        return ('email', 'user_name', 'full_name')
