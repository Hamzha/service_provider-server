from pyexpat import model
from django.db import models
from authorization.models.base import BaseModel
from django.utils.translation import gettext_lazy as _


class SystemChangelog(BaseModel):

    class ActionPerformed(models.IntegerChoices):
        CREATED = 1, _('CREATED')
        UPDATED = 2, _('UPDATED')
        DELETED = 3, _('DELETED')

    class TableName(models.IntegerChoices):
        ACCOUNT = 1, _('ACCOUNT')
        DOCUMENT = 2, _('DOCUMENT')
        LOCATION = 3, _('LOCATION')
        OTP = 4, _('OTP')
        UserUnavailability = 5, _('UserUnavailability')
        USER = 6, _('USER')
        JOB = 7, _('JOB')
        LEAD = 8, _('LEAD')
        SERVICECATEGORY = 9, _('SERVICECATEGORY')
        SERVICE = 10, _('SERVICE')
        REVIEW = 11, _('REVIEW')
        TRANSACTION = 12, _('TRANSACTION')
        USER_DEVICE = 13, _('USER_DEVICE')
        CONFIGURATION = 14, _('CONFIGURATION')
        RATING = 15, _('RATING')

    action_performed = models.IntegerField(
        choices=ActionPerformed.choices,
        null=False,
        blank=False,
        editable=False)
    changed_in = models.IntegerField(
        choices=TableName.choices, null=False, blank=False, editable=False)
    changed_reference_id = models.IntegerField(
        null=False, blank=False, editable=False)
    description = models.CharField(
        max_length=100, null=False, blank=False, editable=False)
