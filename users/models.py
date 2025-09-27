# models.py
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class CustomUser(AbstractBaseUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('agent', 'Agent'),
        ('admin', 'Admin'),
    )
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    # username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    role = models.CharField(max_length=5, choices=ROLE_CHOICES, default='user')
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'
    is_anonymous = None
    last_login = None

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.email
