from unittest.util import _MAX_LENGTH
from rest_framework import serializers


class PhoneEmailValidationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    email = serializers.EmailField()

    def __init__(self, *args, **kwargs):
        super(
            PhoneEmailValidationSerializer,
            self).__init__(
            *args,
            **kwargs)
        for field in self.fields:
            self.fields[field].error_messages['required'] = 'Please provide %s.' % field
            self.fields[field].error_messages['null'] = '%s can not be null.' % field
            self.fields[field].error_messages['blank'] = '%s can not be blank.' % field
