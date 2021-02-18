from django.db import models
from django.contrib import auth
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.TextField(max_length=500, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics',blank=True)
    reset_token = models.TextField(null=True, blank=True)
    reset_token_expires = models.DateTimeField(null=True, blank=True)

class ContactMe(models.Model):
    name = models.TextField(max_length=50, blank=True)
    email = models.TextField(max_length=50, blank=True)
    phone = models.TextField(max_length=50, blank=True)
    message = models.TextField(max_length=500, blank=True)

class Subscribers(models.Model):
    email = models.TextField(max_length=50, blank=True)
