from numpy import source
from stripe import client_id
from leads.models.lead import Lead
from rest_framework import serializers


class UpdateLeadSerializer(serializers.ModelSerializer):
    client_id = serializers.CharField(source='client.id', read_only=True)
    vendor_id = serializers.CharField(source='vendor.id', read_only=True)
    location_id = serializers.CharField(source='location.id', read_only=True)
    job_id = serializers.CharField(source='job.id', read_only=True)
    service_id = serializers.CharField(source='service.id', read_only=True)
    state = serializers.CharField(source='get_state_display')
    class Meta:
        model = Lead
        fields = "__all__"
        read_only_fields = [
            'id',
            'created_at',
            'created_by',
            'deleted_at',
            'deleted_by',
            'service',
            'client',
            'vendor',
            'job',
            'urgent',
            'location']
    def to_representation(self, instance):
        representation=super().to_representation(instance)
        representation.pop('client')
        representation.pop('vendor')
        representation.pop('location')
        representation.pop('job')
        representation.pop('service')
        return representation

    def __init__(self, *args, **kwargs):
        super(
            UpdateLeadSerializer,
            self).__init__(
            *args,
            **kwargs)
        for field in self.fields:
            self.fields[field].error_messages['required'] = 'Please provide %s' % field
            self.fields[field].error_messages['null'] = '%s can not be null' % field
            self.fields[field].error_messages['blank'] = '%s can not be blank' % field