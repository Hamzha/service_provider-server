from django.db.models import fields
from rest_framework import serializers
from authorization.models.document import Document
from authorization.models.user import User
from leads.models.service import Service
from authorization.core.document.read import getDocuentFormatFromEnum, getDocuentTypeFromEnum
from service_provider.config import ConfigUrl
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class DocumentServiceSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        many=False, queryset=User.objects.all(), required=True)
    service = serializers.PrimaryKeyRelatedField(
        many=False, queryset=Service.objects.all(), required=False)

    user_id = serializers.SerializerMethodField()
    service_id = serializers.SerializerMethodField()
    document_url = serializers.SerializerMethodField()
    lead_id = serializers.SerializerMethodField()

    def validate(self, data):
        """
        Check that the start is before the stop.
        """
        if 'user' not in data:
            raise serializers.ValidationError(
                {'Error': "Please provice a valid User ID."})
        if 'user' == None:
            raise serializers.ValidationError(
                {'Error': "Please provice a valid User ID."})

        return data

    class Meta:
        model = Document
        fields = ['id', 'url', 'type', 'name', 'format', 'service', 'user',
                  'user_id', 'document_url',
                  'service_id',
                  'created_at', 'created_by', 'updated_by', 'updated_at', 'deleted_by', 'deleted_at','lead_id']
        write_only_fields = ['service', 'user', 'url']

    def __init__(self, *args, **kwargs):
        super(DocumentServiceSerializer, self).__init__(*args, **kwargs)

        self.fields['url'].error_messages['required'] = u'Please provide a URL.'
        self.fields['type'].error_messages['required'] = u'Please provide the Type.'
        self.fields['name'].error_messages['required'] = u'Please provide Name.'
        self.fields['format'].error_messages['required'] = u'Please provide the Format.'
        self.fields['user'].error_messages['required'] = u'Please provide valid User ID.'

    def get_user_id(self, object):
        if not object.user:
            return object.user
        return object.user.id

    def get_service_id(self, object):
        if not object.service:
            return object.service
        return object.service.id

    def get_lead_id(self, object):
        if not object.lead:
            return object.lead
        return object.lead.id

    def get_format(self, object):
        return getDocuentFormatFromEnum(object.format)

    def get_type(self, object):
        return getDocuentTypeFromEnum(object.type)

    def get_document_url(self, object):
        logger.debug('get url')
        return ConfigUrl.BASE_URL + 'media/' + object.url


class UpdateDocumentServiceSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        many=False, queryset=User.objects.all(), required=False)
    service = serializers.PrimaryKeyRelatedField(
        many=False, queryset=Service.objects.all(), required=False)

    user_id = serializers.SerializerMethodField()
    service_id = serializers.SerializerMethodField()
    lead_id = serializers.SerializerMethodField()

    def validate(self, data):
        """
        Check that the start is before the stop.
        """
        if 'user' not in data:
            raise serializers.ValidationError(
                {'Error': "Please provice a valid User ID."})
        if 'user' == None:
            raise serializers.ValidationError(
                {'Error': "Please provice a valid User ID."})

        return data

    class Meta:
        model = Document
        fields = ['id', 'url', 'type', 'name', 'format', 'service', 'user',
                  'user_id',
                  'service_id',
                  'created_at', 'created_by', 'updated_by', 'updated_at', 'deleted_by', 'deleted_at','lead_id']

        write_only_fields = ['service', 'review', 'url']

    def get_user_id(self, object):
        if not object.user:
            return object.user
        return object.user.id

    def get_service_id(self, object):
        if not object.service:
            return object.service
        return object.service.id

    def get_lead_id(self, object):
        if not object.lead:
            return object.lead
        return object.lead.id

    def get_format(self, object):
        return getDocuentFormatFromEnum(object.format)

    def get_type(self, object):
        return getDocuentTypeFromEnum(object.type)

class GetDocumentSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='get_type_display')
    user_id = serializers.SerializerMethodField()
    service_id = serializers.SerializerMethodField()
    lead_id = serializers.SerializerMethodField()
    class Meta:
        model = Document
        fields = "__all__"
        # excludes = ['user','review','service','lead']
        extra_kwargs = {
            'user': {'write_only': True},
            'service': {'write_only': True},
            'lead': {'write_only': True}
        }
    def get_user_id(self, object):
        if not object.user:
            return object.user
        return object.user.id

    def get_service_id(self, object):
        if not object.service:
            return object.service
        return object.service.id

    def get_lead_id(self, object):
        if not object.lead:
            return object.lead
        return object.lead.id
