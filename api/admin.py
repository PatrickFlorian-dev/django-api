from django.contrib import admin
from .models import Profile
from .models import ContactMe
from .models import Subscribers

# Register your models here.
admin.site.register(Profile)
admin.site.register(ContactMe)
admin.site.register(Subscribers)
