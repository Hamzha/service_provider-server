from unicodedata import category
from django.db.models import fields
from rest_framework import serializers
from leads.core.job.read import get_job_state_display_value
from leads.models.job import Job
from authorization.models.user import User
from rest_framework.validators import UniqueValidator
from leads.models.rating import Rating
from authorization.models.location import Location
from leads.models.lead import Lead
from leads.core.job.read import get_all_jobs
from leads.core.service.read import getServiceStatefromEnum
from authorization.core.location.read import getLocationById
from leads.core.leads.read import get_lead_external_value
from leads.models.service import Service
from leads.models.service_category import ServiceCategory


class UserAddSerializer(serializers.ModelSerializer):
    date_of_birth = serializers.DateTimeField(
        format='%Y-%m-%dT%H:%M:%S.%f%z', required=False)
    email = serializers.EmailField(
        required=True, allow_null=False,
    )
    phone_number = serializers.CharField(validators=[
        UniqueValidator(
            queryset=User.objects.all(),
            message="Phone Number already exists.",
        )]
    )

    def validate_email(self, value):
        lower_email = value.lower()
        if User.objects.filter(email__iexact=lower_email).exists():
            raise serializers.ValidationError("Email already exists")
        return lower_email

    class Meta:
        model = User
        extra_kwargs = {
            "email": {"error_messages": {"required": "Please provide a valid Email Address."}},
            "phone_number": {"error_messeges": {"required": "Please provice a valid Phone Number."}}
        }
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(UserAddSerializer, self).__init__(*args, **kwargs)

        self.fields['email'].error_messages['required'] = u'Please provide a valid Email Address.'
        self.fields['phone_number'].error_messages['required'] = u'Please provide a valid Phone Number.'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'date_of_birth',
                  'phone_number', 'type', 'state', 'gender', "status",
                  'home_address', 'street_address', 'apartment', 'city', 'zipcode',
                  'country', 'created_at', 'created_by', 'updated_by', 'updated_at',
                  'deleted_at', 'deleted_by','user_bio','rating','no_of_reviews']


class DeleteUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'deleted_at', 'deleted_by']


class UpdateUserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(validators=[
        UniqueValidator(
            queryset=User.objects.all(),
            message="Phone Number Already Exists.",
        )]
    )

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'date_of_birth',
            'phone_number', 'type', 'state', 'gender', "status",
            'home_address', 'street_address', 'apartment', 'city', 'zipcode',
            'country', 'created_at', 'created_by', 'updated_by', 'updated_at',
            'deleted_at', 'deleted_by','user_bio']


class CategorySerailizer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        exclude = (
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
            'deleted_at',
            'deleted_by',)


class FilteredServiceSerailizer(serializers.ListSerializer):
    def to_representation(self, data):
        data = data.filter(deleted_by=None,state=Service.ServiceStatus.APPROVED)
        return super(FilteredServiceSerailizer, self).to_representation(data)
class ServiceSerailizer(serializers.ModelSerializer):
    service_category = CategorySerailizer(many=False, read_only=True)
    class Meta:
        model = Service
        exclude = (
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',)
        list_serializer_class=FilteredServiceSerailizer


class RatingSerializer(serializers.ModelSerializer):
    user_id=serializers.SerializerMethodField()
    class Meta:
        model = Rating
        exclude = (
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
            'deleted_at',
            'deleted_by',
            'job')
        extra_kwargs = {
            'user': {'write_only': True}
        }

    def get_user_id(self,object):
        if not object.user:
            return object.user
        return object.user.id


class FilterLocationSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = data.filter(deleted_by=None)
        return super(FilterLocationSerializer, self).to_representation(data)
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        exclude = (
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
            'deleted_at',
            'deleted_by','user')
        list_serializer_class=FilterLocationSerializer


class JobSerializer(serializers.ModelSerializer):
    rating_job = RatingSerializer(many=True, read_only=True)
    job_state = serializers.SerializerMethodField()
    location = LocationSerializer(read_only=True, many= False)

    class Meta:
        model = Job
        exclude = (
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
            'deleted_at',
            'deleted_by','state')
        extra_kwargs = {
            # 'state': {'write_only': True},
            'service_category': {'write_only': True}
        }

    def get_job_state(self, object):
        return get_job_state_display_value(object.state)


class FilterLeadSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = data.filter(deleted_by=None)
        return super(FilterLeadSerializer, self).to_representation(data)
class LeadSerializer(serializers.ModelSerializer):
    job = JobSerializer(many=False, read_only=True)
    lead_state = serializers.SerializerMethodField()
    client_id=serializers.SerializerMethodField()
    vendor_id=serializers.SerializerMethodField()
    service_id=serializers.SerializerMethodField()

    class Meta:
        model = Lead
        exclude = (
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
            'deleted_at',
            'deleted_by', 'location','state')
        extra_kwargs = {
            'client': {'write_only': True},
            'vendor': {'write_only': True},
            'service': {'write_only': True},
        }
        list_serializer_class=FilterLeadSerializer

    def get_lead_state(self, object):
        return get_lead_external_value(object.state)
    
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


class UserSerializerBio(serializers.ModelSerializer):
    location_user = LocationSerializer(many=True, read_only=True)
    lead_client = LeadSerializer(many=True, read_only=True)
    lead_vendor = LeadSerializer(many=True, read_only=True)
    service_user = ServiceSerailizer(many=True, read_only=True)

    class Meta:
        model = User
        exclude = ('stripe_customer_id', 'last_login', 'is_superuser',
                   'is_staff', 'is_active', 'groups', 'user_permissions',)

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        location = representation.pop('location_user')
        if len(location) != 0:
            location = location[0]
        else:
            location = None
        representation['location'] = location

        # Getting lead
        if representation['type'] == User.UserType.VENDOR:
            representation.pop('lead_client')
            leads = representation.pop('lead_vendor')
        else:
            representation.pop('lead_vendor')
            leads = representation.pop('lead_client')

        # Structuring leads
        for lead in leads:
            if lead['job']:
                ratings = lead['job'].pop('rating_job')
                rating_found = None
                for rating in ratings:
                    if representation['type'] == User.UserType.VENDOR:
                        if lead['vendor_id'] == rating['user_id']:
                            rating_found = rating
                    else:
                        if lead['client_id'] == rating['user_id']:
                            rating_found = rating
                lead['rating'] = rating_found
            else:  # If there is no job created
                lead['rating'] = None

        # Get all completed job
        all_completed_job = get_all_jobs(representation['id'], state=2)
        all_completed_job = len(all_completed_job)
        representation['completed_job'] = all_completed_job

        # Initilizing the leads
        representation['leads'] = leads

        # Services
        services = representation.pop('service_user')
        final_services = []
        for service in services:
            final_services.append(service['service_category']['name'])
        representation['other_services'] = final_services
        return representation
        