from datetime import date

from rest_framework import serializers


class CustomValidationSerializer(serializers.ModelSerializer):
    def validate(self, data):
        todays_date = date.today()
        today_year = todays_date.year
        today_month = todays_date.month
        if int(data['expire_year']) == today_year and int(data['expire_month']) <= today_month:
            raise serializers.ValidationError(
                {"Account": "Your account might have been expired"})
        return data

    def validate_expire_year(self, attrs):
        todays_date = date.today()
        today_year = todays_date.year
        if not len(str(attrs)) == 4:
            raise serializers.ValidationError('expire_year must be of length 4')
        if int(attrs) < today_year:
            raise serializers.ValidationError(
                'You account might have been expired')
        return attrs

    def validate_expire_month(self, attrs):
        if int(attrs)<1 or int(attrs)>12:
            raise serializers.ValidationError('Invalid expiry_month')
        return attrs

    def validate_cvv(self, attrs):
        if len(attrs)<3 or len(attrs)>4:
            raise serializers.ValidationError('CVV must be of length 3 or 4')
        return attrs
    
    def validate_card_number(self, attrs):
        if len(attrs)<1 or len(attrs)>16:
            raise serializers.ValidationError('card_number must not be greater then 16')
        return attrs
