from functools import partial
import sys
from rest_framework import status
import datetime
import json
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from django.forms.models import model_to_dict
from authorization.core.utility.serializer_error_formatter import serializerErrorFormatter
from authorization.core.user_device.read import getUserDeviceByID
from authorization.core.user_device.read import getUserDeviceByUser
from authorization.models.user_device import UserDevice
import system_returns_code
from authorization.serializer.user_device import UserdeviceSerializer
from authorization.models.system_changelog import SystemChangelog
from authorization.core.system_changelog.write import create_system_changelog
from authorization.core.user_device.read import getUserDeviceByIdentifier

class UserDecideView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            params = json.loads(request.body)
        except:
            return JsonResponse(
                {'statusCode': system_returns_code.BAD_REQUEST,
                 'exceptionString': ['Missing Parameters.'],
                 'data': {}},
                status=system_returns_code.BAD_REQUEST)
        params['created_by'] = request.user.id
        params['created_at'] = datetime.datetime.utcnow()
        if 'user_id' in params:
            params['user'] = params.get('user_id')
        else:
            params['user'] = request.user.id

        if params.get('user') != request.user.id:
            return JsonResponse(
                {'statusCode': system_returns_code.UNANTTHORIZED,
                 'exceptionString': ['Unathorized.'],
                 'data': {}},
                status=system_returns_code.UNANTTHORIZED)
        if 'identifier' not in params:
            return JsonResponse(
                {'statusCode': system_returns_code.BAD_REQUEST,
                 'exceptionString': ['Please provide identifier'],
                 'data': {}},
                status=system_returns_code.BAD_REQUEST)
        device=getUserDeviceByIdentifier(params.get('identifier'),request.user)

        if(len(device)!=0):
            device[0].updated_at=params['created_at']
            device[0].updated_by=params['created_by']
            device[0].save()
            serializer_data=UserdeviceSerializer(device[0])
            data=serializer_data.data
            content = {'data': data, 'exceptionString': [], 'statusCode': system_returns_code.CREATED}
            return JsonResponse(content, status=system_returns_code.CREATED)
            
        params['created_at'] = datetime.datetime.utcnow()
        params['created_by'] = request.user.id
        user_device_serializer = UserdeviceSerializer(data=params)
        if user_device_serializer.is_valid():
            result=user_device_serializer.save()
            data = user_device_serializer.data
            if "user" in data:
                del data['user']
            create_system_changelog(
                action_performed=SystemChangelog.ActionPerformed.CREATED,
                changed_in=SystemChangelog.TableName.USER_DEVICE,
                changed_reference_id=result.id,
                description='User device is added.',
                created_at=params['created_at'],
                created_by=params['created_by']
            )
            content = {'data': data, 'exceptionString': [], 'statusCode': system_returns_code.CREATED
                       }
            return JsonResponse(content, status=system_returns_code.CREATED)

        else:
            content = serializerErrorFormatter(user_device_serializer)
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

    def delete(self, request):

        params = request.query_params.dict()

        if 'user_device_id' not in params:
            return JsonResponse(
                {'statusCode': system_returns_code.BAD_REQUEST,
                 'exceptionString': ['Please provide User Device ID.'],
                 'data': {}},
                status=system_returns_code.BAD_REQUEST)
        obj = getUserDeviceByID(params.get('user_device_id'))
        if obj is None:
            return JsonResponse(
                {'statusCode': system_returns_code.NOT_FOUND,
                 'exceptionString': ['Record not found.'],
                 'data': {}},
                status=system_returns_code.NOT_FOUND)

        if request.user.id != obj.user.id:
            return JsonResponse(
                {'statusCode': system_returns_code.UNANTTHORIZED,
                 'exceptionString': ['Unathorized.'],
                 'data': {}},
                status=system_returns_code.UNANTTHORIZED)

        params['deleted_at'] = datetime.datetime.utcnow()
        params['deleted_by'] = request.user.id
        params['user'] = obj.user.id

        user_device_serializer = UserdeviceSerializer(
            obj, data=params, partial=True)

        if user_device_serializer.is_valid():
            result=user_device_serializer.save()
            # Adding into the system changelog
            create_system_changelog(
                action_performed=SystemChangelog.ActionPerformed.DELETED,
                changed_in=SystemChangelog.TableName.USER_DEVICE,
                changed_reference_id=obj.id,
                description='User device deleted.',
                created_at=params['deleted_at'],
                created_by=params['deleted_by']
            )
            content = {'data': {"user_device":"Deleted."},
                       'exceptionString': [],
                       'statusCode': system_returns_code.SUCCESSFUL
                       }
            return JsonResponse(content, status=system_returns_code.SUCCESSFUL)

        else:
            content = serializerErrorFormatter(user_device_serializer)
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

    def put(self, request):
        try:
            params = json.loads(request.body)
        except:
            return JsonResponse(
                {'statusCode': system_returns_code.BAD_REQUEST,
                 'exceptionString': ['Missing Parameters.'],
                 'data': {}},
                status=system_returns_code.BAD_REQUEST)
        if 'user_id' in params:
            params['user'] = params.get('user_id')
        else:
            params['user'] = request.user.id

        if params.get('user') != request.user.id:
            return JsonResponse(
                {'statusCode': system_returns_code.UNANTTHORIZED,
                 'exceptionString': ['Unathorized.'],
                 'data': {}},
                status=system_returns_code.UNANTTHORIZED)

        query_params = request.query_params.dict()

        if 'user_device_id' not in query_params:
            return JsonResponse(
                {'statusCode': system_returns_code.BAD_REQUEST,
                 'exceptionString': ['Please provide User Device ID.'],
                 'data': {}},
                status=system_returns_code.BAD_REQUEST)
        obj = getUserDeviceByID(query_params.get('user_device_id'))
        if obj is None:
            return JsonResponse(
                {'statusCode': system_returns_code.NOT_FOUND,
                 'exceptionString': ['Record not found.'],
                 'data': {}},
                status=system_returns_code.NOT_FOUND)

        if request.user.id != obj.user.id:
            return JsonResponse(
                {'statusCode': system_returns_code.UNANTTHORIZED,
                 'exceptionString': ['Unathorized.'],
                 'data': {}},
                status=system_returns_code.UNANTTHORIZED)

        params['updated_at'] = datetime.datetime.utcnow()
        params['updated_by'] = request.user.id

        user_device_serializer = UserdeviceSerializer(
            obj, data=params, partial=True)

        if user_device_serializer.is_valid():
            user_device_serializer.save()
            data = user_device_serializer.data
            # Adding into the system changelog
            create_system_changelog(
                action_performed=SystemChangelog.ActionPerformed.DELETED,
                changed_in=SystemChangelog.TableName.USER_DEVICE,
                changed_reference_id=obj.id,
                description='User device updated',
                created_at= params['updated_at'],
                created_by=params['updated_by']
            )
            content = {'data': data,
                       'exceptionString': [],
                       'statusCode': system_returns_code.SUCCESSFUL
                       }
            return JsonResponse(content, status=system_returns_code.SUCCESSFUL)

        else:
            content = serializerErrorFormatter(user_device_serializer)
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

    def get(self, request):
        query_params = request.query_params.dict()
        if 'user_device_id' in query_params:
            obj = getUserDeviceByID(query_params.get('user_device_id'))
            if obj.user.id != request.user.id:
                return JsonResponse(
                    {'statusCode': system_returns_code.UNANTTHORIZED,
                    'exceptionString': ['Record not found.'],
                    'data': {}},
                    status=system_returns_code.UNANTTHORIZED)
            if obj is None:
                return JsonResponse(
                    {'statusCode': system_returns_code.NOT_FOUND,
                    'exceptionString': ['Record not found.'],
                    'data': {}},
                    status=system_returns_code.NOT_FOUND)
            user_device_serializer = UserdeviceSerializer(obj)
            data = user_device_serializer.data
            content = {'data': data, 'exceptionString': [],
                    'statusCode': system_returns_code.SUCCESSFUL}
            return JsonResponse(content, status=system_returns_code.SUCCESSFUL)
        else:
            obj = getUserDeviceByUser(request.user.id)
            if obj is None:
                return JsonResponse(
                    {'statusCode': system_returns_code.NOT_FOUND,
                    'exceptionString': ['Record not found.'],
                    'data': {}},
                    status=system_returns_code.NOT_FOUND)
            user_device_serializer = UserdeviceSerializer(obj, many=True)
            data = user_device_serializer.data
            content = {'data': data, 'exceptionString': [],
                    'statusCode': system_returns_code.SUCCESSFUL}
            return JsonResponse(content, status=system_returns_code.SUCCESSFUL)
      