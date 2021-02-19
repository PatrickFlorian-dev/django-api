from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from api.serializers import UserSerializer, GroupSerializer

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.response import Response
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password

from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.utils.crypto import get_random_string

from django.utils import timezone

from rest_framework import serializers

from api.models import Profile , ContactMe , Subscribers

import pytz
from datetime import datetime, timedelta

import logging

import json

from rest_framework import permissions

# VIEWS
# ─▄▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▄
# █░░░█░░░░░░░░░░▄▄░██░█
# █░▀▀█▀▀░▄▀░▄▀░░▀▀░▄▄░█
# █░░░▀░░░▄▄▄▄▄░░██░▀▀░█
# ─▀▄▄▄▄▄▀─────▀▄▄▄▄▄▄▀

# Seen at http://127.0.0.1:8000/hello/ quick test to see if app is running
@permission_classes((permissions.AllowAny,))
class TestView(APIView):

    def get(self, request):
        content = {'message': 'Test successful, demo api Django app is running.'}
        return Response(content)

# Seen at http://127.0.0.1:8000/hello/ quick test for auth
@permission_classes([IsAuthenticated])
class HelloView(APIView):

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)

@permission_classes((permissions.AllowAny,))
class GetUserView(APIView):

    def post(self, request):
        username = request.data.get("username")
        content = {'user': User.objects.filter(username=username).values()}
        return Response(content)

@permission_classes((permissions.AllowAny,))
class SendResetPasswordEmailView(APIView):

    def post(self, request):

        username = request.data.get("username")

        if User.objects.filter(username=username).exists():

            user = User.objects.filter(username=username)
            profile = Profile.objects.filter(user__in=user)
            timezone = pytz.timezone('America/New_York')
            dt_now = datetime.now(timezone)
            tomorrow_start = datetime(dt_now.year, dt_now.month, dt_now.day, tzinfo=timezone) + timedelta(1)
            tomorrow_end = tomorrow_start + timedelta(hours=12)
            tomorrow_end_formatted = tomorrow_end.strftime("%m/%d/%Y, %H:%M:%S")
            reset_token = get_random_string(length=32)
            profile.update(reset_token=reset_token,reset_token_expires=tomorrow_end)

            # send_mail(
            #     'Password Reset',
            #     'Heeeeeeey im a password reset!',
            #     'patrickflorian2@gmail.com',
            #     ['patrickflorian2@gmail.com'],
            #     fail_silently=False,
            # )

            subject, from_email, to = 'Your password reset', 'donotreply@patrickflorian.com', username
            html_content = render_to_string('email/password_reset.html', {'reset_token':reset_token,'username':username}) # render with dynamic value
            text_content = strip_tags(html_content) # Strip the html tag. So people can see the pure text at least.
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            content = {
                'message': 'Password reset email sent',
                'success': True
            }

        else:
            content = {'message': 'Username or email not found', 'success': False}

        return Response(content)

@permission_classes((permissions.AllowAny,))
class ResetPasswordTokenConfirmView(APIView):

    def post(self, request):

        username = request.data.get("username")
        reset_token = request.data.get("reset_token")
        user = User.objects.filter(username=username)
        curTime = timezone.now()

        for p in Profile.objects.filter(user__in=user).values('reset_token','reset_token_expires'):
            print(p['reset_token_expires'])
            print(curTime)
            if(p['reset_token'] == reset_token and p['reset_token_expires'] > curTime):
                content = {'message': 'User token matches and not expired', 'success': True}
            else:
                content = {'message': 'User token does not match or is expired, access denied', 'success': False}
            return Response(content)

@permission_classes((permissions.AllowAny,))
class UpdatePasswordView(APIView):

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = User.objects.filter(username=username)
        user.update(password=make_password(password))
        content = {'message': 'Password updated'}
        return Response(content)

@permission_classes((permissions.AllowAny,))
class RegisterView(APIView):

    def post(self, request):

        print(request.data.get("username"))

        username = request.data.get("username")
        password = request.data.get("password")

        if User.objects.filter(username=username).exists():
            content = {'message': 'User already exists', 'success': False}
            return Response(content)

        else:
            user, created = User.objects.get_or_create(username=username)
            user.set_password(password)
            user.first_name = request.data.get("first_name")
            user.last_name = request.data.get("last_name")
            user.is_staff = request.data.get("is_staff")
            user.save()
            profile = Profile(user=user,phone_number='')
            profile.save()
            content = {'message': 'Registered ok!', 'success': True}
            return Response(content)

@permission_classes((permissions.AllowAny,))
class LogoutView(APIView):

    def get(self, request):

        print(request.user.is_authenticated)

        if request.user.is_authenticated:
            logout(request)
            content = {'message': 'LOGGED OUT'}
        else:
            content = {'message': 'USER ALREADY LOGGED OUT'}

        return Response(content)

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if username is None or password is None:
        return Response({'error': 'Please provide both username and password'},
                        status=HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid Credentials'},
                        status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key},
                    status=HTTP_200_OK)

# DATA TRANSMISSION - CONTACT ME FORM
# NO AUTH NEEDED ANYONE CAN SUBMIT A CONTACT FORM
# WILL VALIDATE AGAINST EMAIL IN THE FUTURE TODO
@permission_classes((AllowAny,))
class SubmitContactFormView(APIView):
    def post(self, request):

        if ContactMe.objects.filter(email=request.data.get("email")).exists():

            content = {'message': 'You have sent an email within the last 24 hours ...', 'success': False}
            return Response(content)

        else:

            contactMeModel = ContactMe(
                name = request.data.get("name"),
                email = request.data.get("email"),
                phone = request.data.get("phone"),
                message = request.data.get("message")
            )

            contactMeModel.save()
            content = {'message': 'Contact form ok!', 'success': True}
            return Response(content)

@permission_classes((permissions.AllowAny,))
class SubscribeView(APIView):
    def post(self, request):

        if Subscribers.objects.filter(email=request.data.get("email")).exists():

            content = {'message': 'You are already subscribed', 'success': False}
            subject, from_email, to = 'Click the link below to unsubscribe', 'donotreply@patrickflorian.com', request.data.get("email")
            html_content = render_to_string('email/unsubscribe.html', {'email': request.data.get("email") })
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return Response(content)

        else:

            subscribeModel = Subscribers(
                email = request.data.get("email"),
            )

            subscribeModel.save()
            content = {'message': 'Subscribed ok!', 'success': True}
            return Response(content)

@permission_classes((permissions.AllowAny,))
class UnsubscribeView(APIView):

    def post(self, request):
        success = True
        email = request.data.get("email")
        subscriber = Subscribers.objects.filter(email=email)
        # This is prevented throgh the frontend but if the user goes back to that link this prevents false positive model deletion on the UI side
        if not subscriber:
            success = False
        else:
            subscriber.delete()
        content = {'message': 'Unsubscribed', 'email' : email, 'success': success }
        return Response(content)

# Seen at http://127.0.0.1:8000/users/
class UserViewSet(viewsets.ModelViewSet):

    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]

    """
    API endpoint that allows users to be viewed or edited.
    """

    # def get(self, request, format=None):
    #     content = {
    #         'user': unicode(request.user),  # `django.contrib.auth.User` instance.
    #         'auth': unicode(request.auth),  # None
    #     }
    #     print(content)

    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

# Seen at http://127.0.0.1:8000/groups/
class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
