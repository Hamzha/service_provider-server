from rest_framework import serializers
from transactions.models.transaction import Transaction
from leads.models.job import Job
from authorization.models.account import Account
from leads.models.lead import Lead
from leads.models.job import Job
from leads.models.service import Service
from authorization.models.location import Location
from authorization.models.user import User
from leads.core.service.read import getServiceStatefromEnum


class GetServiceSerializer(serializers.ModelSerializer):
    service_state = serializers.SerializerMethodField()
    service_category = serializers.SerializerMethodField()

    class Meta:
        model = Service
        exclude = (
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
            'deleted_at',
            'deleted_by',
            'user')
        extra_kwargs = {
            'state': {'write_only': True},
            'service_category': {'write_only': True}
        }

    def get_service_state(self, object):
        return getServiceStatefromEnum(object.state)

    def get_service_category(self, object):
        return object.service_category.name


class GetLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        exclude = (
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
            'deleted_at',
            'deleted_by',
            'user')


class GetJobSerializer(serializers.ModelSerializer):
    state = serializers.CharField(source='get_state_display')
    location = GetLocationSerializer(many=False, read_only=True)

    class Meta:
        model = Job
        exclude = (
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
            'deleted_at',
            'deleted_by')


class GetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name','rating',)


class GetTransactionSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='get_type_display')
    account_id=serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        exclude = (
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
            'deleted_at',
            'deleted_by',
            'lead',
            'account')
    def get_account_id(self, object):
        if not object.account:
            return object.account
        return object.account.id


class GetLeadSerlizer(serializers.ModelSerializer):
    job = GetJobSerializer(many=False, read_only=True)
    service = GetServiceSerializer(many=False, read_only=True)
    vendor = GetUserSerializer(many=False, read_only=True)
    client = GetUserSerializer(many=False, read_only=True)
    transaction_lead = GetTransactionSerializer(many=True, read_only=True)
    state = serializers.CharField(source='get_state_display')

    class Meta:
        model = Lead
        exclude = (
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
            'deleted_at',
            'deleted_by')


class GetAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        exclude = (
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
            'deleted_at',
            'deleted_by',
            'card_number_hashed')


class GetJobSerializer(serializers.ModelSerializer):
    state = serializers.CharField(source='get_state_display')
    lead_job = GetLeadSerlizer(many=False, read_only=True)

    class Meta:
        model = Job
        exclude = (
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
            'deleted_at',
            'deleted_by')

    def __init__(self, *args, **kwargs):
        super(
            GetJobSerializer,
            self).__init__(
            *args,
            **kwargs)
        for field in self.fields:
            self.fields[field].error_messages['required'] = 'Please provide %s' % field
            self.fields[field].error_messages['null'] = '%s can not be null' % field
            self.fields[field].error_messages['blank'] = '%s can not be blank' % field

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        lead = representation.pop('lead_job')
        if lead:
            lead['location_id']=lead['location']
            lead.pop('location')
        transaction = lead.pop('transaction_lead')
        service = lead.pop('service')
        client = lead.pop('client')
        if client:
            client['total_rating']=client['rating']
            client.pop('rating')
        vendor = lead.pop('vendor')
        if vendor:
            vendor['total_rating']=vendor['rating']
            vendor.pop('rating')
        job = lead.pop('job')
        representation['service'] = service
        representation['client'] = client
        representation['vendor'] = vendor
        representation['lead'] = lead
        representation['transaction'] = transaction
        return representation
