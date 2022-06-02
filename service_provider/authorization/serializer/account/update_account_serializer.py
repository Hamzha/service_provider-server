from authorization.models.account import Account
from authorization.serializer.account.custom_validation_serializer import \
    CustomValidationSerializer
from rest_framework import serializers

class UpdateAccountSerializer(CustomValidationSerializer):
    user_id = serializers.PrimaryKeyRelatedField(read_only=True,source='user')
    class Meta:
        model = Account
        exclude = ('user', )
        read_only_fields = [
            'id',
            'created_at',
            'created_by',
            'deleted_at',
            'deleted_by',
            'user_id']
        extra_kwargs ={
            'card_number_hashed':{'write_only':True}
        }
    def __init__(self, *args, **kwargs):
        super(
            UpdateAccountSerializer,
            self).__init__(
            *args,
            **kwargs)
        for field in self.fields:
            self.fields[field].error_messages['required'] = 'Please provide %s' % field
            self.fields[field].error_messages['null'] = '%s can not be null' % field
            self.fields[field].error_messages['blank'] = '%s can not be blank' % field
