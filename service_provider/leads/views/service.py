from os import stat
from re import S
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from leads.serielizer.service import ServiceSerlizer, UpdateServceSerializer
from leads.core.service.read import getServiceCategoryByName, serviceExistOrNot, serviceAlreadyDeletedOrNot, getServiceByID
from leads.core.service.read import getServiceStatefromEnum, getEnumFromServieStatus, getServiceCategoryfromID,isServiceAlreadyRegister
from leads.core.service.write import delete_service
import datetime
from leads.core.service.write import update_service
from django.forms.models import model_to_dict
import json
from leads.core.service.read import getAllServices
from leads.serielizer.service import GetServiceSerializer
from leads.core.service.read import getServiceCategoryById
from authorization.core.utility.serializer_error_formatter import serializerErrorFormatter
import system_returns_code
from authorization.models.system_changelog import SystemChangelog
from authorization.core.system_changelog.write import create_system_changelog
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Service(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        logger.debug("testteest")
        try:
            params = json.loads(request.body)
        except:
            content = {'statusCode': system_returns_code.BAD_REQUEST,
                       'data': {}, 'exceptionString': ['Missing Parameters.']}
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)
        if 'service_category_id' not in params:
            content = {'statusCode': system_returns_code.BAD_REQUEST,
                       'data': {}, 'exceptionString': ['Please input valid Service Category of the service.']}
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

        params['service_category'] = getServiceCategoryById(
            params['service_category_id'])
        if params['service_category'] == 'NONE':
            content = {'statusCode': system_returns_code.BAD_REQUEST,
                       'data': {}, 'exceptionString': ['Please input valid Service Category of the service.']}
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)
        else:
            params['service_category'] = params['service_category']
        params['user'] = request.user.id
        params['created_at'] = datetime.datetime.utcnow()
        params['created_by'] = request.user.id
        params['state'] = getEnumFromServieStatus('APPROVED')
        service_serializer = ServiceSerlizer(data=params)
        if service_serializer.is_valid():
            previous_service=isServiceAlreadyRegister(params['service_category_id'],request.user)
            if previous_service:
                content = {'statusCode': system_returns_code.BAD_REQUEST,
                       'data': {}, 'exceptionString': ['This service is already registered.']}
                return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

            result=service_serializer.save()
            data = service_serializer.data

            # Adding system changelog
            create_system_changelog(
                action_performed=SystemChangelog.ActionPerformed.CREATED,
                changed_in=SystemChangelog.TableName.SERVICE,
                changed_reference_id=result.id,
                description='Service is created.',
                created_at=params['created_at'],
                created_by=params['created_by']
            )

            data['state'] = getServiceStatefromEnum(
                params['state'])
            data['service_category'] = getServiceCategoryfromID(
                params['service_category'])

            content = {'data': data,
                       'exceptionString': [],
                       'statusCode': system_returns_code.CREATED
                       }
            return JsonResponse(content, status=system_returns_code.CREATED)
        else:
            logger.debug(service_serializer.errors)
            content = serializerErrorFormatter(service_serializer)
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

    def delete(self, request):
        if 'service_id' not in request.query_params or request.query_params['service_id'] == '':
            content = {'statusCode': system_returns_code.BAD_REQUEST,
                       'exceptionString': ["Please input a valid Service ID"],
                       'data': {}}
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)
        service_id = request.query_params['service_id']
        if serviceExistOrNot(service_id):
            if serviceAlreadyDeletedOrNot(service_id):
                deleted_at=datetime.datetime.utcnow()  
                delete_service(service_id, request.user.id)
                # Adding system changelog
                create_system_changelog(
                    action_performed=SystemChangelog.ActionPerformed.DELETED,
                    changed_in=SystemChangelog.TableName.SERVICE,
                    changed_reference_id=service_id,
                    description='Service is deleted.',
                    created_at=deleted_at,
                    created_by= request.user.id
                )
                content = {'statusCode': system_returns_code.SUCCESSFUL,
                           'exceptionString': [],
                           'data': {"service":'Service is Deleted.'}}
                return JsonResponse(content, status=system_returns_code.SUCCESSFUL)
            else:
                content = {'statusCode': system_returns_code.NOT_FOUND,
                           'exceptionString': ["Service is already Deleted."],
                           'data': {}}
                return JsonResponse(content, status=system_returns_code.NOT_FOUND)

        else:
            content = {'statusCode': system_returns_code.NOT_FOUND,
                       'exceptionString': ["Please input a valid Service ID"],
                       'data': {}}
            return JsonResponse(content, status=system_returns_code.NOT_FOUND)

    def put(self, request):
        try:
            params = json.loads(request.body)
        except:
            content = {'statusCode': system_returns_code.BAD_REQUEST,
                       'data': {}, 'exceptionString': ['Missing Parameters.']}
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

        if 'service_id' not in request.query_params or request.query_params['service_id'] == '':
            content = {'statusCode': system_returns_code.BAD_REQUEST,
                       'exceptionString': ["Please input a valid Service ID"],
                       'data': {}}
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)
        service_id = request.query_params['service_id']

        if serviceExistOrNot(service_id):
            if not 'state' in params:
                content = {'statusCode': system_returns_code.BAD_REQUEST,
                           'data': {}, 'exceptionString': ['Please input valid state of the service.']}
                return JsonResponse(content, status=system_returns_code.BAD_REQUEST)
            params['state'] = getEnumFromServieStatus(params['state'])
            if params['state'] == 'NONE':
                content = {'statusCode': system_returns_code.BAD_REQUEST,
                           'data': {}, 'exceptionString': ['Please input valid state of the service.']}
                return JsonResponse(content, status=system_returns_code.BAD_REQUEST)
            if 'service_category_id' not in params:
                content = {'statusCode': system_returns_code.BAD_REQUEST,
                           'data': {}, 'exceptionString': ['Please input valid Service Category of the service.']}
                return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

            params['service_category'] = getServiceCategoryById(
                params['service_category_id'])

            if params['service_category'] == 'NONE':
                content = {'statusCode': system_returns_code.BAD_REQUEST,
                           'data': {}, 'exceptionString': ['Please input valid Service Category of the service.']}
                return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

            params['user'] = request.user.id
            params['updated_by'] = request.user.id
            params['updated_at'] = datetime.datetime.utcnow()
            params['deleted_by'] = None
            params['deleted_at'] = None
            service = getServiceByID(service_id)
            if service.user.id != request.user.id:
                content = {'statusCode': system_returns_code.UNANTTHORIZED,
                           'data': {}, 'exceptionString': ['Unathorized.']}
                return JsonResponse(content, status=system_returns_code.UNANTTHORIZED)
            service_serializer = UpdateServceSerializer(service, data=params)
            if service_serializer.is_valid():

                service_serializer.save()
                data = service_serializer.data
                data['state'] = getServiceStatefromEnum(data['state'])

                # Adding system changelog
                create_system_changelog(
                    action_performed=SystemChangelog.ActionPerformed.UPDATED,
                    changed_in=SystemChangelog.TableName.SERVICE,
                    changed_reference_id=service_id,
                    description='Service is updated.',
                    created_at= params['updated_at'],
                    created_by= params['updated_by']
                )

                content = {'statusCode': system_returns_code.SUCCESSFUL,
                           'exceptionString': [],
                           'data': data}
                return JsonResponse(content, status=system_returns_code.SUCCESSFUL)
            else:
                error = []
                for key, value in service_serializer.errors.items():
                    error.append(key + " : "+value[0])
                content = {'statusCode': system_returns_code.BAD_REQUEST,
                           'exceptionString': error,
                           'data': {}}
                return JsonResponse(content, status=system_returns_code.BAD_REQUEST)
        else:
            content = {'statusCode': system_returns_code.NOT_FOUND,
                       'exceptionString': ["Service does not exists"],
                       'data': {}}
            return JsonResponse(content, status=system_returns_code.NOT_FOUND)

    def get(self, request):

        if 'user_id' not in request.query_params and 'service_id' not in request.query_params:
            services = getAllServices(request.user)
            tmp = GetServiceSerializer(services, many=True)
            content = {'statusCode': system_returns_code.SUCCESSFUL,
                       'exceptionString': [],
                       'data': tmp.data}
            return JsonResponse(content, status=system_returns_code.SUCCESSFUL)

        if 'user_id' in request.query_params and request.query_params.get('user_id') != '':
            if int(request.query_params.get('user_id')) != request.user.id:
                content = {'statusCode': system_returns_code.UNANTTHORIZED,
                           'exceptionString': ["Unathorized"],
                           'data': {}}
                return JsonResponse(content, status=system_returns_code.UNANTTHORIZED)

            else:
                services = getAllServices(request.user)
                tmp = GetServiceSerializer(services, many=True)
                content = {'statusCode': system_returns_code.SUCCESSFUL,
                           'exceptionString': [],
                           'data': tmp.data}
                return JsonResponse(content, status=system_returns_code.SUCCESSFUL)

        if 'service_id' not in request.query_params or request.query_params['service_id'] == '':
            content = {'statusCode': system_returns_code.BAD_REQUEST,
                       'exceptionString': ["Please input a valid Service ID"],
                       'data': {}}
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)
        service_id = request.query_params.get('service_id')
        if serviceExistOrNot(service_id):
            if serviceAlreadyDeletedOrNot(service_id) == False:
                content = {'statusCode': system_returns_code.NOT_FOUND,
                           'exceptionString': ["Service does not exists."],
                           'data': {}}
                return JsonResponse(content, status=system_returns_code.NOT_FOUND)
            else:
                service = getServiceByID(service_id)
                if service.user.id != request.user.id:
                    content = {'statusCode': system_returns_code.UNANTTHORIZED,
                               'exceptionString': ["Unathorized."],
                               'data': {}}
                    return JsonResponse(content, status=system_returns_code.UNANTTHORIZED)
                service_serializer = ServiceSerlizer(
                    data=model_to_dict(service))
                if service_serializer.is_valid():
                    data = service_serializer.data
                    data['state'] = getServiceStatefromEnum(data['state'])
                    data['service_category'] = getServiceCategoryfromID(
                        data['service_category'])

                    content = {'statusCode': system_returns_code.SUCCESSFUL,
                               'exceptionString': [],
                               'data': data}
                    return JsonResponse(content, status=system_returns_code.SUCCESSFUL)

                else:
                    content = serializerErrorFormatter(service_serializer)
                    return JsonResponse(content, status=system_returns_code.BAD_REQUEST)
        else:
            content = {'statusCode': system_returns_code.NOT_FOUND,
                       'exceptionString': ["Service does not exists"],
                       'data': {}}
            return JsonResponse(content, status=system_returns_code.NOT_FOUND)