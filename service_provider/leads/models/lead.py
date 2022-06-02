from django.db import models
from authorization.models.base import BaseModel
from django.utils.translation import gettext_lazy as _
from leads.models.service import Service
from authorization.models.user import User
from leads.models.job import Job
from authorization.models.location import Location


class Lead(BaseModel):
    class LeadState(models.IntegerChoices):
        PENDING = 1, _('PENDING'),
        ACCEPTED = 2, _('ACCEPTED'),
        VENDOR_REJECTED = 3, _('VENDOR_REJECTED'),
        CLIENT_REJECTED = 4, _('CLIENT_REJECTED')

    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, blank=False, null=False)
    client = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=False, null=False, related_name='lead_client')
    vendor = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=False, null=False, related_name='lead_vendor')
    job = models.OneToOneField(
        Job, on_delete=models.CASCADE, null=True, related_name='lead_job')
    urgent = models.BooleanField(default=False)
    state = models.IntegerField(
        choices=LeadState.choices, blank=False, null=False)
    location = models.OneToOneField(Location, verbose_name="lead_location", on_delete=models.CASCADE)
    description = models.CharField(max_length=500,null=True,blank=False)
    quotation_description = models.CharField(max_length=500,null=True,blank=False)
    quotation_price = models.FloatField(null=True)
