from rest_framework import serializers
from leads.models.lead import Lead
from leads.models.job import Job
from authorization.models.location import Location
from leads.core.service.read import getServiceStatefromEnum
from leads.core.leads.read import get_lead_external_value
from leads.models.service import Service
from transactions.models.transaction import Transaction
from authorization.models.document import Document
from authorization.models.user import User

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

class GetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name',)


class GetTransactionSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='get_type_display')
    account_id = serializers.CharField(source='account.id')

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

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        exclude = (
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
            'deleted_at',
            'deleted_by',)

class GetDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields=['url']

class LeadSerlizer(serializers.ModelSerializer):
    state = serializers.SerializerMethodField()
    job = GetJobSerializer(many=False, read_only=True)
    service = GetServiceSerializer(many=False, read_only=True)
    vendor = GetUserSerializer(many=False, read_only=True)
    client = GetUserSerializer(many=False, read_only=True)
    transaction_lead = GetTransactionSerializer(many=True, read_only=True)
    location=LocationSerializer(many=False, read_only=True)
    document_lead = GetDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Lead
        fields = "__all__"

    def get_state(self, object):
        return get_lead_external_value(object.state)

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        transaction = representation.pop('transaction_lead')
        # Documents
        documents = representation.pop('document_lead')
        documents_urls=[]
        for document in documents:
            documents_urls.append(document['url'])
        # Service
        service = representation.pop('service')
        # Cleint
        client = representation.pop('client')
        if client:
            client['total_rating']=0
        # Vendor
        vendor = representation.pop('vendor')
        if vendor:
            vendor['total_rating']=0
        job = representation.pop('job')
        # location = None
        # if job:
        #     location = job.pop('location')
        representation['service'] = service
        # representation['location'] = location
        representation['client'] = client
        representation['documents']=documents_urls
        representation['vendor'] = vendor
        representation['transaction'] = transaction
        representation['job']=job
        return representation

class CreateLeadSerializer(serializers.ModelSerializer):
    location_id=serializers.SerializerMethodField()
    service_id=serializers.SerializerMethodField()
    client_id=serializers.SerializerMethodField()
    vendor_id=serializers.SerializerMethodField()
    class Meta:
        model = Lead
        fields = "__all__"
        extra_kwargs = {
            'location': {'write_only': True},
            'service': {'write_only': True},
            'client': {'write_only': True},
            'vendor': {'write_only': True}
        }

    def get_location_id(self, object):
        if not object.location:
            return object.location
        return object.location.id

    def get_service_id(self, object):
        if not object.service:
            return object.service
        return object.service.id

    def get_client_id(self, object):
        if not object.client:
            return object.client
        return object.client.id

    def get_vendor_id(self, object):
        if not object.vendor:
            return object.vendor
        return object.vendor.id

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        representation['state'] = get_lead_external_value(representation['state'])
        return representation
