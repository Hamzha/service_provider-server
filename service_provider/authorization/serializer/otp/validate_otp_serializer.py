from authorization.models.otp import Otp
from rest_framework import serializers


class ValidateOtpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Otp
        fields = ['otp', 'email']
    def __init__(self, *args, **kwargs):
        super(
            ValidateOtpSerializer,
            self).__init__(
            *args,
            **kwargs)
        for field in self.fields:
            self.fields[field].error_messages['required'] = 'Please provide %s' % field
            self.fields[field].error_messages['null'] = '%s can not be null' % field
            self.fields[field].error_messages['blank'] = '%s can not be blank' % field
            
