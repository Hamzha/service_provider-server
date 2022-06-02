from django.db import models
from authorization.models.base import BaseModel
from django.utils.translation import gettext_lazy as _

from authorization.models.user import User
from leads.models.service import Service
from leads.models.lead import Lead


class Document(BaseModel):

    class DocumentType(models.IntegerChoices):
        CERTIFICATE = 1, _('CERTIFICATE')
        IMAGE = 2, _('IMAGE')
        REVIEW = 3, _('REVIEW')
        JOB = 4, _('JOB')
        LEAD = 5, _('LEAD')

    class DocumentFormat(models.IntegerChoices):
        PDF = 1, _('PDF')
        JPG = 2, _('JPG')
        PNG = 3, _('PNG')
        JPEG = 4, _('JPEG')

    url = models.CharField(max_length=50, blank=False, null=False)
    type = models.IntegerField(
        choices=DocumentType.choices, default=1, blank=False, null=False)
    name = models.CharField(max_length=50, blank=True, null=True)
    format = models.IntegerField(
        choices=DocumentFormat.choices, default=3, blank=False, null=False)

    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, blank=True, null=True)
    lead = models.ForeignKey(
        Lead, on_delete=models.CASCADE, blank=True, null=True,related_name='document_lead')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True
    )
