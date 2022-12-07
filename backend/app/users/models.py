from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

ROLES = (
    ('user', 'пользователь'),
    ('admin', 'администратор'),
)


class User(AbstractUser):
    username = models.CharField(
        verbose_name='user name',
        max_length=150,
        validators=(
            RegexValidator(r'[\w.@+-]+'),
        ),
        unique=True,
    )
    email = models.EmailField(
        verbose_name='email address',
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='first name',
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name='last name',
        max_length=150,
    )
    password = models.CharField( # todo: add password field
        verbose_name='password',
        max_length=150,
    )
    role = models.CharField(
        max_length=20,
        choices=ROLES,
        blank=True,
        default='user',
    )

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    def save(self, *args, **kwargs):
        if self.is_admin or self.is_superuser:
            self.is_staff = True
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.username