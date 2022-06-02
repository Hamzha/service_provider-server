from django.db import models
from authorization.models.base import BaseModel
from django.utils.translation import gettext_lazy as _

from leads.models.service_category import ServiceCategory
from authorization.models.user import User


class Service(BaseModel):
    class ServiceStatus(models.IntegerChoices):
        APPROVED = 1, _('APPROVED')
        REJECTED = 2, _('REJECTED')
        PENDING = 3, _('PENDING')

    state = models.IntegerField(
        choices=ServiceStatus.choices, blank=False, null=False)
    per_hour_rate = models.FloatField(null=True, blank=True)
    service_category = models.ForeignKey(
        ServiceCategory, on_delete=models.CASCADE, null=False, blank=False,related_name="service_category")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, blank=False,related_name="service_user")

    def __str__(self):
        return self.service_category.name + ' - ' + self.user.first_name + ' ' + str(self.user.last_name)
