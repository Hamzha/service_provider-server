from django.db import models
from authorization.models.base import BaseModel
from django.utils.translation import gettext_lazy as _
from authorization.models.user import User
from django_cryptography.fields import encrypt


class Account(BaseModel):

    class Months(models.IntegerChoices):
        JAN = 1, _('JAN')
        FEB = 2, _('FEB')
        MAR = 3, _('MAR')
        APR = 4, _('APR')
        MAY = 5, _('MAY')
        JUN = 6, _('JUN')
        JUL = 7, _('JUL')
        AUG = 8, _('AUG')
        SEP = 9, _('SEP')
        OCT = 10, _('OCT')
        NOV = 11, _('NOV')
        DEC = 12, _('DEC')

    card_number = encrypt(models.CharField(
        max_length=100, blank=False, null=False))
    card_number_hashed  = models.CharField(
        max_length=256, blank=False, null=False,unique=True,verbose_name='card number' )
    cvv = encrypt(models.CharField(max_length=100, blank=False, null=False))
    expire_month = encrypt(models.CharField(
        max_length=100, null=False, blank=False))
    expire_year = encrypt(models.CharField(max_length=100,null=False, blank=False))
    stripe_payment_method_id=models.CharField(
        max_length=50, null=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, blank=False)
