from rest_framework import serializers

from authorization.models.location import Location
from authorization.models.user import User


class LocationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        many=False, queryset=User.objects.all(),write_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        read_only=True,source='user')

    def validate(self, data):
        """
        Check that the start is before the stop.
        """
        if 'user' not in data:
            raise serializers.ValidationError(
                {'Error': "Please provice a valid User ID."})
        return data

    class Meta:
        model = Location
        fields = ['lat', 'lng', 'user', 'created_by', 'created_at',
                  "updated_at", "updated_by", 'deleted_at', 'deleted_by','user_id']
        extra_kwargs ={
            'user':{'write_only':True},
        }

    def __init__(self, *args, **kwargs):
        super(LocationSerializer, self).__init__(*args, **kwargs)

        self.fields['lat'].error_messages['required'] = u'Please provide Latitude.'
        self.fields['lng'].error_messages['required'] = u'Please provide Longitude.'


class UpdateLocationSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        read_only=True,source='user')
    class Meta:
        model = Location
        fields = ['lat', 'lng', 'user','user_id', 'created_by',
                  'created_at', "updated_at", "updated_by", 'deleted_by', 'deleted_at']
        extra_kwargs ={
            'user':{'write_only':True},
        }

class LocationSerializerWithoutUser(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['lat', 'lng', 'created_by', 'created_at',
                  "updated_at", "updated_by", 'deleted_at', 'deleted_by']


    def __init__(self, *args, **kwargs):
        super(LocationSerializerWithoutUser, self).__init__(*args, **kwargs)

        self.fields['lat'].error_messages['required'] = u'Please provide Latitude.'
        self.fields['lng'].error_messages['required'] = u'Please provide Longitude.'
