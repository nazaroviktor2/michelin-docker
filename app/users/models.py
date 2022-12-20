import datetime

from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    is_editor = models.BooleanField(default=False, null=False)
    allow_video = models.BooleanField(default=True, null=False)
    allow_auto_transition = models.BooleanField(default=True, null=False)
