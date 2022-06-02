from rest_framework import serializers
from leads.models.rating import Rating
from leads.models.lead import Lead
from django.db.models import Q


class UpdateRatingSerializer(serializers.ModelSerializer):
    job_id = serializers.PrimaryKeyRelatedField(read_only=True, source='job')

    class Meta:
        model = Rating
        fields = "__all__"
        read_only_fields = [
            'id',
            'job',
            'created_at',
            'created_by',
            'deleted_at',
            'deleted_by']

    def __init__(self, *args, **kwargs):
        super(
            UpdateRatingSerializer,
            self).__init__(
            *args,
            **kwargs)
        for field in self.fields:
            self.fields[field].error_messages['required'] = 'Please provide %s' % field
            self.fields[field].error_messages['null'] = '%s can not be null' % field
            self.fields[field].error_messages['blank'] = '%s can not be blank' % field
