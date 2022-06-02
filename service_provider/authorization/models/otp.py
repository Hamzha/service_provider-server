import math
import random

from authorization.models.base import BaseModel
from authorization.models.user import User
from django.core.validators import RegexValidator
from django.db import models


class Otp(BaseModel):
    time_added = models.DateTimeField(
        blank=False, null=False, auto_now_add=True)
    otp = models.IntegerField(
        blank=False,
        null=False,
        validators=[
            RegexValidator(
                "^[0-9]{4}$",
                'Invalid OTP')],
    )
    email = models.EmailField(
        blank=False, null=False)
