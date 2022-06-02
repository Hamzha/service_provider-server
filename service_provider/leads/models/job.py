from django.db import models
from authorization.models.base import BaseModel
from django.utils.translation import gettext_lazy as _
from authorization.models.location import Location


class Job(BaseModel):
    class JobState(models.IntegerChoices):
        PENDING = 1, _('PENDING')
        COMPLETE = 2, _('COMPLETE')
        INCOMPLETE = 3, _('INCOMPLETE')
        CANCELED = 4, _('CANCELED')
        ON_MY_WAY = 5, _('ON_MY_WAY')
        ARRIVED = 6, _('ARRIVED')

    start_datetime = models.DateTimeField(null=False, blank=False)
    end_datetime = models.DateTimeField(null=False, blank=False)
    state = models.IntegerField(
        choices=JobState.choices, blank=False, null=False)
    earning = models.FloatField(null=True)
    