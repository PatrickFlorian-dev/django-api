"""demo_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from api import views
from rest_framework.authtoken.views import obtain_auth_token
from django.conf.urls import url
from django.contrib.auth import views as auth_views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    # url(r'^admin/', admin.site.urls),

    url( r'^login/$',auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),

    # Auth stuff
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('hello/', views.HelloView.as_view(), name='hello'),
    path('test/', views.TestView.as_view(), name='test'),
    path('api/logout/', views.LogoutView.as_view(), name='logout'),
    path('api/register/', views.RegisterView.as_view(), name='register'),
    path('api/profile/', views.GetUserView.as_view(), name='profile'),
    path('api/password-reset/', views.SendResetPasswordEmailView.as_view(), name='passwordReset'),
    path('api/password-reset-confirm/', views.ResetPasswordTokenConfirmView.as_view(), name='passwordResetConfirm'),
    path('api/update-password/', views.UpdatePasswordView.as_view(), name='updatePassword'),

    # Same as base url
    # path('api/v1/', include(router.urls)),

    # These both do the same thing mine just has custom logging logic
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('api/login/', views.login, name='login'),

    # User permissions
    path('accounts/', include('django.contrib.auth.urls')),

    # Master AUTH
    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Contact Me Form
    path('api/contact-me/', views.SubmitContactFormView.as_view(), name='contactMe'),

    # Subscribe Form
    path('api/subscribe/', views.SubscribeView.as_view(), name='subscribe'),

]
