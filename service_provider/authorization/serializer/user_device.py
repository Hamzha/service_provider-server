from rest_framework import serializers
from authorization.models.user import User
from authorization.models.user_device import UserDevice


class UserdeviceSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        many=False, queryset=User.objects.all(),write_only=True)

    def validate(self, data):
        """
        Check that the start is before the stop.
        """
        if 'user' not in data:
            raise serializers.ValidationError(
                {'Error': "Please provice a valid User ID."})
        return data
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = UserDevice
        fields = ['id', 'user', 'user_id', 'identifier', 'model', 'os', 'manufacture', 'created_at', 'created_by',
                  'deleted_by', 'deleted_at', 'updated_by', 'updated_at']
        extra_kwargs = {
            'created_at': {'write_only': True},
            'created_by': {'write_only': True},
            'deleted_at': {'write_only': True},
            'deleted_by': {'write_only': True},
            'updated_by': {'write_only': True},
            'updated_at': {'write_only': True},
            "user": {'write_only': True},
            "identifier": {
                "error_messages": {
                    "required": "Please provide a identifier."
                }
            },
            "user": {
                "error_messages": {
                    "required": "Please provide a Valid User ID."
                }
            }


        }

        def __init__(self, *args, **kwargs):
            super(UserDevice, self).__init__(*args, **kwargs)

            self.fields['identifier'].error_messages['required'] = u'My custom required msg'

    def get_user_id(self, object):
        return object.user.id
