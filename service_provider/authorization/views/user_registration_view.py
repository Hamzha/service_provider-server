import datetime
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from authorization.serializer.user import UserAddSerializer
from django.contrib.auth.hashers import make_password
from authorization.core.user.read import convertStatusToEnum, convertTypeToEnum
from authorization.core.user.read import convertGenderToEnum, convertEnumtoStatus
from authorization.core.user.read import convertEnumToGender, convertEnumToType
from authorization.core.system_changelog.write import create_system_changelog
from authorization.core.user.write import stripe_create_customer
from authorization.models.system_changelog import SystemChangelog
import json
import system_returns_code
from authorization.core.utility.serializer_error_formatter import serializerErrorFormatter


class UserRegistrationView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []

    def post(self, request):
        try:
            params = json.loads(request.body)
        except:
            return JsonResponse(
                {'statusCode': system_returns_code.BAD_REQUEST,
                 'exceptionString': ['Missing Parameters.'],
                 'data': {}},
                status=system_returns_code.BAD_REQUEST)

        try:
            if 'type' in params:
                params['type'] = convertTypeToEnum(params['type'])
            if 'status' in params:
                params['status'] = convertStatusToEnum(params['status'])
            if 'gender' in params:
                params['gender'] = convertGenderToEnum(
                    params['gender'])

        except:
            content = {'statusCode': system_returns_code.BAD_REQUEST,
                       'ExceptionString': ['Please input a valid type, state or gender parameter.'],
                       'data': {}}
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)
        params['created_by'] = request.user.id
        params['created_at'] = datetime.datetime.utcnow()
        user_serielizer = UserAddSerializer(data=params)

        if user_serielizer.is_valid():

            user_serielizer.validated_data['password'] = make_password(
                user_serielizer.validated_data['password'])
            
            # Creating the stripe customer
            customer=stripe_create_customer(user_serielizer.validated_data['first_name'],user_serielizer.validated_data['email'],user_serielizer.validated_data['phone_number'])
            if customer:
                user_serielizer.validated_data['stripe_customer_id']=customer.id
            else:
                content = {'statusCode': system_returns_code.BAD_REQUEST,
                       'exceptionString': ['Something went wrong while creating customer.'],
                       'data': {}}
                return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

            result = user_serielizer.save()
            user = user_serielizer.data
            
            # Adding into the system changelog
            create_system_changelog(
                action_performed=SystemChangelog.ActionPerformed.CREATED,
                changed_in=SystemChangelog.TableName.USER,
                changed_reference_id=result.id,
                description='User has been registered.',
                created_at=params['created_at'],
                created_by=result.id
            )

            user['status'] = convertEnumtoStatus((user['status']))
            user['type'] = convertEnumToType(int(user['type']))
            user['gender'] = convertEnumToGender(int(user['gender']))

            user.pop('password', None)
            content = {'statusCode': system_returns_code.CREATED,
                       'exceptionString': [],
                       'data': user}

            return JsonResponse(content, status=system_returns_code.CREATED)
        else:
            content = serializerErrorFormatter(user_serielizer)
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)
