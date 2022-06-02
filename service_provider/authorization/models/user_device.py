from django.db import models
from authorization.models.base import BaseModel
from authorization.models.user import User


class UserDevice(BaseModel):

    user = models.ForeignKey(
        User, null=False, blank=False, on_delete=models.CASCADE)
    identifier = models.TextField(max_length=200, null=False, blank=False)
    model = models.TextField(max_length=200, null=True, blank=True)
    os = models.TextField(max_length=200, null=True, blank=True)
    manufacture = models.TextField(max_length=200, null=True, blank=True)
