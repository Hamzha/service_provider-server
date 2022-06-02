from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from authorization.models.base import BaseModel


class MyUserManager(BaseUserManager):

    def create_superuser(self, email, password=None):
        user = self.model(
            email=email
        )
        user.is_superuser = True
        user.is_staff = True
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractUser, BaseModel):

    class UserType(models.IntegerChoices):
        NONE = 0, _('None')
        VENDOR = 1, _('Vendor')
        CLIENT = 2, _('Client')
        ADMIN = 3, _('Admin')

    class UserStatus(models.IntegerChoices):
        NONE = 0, _('None')
        INACTIVE = 1, _('Inactive')
        ACTIVE = 2, _('Active')
        PENDING = 3, _('Pending')

    class UserGender(models.IntegerChoices):
        NONE = 0, _('None')
        MALE = 1, _('Male')
        FEMALE = 2, _('Female')
        NOT_SPECIFIC = 3, _('Not Specify')

    username = None
    email = models.EmailField(
        verbose_name="email", max_length=60, unique=True, blank=False, null=False)
    first_name = models.CharField(
        max_length=30, default='', blank=False, null=False)
    last_name = models.CharField(
        max_length=30, default='', blank=False, null=False)
    date_of_birth = models.DateTimeField(
        verbose_name='date of birth', blank=True, null=True)
    phone_number = models.CharField(
        max_length=15, blank=True, null=True, unique=True)

    type = models.IntegerField(
        choices=UserType.choices, default=0, blank=False, null=False)
    status = models.IntegerField(
        choices=UserStatus.choices, default='0', blank=False, null=False)
    gender = models.IntegerField(
        choices=UserGender.choices, default=0, blank=False, null=False)

    home_address = models.CharField(
        max_length=1000, blank=False, null=False, default='')
    street_address = models.CharField(
        max_length=1000, blank=False, null=False, default='')
    apartment = models.CharField(
        max_length=1000, blank=False, null=False, default='')
    city = models.CharField(max_length=50, blank=False, null=False, default='')
    state = models.CharField(
        max_length=50, blank=False, null=False, default='')
    zipcode = models.CharField(
        max_length=50, blank=False, null=False, default='')
    country = models.CharField(
        max_length=50, blank=False, null=False, default='')
    stripe_customer_id=models.CharField(
        max_length=100, default='')
    user_bio=models.CharField(
        max_length=500, default='')
    rating = models.IntegerField(default=0, blank=False, null=False)
    no_of_reviews = models.IntegerField(default=0, blank=False, null=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = MyUserManager()

    def __str__(self):
        return self.email
