from rest_framework import serializers


class CustomValidationSerializer(serializers.ModelSerializer):
    def validate_account(self, attrs):
        if not attrs:
            raise serializers.ValidationError('This Field can not be null')
        else:
            return attrs

    def validate_lead(self, attrs):
        if not attrs:
            raise serializers.ValidationError('This Field can not be null')
        else:
            return attrs
