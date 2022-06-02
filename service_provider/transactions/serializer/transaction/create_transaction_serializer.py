from transactions.models.transaction import Transaction
from transactions.serializer.transaction.custom_validation_serializer import \
    CustomValidationSerializer
from transactions.core.transaction.read import get_transaction_type_display_value
from rest_framework import serializers


class CreateTransactionSerializer(CustomValidationSerializer):
    lead_id = serializers.PrimaryKeyRelatedField(read_only=True, source='lead')
    account_id = serializers.PrimaryKeyRelatedField(
        read_only=True, source='account')

    class Meta:
        model = Transaction
        fields = "__all__"
        read_only_fields = [
            'updated_at',
            'updated_by',
            'deleted_at',
            'deleted_by']
        extra_kwargs = {
            'lead': {'write_only': True},
            'account': {'write_only': True}
        }

    def to_representation(self, data):
        data = super(CreateTransactionSerializer, self).to_representation(data)
        data['type'] = get_transaction_type_display_value(data.get('type'))
        return data

    def __init__(self, *args, **kwargs):
        super(
            CreateTransactionSerializer,
            self).__init__(
            *args,
            **kwargs)
        for field in self.fields:
            id = ''
            if field == 'account' or field == 'lead':
                id = '_id'
            self.fields[field].error_messages['required'] = 'Please provide %s%s' % (
                field, id)
            self.fields[field].error_messages['null'] = '%s%s can not be null' % (
                field, id)
            self.fields[field].error_messages['blank'] = '%s%s can not be blank' % (
                field, id)
            self.fields[field].error_messages['does_not_exist'] = '%s%s does not exist' % (
                field, id)
