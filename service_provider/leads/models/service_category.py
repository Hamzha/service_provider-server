from django.db import models
from authorization.models.base import BaseModel
from django.utils.translation import gettext_lazy as _


class ServiceCategory(BaseModel):
    name = models.CharField(max_length=100, null=False, blank=False)
    parent_id = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name
