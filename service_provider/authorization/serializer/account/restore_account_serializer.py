from authorization.models.account import Account
from authorization.serializer.account.custom_validation_serializer import \
    CustomValidationSerializer
from rest_framework import serializers

class RestoreAccountSerializer(CustomValidationSerializer):
    user_id = serializers.PrimaryKeyRelatedField(read_only=True,source='user')
    class Meta:
        model = Account
        fields = "__all__"
        read_only_fields = ['created_at', 'created_by', 'id']
        extra_kwargs ={
            'user':{'write_only':True},
            'card_number_hashed':{'write_only':True}
        }
    def __init__(self, *args, **kwargs):
        super(
            RestoreAccountSerializer,
            self).__init__(
            *args,
            **kwargs)
        for field in self.fields:
            self.fields[field].error_messages['required'] = 'Please provide %s' % field
            self.fields[field].error_messages['null'] = '%s can not be null' % field
            self.fields[field].error_messages['blank'] = '%s can not be blank' % field