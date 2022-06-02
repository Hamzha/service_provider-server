from django.db import models
from authorization.models.base import BaseModel
from authorization.models.user import User


class Location(BaseModel):
    lat = models.FloatField(blank=False, null=False)
    lng = models.FloatField(blank=False, null=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True,related_name='location_user')

    def __str__(self):
        if self.user:
            return self.user.email
        else:
            return "NONE"
