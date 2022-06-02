from rest_framework import serializers
from leads.models.service import Service
from authorization.models.user import User
from leads.models.service_category import ServiceCategory
from leads.core.service.read import getServiceStatefromEnum
from leads.core.service.read import getServiceCategoryfromID


class ServiceSerlizer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        many=False, queryset=User.objects.all(),write_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        read_only=True,source='user')
    service_category = serializers.PrimaryKeyRelatedField(
        many=False, queryset=ServiceCategory.objects.all())

    class Meta:
        model = Service
        fields = ['state', 'per_hour_rate', 'service_category',
                  'user', 'id', 'created_at', 'created_by', 'updated_at', 'updated_by', 'deleted_by', 'deleted_at','user_id']
        extra_kwargs ={
            'user':{'write_only':True},
        }

    def __init__(self, *args, **kwargs):
        super(ServiceSerlizer, self).__init__(*args, **kwargs)

        self.fields['service_category'].error_messages['required'] = u'Please provide service category.'


class UpdateServceSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        many=False, queryset=User.objects.all(),write_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        read_only=True,source='user')
    service_category = serializers.PrimaryKeyRelatedField(
        many=False, queryset=ServiceCategory.objects.all())

    class Meta:
        model = Service
        fields = ['state', 'per_hour_rate', 'service_category',
                  'user', 'id', 'updated_by', 'updated_at', 'deleted_at',
                  'deleted_by','user_id']
        extra_kwargs ={
            'user':{'write_only':True},
        }

class GetServiceSerializer(serializers.ModelSerializer):
    service_state = serializers.SerializerMethodField()
    service_category = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ['service_state', 'state', 'per_hour_rate', 'service_category', 'service_category',
                  'id', 'created_at', 'created_by', 'deleted_at', 'deleted_by', 'updated_by', 'updated_at']
        extra_kwargs = {
            'state': {'write_only': True},
            'service_category': {'write_only': True}
        }

    def get_service_state(self, object):
        return getServiceStatefromEnum(object.state)

    def get_service_category(self, object):
        return object.service_category.name
