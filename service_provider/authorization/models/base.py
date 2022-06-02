import datetime
from django.db import models
from django.conf import settings
from django.utils.timezone import make_aware
from django.forms.models import model_to_dict
from django.utils import timezone
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now=False, null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=False, null=True, blank=True)
    updated_by = models.IntegerField(null=True, blank=True)

    deleted_at = models.DateTimeField(auto_now=False, null=True, blank=True)
    deleted_by = models.IntegerField(null=True, blank=True)

    class Meta:
        """meta class for common model fields."""
        abstract = True

    def delete(self, user: int):
        """Cascade Delete item from the table.

        Args:
            using:
            keep_parents:
        """
        logger.debug(f'log from delete [BaseModel]')
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save()
