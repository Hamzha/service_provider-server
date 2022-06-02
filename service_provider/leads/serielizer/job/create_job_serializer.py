from leads.models.job import Job
from leads.serielizer.job.custom_validation_serializer import CustomValidationSerializer
from rest_framework import serializers
from leads.core.job.read import get_job_state_display_value



class CreateJobSerializer(CustomValidationSerializer):
    class Meta:
        model = Job
        fields = "__all__"
        read_only_fields = ['updated_at', 'updated_by',
                            'deleted_at', 'deleted_by', 'id']
    def to_representation(self, data):
        data = super(CreateJobSerializer, self).to_representation(data)
        data['state'] = get_job_state_display_value(data.get('state'))
        return data
    def __init__(self, *args, **kwargs):
        super(
            CreateJobSerializer,
            self).__init__(
            *args,
            **kwargs)
        for field in self.fields:
            self.fields[field].error_messages['required'] = 'Please provide %s' % field
            self.fields[field].error_messages['null'] = '%s can not be null' % field
            self.fields[field].error_messages['blank'] = '%s can not be blank' % field