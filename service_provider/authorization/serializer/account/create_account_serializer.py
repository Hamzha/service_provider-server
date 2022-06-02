from numpy import require
from authorization.models.account import Account
from authorization.serializer.account.custom_validation_serializer import \
    CustomValidationSerializer
from rest_framework import serializers
from django_cryptography.fields import encrypt


class CreateAccountSerializer(CustomValidationSerializer):
    user_id = serializers.PrimaryKeyRelatedField(read_only=True,source='user')
    class Meta:
        model = Account
        fields = ["cvv","expire_month","expire_year","user","card_number_hashed","user_id","card_number"]
        read_only_fields = [
            'updated_at',
            'updated_by',
            'deleted_at',
            'deleted_by']
        extra_kwargs ={
            'user':{'write_only':True},
            'card_number_hashed':{'write_only':True}
        }
    def __init__(self, *args, **kwargs):
        super(
            CreateAccountSerializer,
            self).__init__(
            *args,
            **kwargs)
        for field in self.fields:
            self.fields[field].error_messages['required'] = 'Please provide %s' % field
            self.fields[field].error_messages['null'] = '%s can not be null' % field
            self.fields[field].error_messages['blank'] = '%s can not be blank' % field
