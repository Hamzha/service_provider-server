from transactions.models.transaction import Transaction
from transactions.serializer.transaction.custom_validation_serializer import \
    CustomValidationSerializer
from rest_framework import serializers
from transactions.core.transaction.read import get_transaction_type_display_value

class UpdateTransactionSerializer(CustomValidationSerializer):
    lead_id = serializers.PrimaryKeyRelatedField(read_only=True,source='lead')
    account_id = serializers.PrimaryKeyRelatedField(read_only=True,source='account')
    class Meta:
        model = Transaction
        fields = "__all__"
        read_only_fields = [
            'id',
            'created_at',
            'created_by',
            'deleted_at',
            'deleted_by',
            ]
        extra_kwargs ={
            'lead':{'write_only':True},
            'account':{'write_only':True}
        }
    def to_representation(self, data):
        data = super(UpdateTransactionSerializer, self).to_representation(data)
        data['type'] = get_transaction_type_display_value(data.get('type'))
        return data
    def __init__(self, *args, **kwargs):
        super(
            UpdateTransactionSerializer,
            self).__init__(
            *args,
            **kwargs)
        for field in self.fields:
            self.fields[field].error_messages['required'] = 'Please provide %s' % field
            self.fields[field].error_messages['null'] = '%s can not be null' % field
            self.fields[field].error_messages['blank'] = '%s can not be blank' % field
            