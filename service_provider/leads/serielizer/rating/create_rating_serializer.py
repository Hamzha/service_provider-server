from rest_framework import serializers
from leads.models.rating import Rating
from leads.models.lead import Lead
from django.db.models import Q


class CreateRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        exclude = ('job',)

    def __init__(self, *args, **kwargs):
        super(
            CreateRatingSerializer,
            self).__init__(
            *args,
            **kwargs)
        for field in self.fields:
            self.fields[field].error_messages['required'] = 'Please provide %s' % field
            self.fields[field].error_messages['null'] = '%s can not be null' % field
            self.fields[field].error_messages['blank'] = '%s can not be blank' % field
