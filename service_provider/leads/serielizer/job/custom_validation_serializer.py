from rest_framework import serializers
import datetime as dt
import pytz


class CustomValidationSerializer(serializers.ModelSerializer):
    def validate(self, data):
        starting_time = data['start_datetime']
        ending_time = data['end_datetime']
        if starting_time > ending_time:
            raise serializers.ValidationError(
                {"Date": "Ending time must be greater then starting time"})
        return data

    def validate_end_datetime(self, attrs):
        current_time = dt.datetime.now(tz=pytz.UTC)
        end_time = attrs
        if current_time > end_time:
            raise serializers.ValidationError(
                'End time should be greater then current time.')
        return attrs

    def validate_start_datetime(self, attrs):
        current_time = dt.datetime.now(tz=pytz.UTC)
        starting_time = attrs
        if current_time > starting_time:
            raise serializers.ValidationError(
                'Starting time should be greater then current time.')
        return attrs
