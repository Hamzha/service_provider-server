

from django.http import JsonResponse
from authorization.core.user.read import getUserByEmail, getUserByPhoneNumber
from authorization.serializer.account.phone_email_serializer import PhoneEmailValidationSerializer
from authorization.core.utility.serializer_error_formatter import serializerErrorFormatter
from system_returns_code import *
from rest_framework.views import APIView


class UserPhoneEmailvalidate(APIView):

    def get(self, request):
        data = request.query_params.dict()
        phone_email_valifation_serializer =   PhoneEmailValidationSerializer(data = data)
        if phone_email_valifation_serializer.is_valid():
            print(phone_email_valifation_serializer.data)
        else:
            content= serializerErrorFormatter(phone_email_valifation_serializer)
            return JsonResponse(content, status=BAD_REQUEST)
        
        if getUserByEmail(data['email']):
            content = content = {'statusCode': BAD_REQUEST,
                                    'exceptionString': ['Email already exists.'],
                                    'data': {}}
            return JsonResponse(content, status=BAD_REQUEST)

        if getUserByPhoneNumber(data['phone_number']):
            content = content = {'statusCode': BAD_REQUEST,
                                    'exceptionString': ['Phone Number already exists.'],
                                    'data': {}}
            return JsonResponse(content, status=BAD_REQUEST)
        return JsonResponse({'statusCode': SUCCESSFUL,
                             'data': {},
                             'exceptionString': []}, status=SUCCESSFUL)
