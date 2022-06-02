from authorization.models.user_unavailability import UserUnavailability
from rest_framework import serializers


class GetUserUnavailabilitySerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(read_only=True,source='user')
    class Meta:
        model = UserUnavailability
        fields = "__all__"
        extra_kwargs ={
            'user':{'write_only':True},
        }
    def __init__(self, *args, **kwargs):
        super(
            GetUserUnavailabilitySerializer,
            self).__init__(
            *args,
            **kwargs)
        for field in self.fields:
            self.fields[field].error_messages['required'] = 'Please provide %s' % field
            self.fields[field].error_messages['null'] = '%s can not be null' % field
            self.fields[field].error_messages['blank'] = '%s can not be blank' % field
