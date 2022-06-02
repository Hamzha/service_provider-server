import datetime
from functools import partial
import json
from re import S
import sys
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.forms.models import model_to_dict
from rest_framework import status

from django.contrib.auth.hashers import make_password

from authorization.core.user.read import checkUserdelete, checkEmailAvailability
from authorization.core.user.read import getUserByEmail
from authorization.core.user.write import deleteUser, updateUserByEmail
from authorization.core.utility.serializer_error_formatter import serializerErrorFormatter
from authorization.core.user.read import convertEnumToGender, convertEnumToType, convertEnumtoStatus
from authorization.core.user.read import getUserById
from authorization.serializer.user import UserSerializer, UserSerializerBio
from authorization.serializer.user import DeleteUserSerializer
from authorization.serializer.user import UpdateUserSerializer
import system_returns_code
from authorization.models.system_changelog import SystemChangelog
from authorization.models.document import Document
from authorization.core.document.read import getDocumentByService
from authorization.core.system_changelog.write import create_system_changelog
from authorization.serializer.document import GetDocumentSerializer


class UserView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if 'user_id' not in request.query_params:
            user = getUserById(request.user.id)
            if checkUserdelete(user):
                content = {'statusCode': system_returns_code.NOT_FOUND,
                           'exceptionString': ['Record not Found.'],
                           'data': {}}
                return JsonResponse(content, status=system_returns_code.SUCCESSFUL)
            if 'user_bio' in request.query_params:
                user_serializer = UserSerializerBio(user)
            else:
                user_serializer = UserSerializer(user)
            data = user_serializer.data
            data['status'] = convertEnumtoStatus(data.get('status'))
            data['gender'] = convertEnumToGender(data.get('gender'))
            data['type'] = convertEnumToType(data.get('type'))
            data.pop('password', None)
            content = {'statusCode': system_returns_code.SUCCESSFUL,
                       'exceptionString': [],
                       'data': data}
            return JsonResponse(content, status=system_returns_code.SUCCESSFUL)
        else:
            user_id = int(request.query_params.get('user_id'))
            # if request.user.id != user_id:
            #     content = {'status_code': system_returns_code.UNANTTHORIZED,
            #                'exceptionString': ['Unathorized'],
            #                'data': {}}
            #     return JsonResponse(content, status=system_returns_code.UNANTTHORIZED)
            
            user = getUserById(user_id)
            if checkUserdelete(user):
                content = {'statusCode': system_returns_code.NOT_FOUND,
                           'exceptionString': ['Record not Found.'],
                           'data': {}}
                return JsonResponse(content, status=system_returns_code.SUCCESSFUL)
            if 'user_bio' in request.query_params:
                user_serializer = UserSerializerBio(user)
            else:
                user_serializer = UserSerializer(user)
            data = user_serializer.data
            data['status'] = convertEnumtoStatus(data.get('status'))
            data['gender'] = convertEnumToGender(data.get('gender'))
            data['type'] = convertEnumToType(data.get('type'))
            if 'user_bio' in request.query_params:
                document = getDocumentByService(request.query_params['service_id'])
                document_serializer=GetDocumentSerializer(document,many=True)
                data['documents']=document_serializer.data

            data.pop('password', None)

            content = {'statusCode': system_returns_code.SUCCESSFUL,
                       'exceptionString': [],
                       'data': data}
            return JsonResponse(content, status=system_returns_code.SUCCESSFUL)

    def delete(self, request):
        if 'user_id' not in request.query_params:
            user = getUserById(request.user.id)
        else:
            if int(request.query_params.get('user_id')) != request.user.id:
                content = {'statusCode': system_returns_code.UNANTTHORIZED,
                           'exceptionString': ['Unathorized.'],
                           'data': {}}
                return JsonResponse(content, status=system_returns_code.UNANTTHORIZED)

            user = getUserById(int(request.query_params.get('user_id')))

        if checkUserdelete(user):
            content = {'statusCode': system_returns_code.NOT_FOUND,
                       'exceptionString': ['Record not Found.'],
                       'data': {}}

            return JsonResponse(content, status=system_returns_code.NOT_FOUND)
        userDict = model_to_dict(user)
        userDict['deleted_by'] = request.user.id
        userDict['deleted_at'] = datetime.datetime.utcnow()
        user_serializer = DeleteUserSerializer(user, data=userDict)
        if user_serializer.is_valid():
            result = user_serializer.save()
            # Adding into the system changelog
            create_system_changelog(
                action_performed=SystemChangelog.ActionPerformed.DELETED,
                changed_in=SystemChangelog.TableName.USER,
                changed_reference_id=result.id,
                description='User has been deleted.',
                created_at=userDict['deleted_at'],
                created_by=userDict['deleted_by']
            )
            content = {'statusCode': system_returns_code.SUCCESSFUL,
                       'exceptionString': [],
                       'data': {"user": 'User is deleted.'}}

            return JsonResponse(content, status=system_returns_code.SUCCESSFUL)
        else:

            content = {'statusCode': system_returns_code.BAD_REQUEST,
                       'exceptionString': ['Bad Request.'],
                       'data': {}}

            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

    def put(self, request):
        try:
            params = json.loads(request.body)
        except:
            return JsonResponse(
                {'statusCode': system_returns_code.BAD_REQUEST,
                 'exceptionString': ['JSON body not found.'],
                 'data': {}},
                status=system_returns_code.BAD_REQUEST)
        if 'user_id' not in request.query_params:
            user = getUserById(request.user.id)
        else:
            if int(request.query_params.get('user_id')) != request.user.id:
                content = {'statusCode': system_returns_code.UNANTTHORIZED,
                           'exceptionString': ['Unathorized.'],
                           'data': {}}
                return JsonResponse(content, status=system_returns_code.UNANTTHORIZED)

            user = getUserById(int(request.query_params.get('user_id')))

        if checkUserdelete(user):
            content = {'statusCode': system_returns_code.NOT_FOUND,
                       'exceptionString': ['Record not Found.'],
                       'data': {}}

            return JsonResponse(content, status=system_returns_code.NOT_FOUND)
        params['updated_at'] = datetime.datetime.utcnow()
        params['updated_by'] = request.user.id
        try:
            if 'status' in params:
                params['status'] = params.get('status')

        except:
            content = {'statusCode': system_returns_code.BAD_REQUEST,
                       'exceptionString': ['Please input correct status option.'],
                       'data': {}}
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)
        try:
            if 'gender' in params:
                params['gender'] = params.get('gender')
        except:
            content = {'statusCode': system_returns_code.BAD_REQUEST,
                       'exceptionString': ['Please input correct gender option.'],
                       'data': {}}
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)
        try:
            if 'type' in params:
                params['type'] = params.get('type')
        except:
            content = {'statusCode': system_returns_code.BAD_REQUEST,
                       'exceptionString': ['Please input correct user type option.'],
                       'data': {}}
            return JsonResponse(content, status=system_returns_code.NOT_FOUND)
        user_serializer = UpdateUserSerializer(user, data=params, partial=True)
        if user_serializer.is_valid():
            result = user_serializer.save()
            # Adding into the system changelog
            create_system_changelog(
                action_performed=SystemChangelog.ActionPerformed.DELETED,
                changed_in=SystemChangelog.TableName.USER,
                changed_reference_id=result.id,
                description='User has been updated.',
                created_at=params['updated_at'],
                created_by=params['updated_by']
            )
            data = user_serializer.data
            data['status'] = convertEnumtoStatus(data.get('status'))
            data['gender'] = convertEnumToGender(data.get('gender'))
            data['type'] = convertEnumToGender(data.get('type'))

            content = {'statusCode': system_returns_code.SUCCESSFUL,
                       'exceptionString': [],
                       'data': data}
            return JsonResponse(content, status=system_returns_code.SUCCESSFUL)

        else:
            content = serializerErrorFormatter(user_serializer)
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)