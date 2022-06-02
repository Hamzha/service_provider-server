from telnetlib import DO
from django.contrib import admin
from authorization.models.user import User
from authorization.models.document import Document
from authorization.models.location import Location
from authorization.models.configuration import Configuration
from authorization.models.account import Account
from authorization.models.otp import Otp
from authorization.models.user_device import UserDevice
from authorization.models.user_unavailability import UserUnavailability
from django.contrib.auth.admin import UserAdmin

# Register your models here.


admin.site.register(User)
admin.site.register(Location)
admin.site.register(Document)
admin.site.register(Account)
admin.site.register(Otp)
admin.site.register(UserDevice)
admin.site.register(Configuration)
admin.site.register(UserUnavailability)
