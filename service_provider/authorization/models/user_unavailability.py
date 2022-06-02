from django.db import models
from authorization.models.base import BaseModel
from authorization.models.user import User

class UserUnavailability(BaseModel):
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    reason = models.TextField(blank=True, null=True)

    monday=models.BooleanField(default=False)
    tuesday=models.BooleanField(default=False)
    wednesday=models.BooleanField(default=False)
    thursday=models.BooleanField(default=False)
    friday=models.BooleanField(default=False)
    saturday=models.BooleanField(default=False)
    sunday=models.BooleanField(default=False)

    offline=models.BooleanField(default=False)

    user = models.OneToOneField(User, blank=False, null=False , on_delete=models.CASCADE)

    def __str__(self):
        return self.user.email
