from dataclasses import field, fields
from authorization.models.configuration import Configuration
from rest_framework import serializers


class UpdateConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuration
        fields = "__all__"
        read_only_fields = [
            'id',
            'created_at',
            'created_by',
            'deleted_at',
            'deleted_by',
            'user_id']

    def __init__(self, *args, **kwargs):
        super(
            UpdateConfigurationSerializer,
            self).__init__(
            *args,
            **kwargs)
        for field in self.fields:
            self.fields[field].error_messages['required'] = 'Please provide %s' % field
            self.fields[field].error_messages['null'] = '%s can not be null' % field
            self.fields[field].error_messages['blank'] = '%s can not be blank' % field
