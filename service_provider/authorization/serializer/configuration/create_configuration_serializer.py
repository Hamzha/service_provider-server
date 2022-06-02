from authorization.models.configuration import Configuration
from rest_framework import serializers


class CreateConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuration
        fields = "__all__"
        read_only_fields = [
            'updated_at',
            'updated_by',
            'deleted_at',
            'deleted_by']

    def __init__(self, *args, **kwargs):
        super(
            CreateConfigurationSerializer,
            self).__init__(
            *args,
            **kwargs)

        for field in self.fields:
            self.fields[field].error_messages['required'] = 'Please provide %s' % field
            self.fields[field].error_messages['null'] = '%s can not be null' % field
            self.fields[field].error_messages['blank'] = '%s can not be blank' % field
