from rest_framework import serializers
from leads.models.rating import Rating


class GetRatingSerializer(serializers.ModelSerializer):
    job_id = serializers.PrimaryKeyRelatedField(read_only=True, source='job')
    user_id = serializers.SerializerMethodField()
    class Meta:
        model = Rating
        fields = '__all__'
        extra_kwargs = {
            'job': {'write_only': True},
            'user': {'write_only': True},
        }

    def get_user_id(self, object):
        if not object.user:
            return object.user
        return object.user.id

    def __init__(self, *args, **kwargs):
        super(
            GetRatingSerializer,
            self).__init__(
            *args,
            **kwargs)
        for field in self.fields:
            self.fields[field].error_messages['required'] = 'Please provide %s' % field
            self.fields[field].error_messages['null'] = '%s can not be null' % field
            self.fields[field].error_messages['blank'] = '%s can not be blank' % field
