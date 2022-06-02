from rest_framework import serializers
from authorization.models.user import User
from leads.models.service import Service
from leads.models.service_category import ServiceCategory


class VendorSearchSerializer(serializers.Serializer):

    lat = serializers.FloatField(required=True, error_messages={
                                 'required': 'Please enter latitude'})
    lng = serializers.FloatField(required=True, error_messages={
                                 'required': 'Please enter your longitude'})
    date_time = serializers.DateTimeField(required=True, format="%Y-%m-%d %H:%M:%S%z", error_messages={
                                          'required': 'Please enter date and time'})
    service_category = serializers.PrimaryKeyRelatedField(queryset=ServiceCategory.objects.all(), required=True,
                                                          error_messages={'required': 'Please enter service category'})
    urgent = serializers.BooleanField(required=False, error_messages={
                                      'required': 'Please enter urgent'})