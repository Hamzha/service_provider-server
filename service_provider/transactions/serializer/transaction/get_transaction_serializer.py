from rest_framework import serializers
from transactions.models.transaction import Transaction
from authorization.serializer.account.get_account_serializer import GetAccountSerializer
from authorization.models.account import Account
from leads.models.lead import Lead
from leads.models.job import Job
from leads.models.service import Service
from authorization.models.location import Location
from authorization.models.user import User
from leads.core.service.read import getServiceStatefromEnum
from leads.core.service.read import getServiceCategoryfromID


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
        fields = ('id', 'email', 'first_name', 'last_name',)


class GetLeadSerlizer(serializers.ModelSerializer):
    job = GetJobSerializer(many=False, read_only=True)
    service = GetServiceSerializer(many=False, read_only=True)
    vendor = GetUserSerializer(many=False, read_only=True)
    client = GetUserSerializer(many=False, read_only=True)
    state=serializers.CharField(source='get_state_display')
    location_id=serializers.CharField(source='location.id')

    class Meta:
        model = Lead
        exclude = (
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
            'deleted_at',
            'deleted_by')
        extra_kwargs = {
            'location': {'write_only': True}
        }


class GetAccountSerializer(serializers.ModelSerializer):
    user_id=serializers.IntegerField(source='user.id')
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
        extra_kwargs = {
            'user': {'write_only': True}
        }

class GetTransactionSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='get_type_display')
    lead = GetLeadSerlizer(many=False, read_only=True)
    account = GetAccountSerializer(many=False, read_only=True)

    class Meta:
        model = Transaction
        exclude = (
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
            'deleted_at',
            'deleted_by')

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        job = representation['lead'].pop('job')
        service = representation['lead'].pop('service')
        client = representation['lead'].pop('client')
        if client:
            client['total_rating']=0
        vendor = representation['lead'].pop('vendor')
        if vendor:
            vendor['total_rating']=0
        location = None
        if job:
            location = job.pop('location')
        representation['job'] = job
        representation['service'] = service
        representation['location'] = location
        representation['client'] = client
        representation['vendor'] = vendor
        return representation
