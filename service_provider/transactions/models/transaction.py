from unicodedata import category
from django.db import models
from authorization.models.base import BaseModel
from django.utils.translation import gettext_lazy as _

from authorization.models.account import Account
from leads.models.lead import Lead


class Transaction(BaseModel):

    class TransactionType(models.IntegerChoices):
        PANELTIES = 1, _('PANELTIES')
        LEAD_CHARGES = 2, _('LEAD CHARGES')
        SERVICE_CHARGES = 3, _('SERVICE CHARGES')
        VENDOR_SEARCH = 4, _('VENDOR SEARCH')
        VOLUNTEERS = 5, _('VOLUNTEERS')
        JOB_CREATION = 6, _('JOB CREATION')
    amount = models.FloatField(blank=False, null=False)
    type = models.IntegerField(
        choices=TransactionType.choices, blank=False, null=False)
    
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, null=True, blank=False)
    lead = models.ForeignKey(
        Lead, on_delete=models.CASCADE, null=True, blank=True,related_name='transaction_lead')
    stripe_charge_id=models.CharField(max_length=100,null=True)
