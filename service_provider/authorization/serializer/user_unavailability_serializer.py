from rest_framework import serializers
from authorization.models.user_unavailability import UserUnavailability
from authorization.models.user import User


class UserUnavailabilitySerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        many=False, queryset=User.objects.all(),write_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        read_only=True,source='user')

    class Meta:
        model = UserUnavailability
        fields = ['id', 'reason', 'start_time', 'end_time', 'user',
                  'created_by', 'created_at', 'deleted_by', 'deleted_at','user_id']
        extra_kwargs ={
            'user':{'write_only':True},
        }


class UserUnavailabilityUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserUnavailability
        fields = ['id', 'start_time', 'reason', 'end_time',
                  'created_by', 'created_at', 'updated_at', 'updated_by']
        read_only_fields = ['id', 'created_by', 'created_at']


class CreateUnavailabilityTimeSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        read_only=True,source='user')
    class Meta:
        model = UserUnavailability
        fields = [
            'id',
            'start_time',
            'end_time',
            'reason',
            'created_at',
            'created_by',
            'user',
            'user_id']
        extra_kwargs = {
            'end_time': {'required': True},
            "user": {'required': False,'write_only':True}
        }


    def get_created_at(self, obj):
        return self.context['created_at']

    def get_created_by(self, obj):
        return self.context['created_by']

    def __init__(self, *args, **kwargs):
        super(
            CreateUnavailabilityTimeSerializer,
            self).__init__(
            *args,
            **kwargs)  # call the super()
        for field in self.fields:  # iterate over the serializer fields
            # set the custom error message
            self.fields[field].error_messages['required'] = 'Please provide %s field' % field

    def create(self, validated_data):
        return UserUnavailability.objects.create(
            **validated_data,
            user=self.context['user'],
            created_at=self.context['created_at'],
            created_by=self.context['created_by'])