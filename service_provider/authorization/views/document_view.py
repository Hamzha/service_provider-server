from asyncio import DatagramTransport
from dataclasses import dataclass
import datetime
import os
from pydoc import doc

from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from django.core.files.storage import FileSystemStorage

from leads.core.service.read import getServiceByID
from authorization.serializer.document import DocumentServiceSerializer
from authorization.core.system_changelog.write import create_system_changelog
from authorization.models.system_changelog import SystemChangelog
from authorization.core.document.read import getDocumentTypeToEnum
from authorization.core.utility.serializer_error_formatter import serializerErrorFormatter
from authorization.core.document.read import getDocumentFormatToEnum
from authorization.core.document.read import getDocuentFormatFromEnum
from authorization.core.document.read import getDocuentTypeFromEnum
from authorization.core.document.read import getDocumentByService
from authorization.core.document.read import getDocumentByID
from authorization.serializer.document import UpdateDocumentServiceSerializer
from authorization.core.document.read import getDocumentByUser
from service_provider.config import ConfigUrl
import system_returns_code
from django.forms.models import model_to_dict


class DocumentView(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request):

        if 'document' not in request.FILES:
            content = {'exceptionString': [
                'Please provice the Document.'],
                'data': {},
                'statusCode': system_returns_code.BAD_REQUEST}
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)
        else:
            document = request.FILES.get("document", None)

            params = request.POST.dict()

            if 'service_id' in params:
                params['service_id'] = int(params['service_id'])
                service = getServiceByID(params.get('service_id'))
                if service:
                    if service.user.id != request.user.id:
                        content = {'exceptionString': [
                            'Unathorized.'],
                            'data': {},
                            'statusCode': system_returns_code.UNANTTHORIZED}
                        return JsonResponse(content, status=system_returns_code.UNANTTHORIZED)
                    params['service'] = service.id
                else:

                    content = {'exceptionString': [
                        'Please provice a valid Service Id.'],
                        'data': {},
                        'statusCode': system_returns_code.BAD_REQUEST}
                    return JsonResponse(content, status=system_returns_code.BAD_REQUEST)
            if 'type' not in params:
                content = {'exceptionString': [
                    'Please provice a valid type.'],
                    'data': {},
                    'statusCode': system_returns_code.BAD_REQUEST}
                return JsonResponse(content, status=system_returns_code.BAD_REQUEST)
            else:
                params['type'] = getDocumentTypeToEnum(params.get('type'))

            if params.get('user_id') != None:
                params['user'] = int(params.get('user_id'))
            else:
                params['user'] = request.user.id
            if params.get('user') != request.user.id:
                content = {'exceptionString': [
                    'Unathorized'],
                    'data': {},
                    'statusCode': system_returns_code.UNANTTHORIZED}
                return JsonResponse(content, status=system_returns_code.UNANTTHORIZED)

            params['url'] = document.name
            params['created_at'] = datetime.datetime.utcnow()
            params['created_by'] = request.user.id
            params['format'] = getDocumentFormatToEnum(
                document.name.split('.')[-1])

            path = str(request.user.id)+"/"+str(
                getDocuentTypeFromEnum(params.get('type')))+"/"+getDocuentFormatFromEnum(params.get('format'))
            absolute = 'service_provider/media/'
            print('->'+absolute+path)
            if os.path.exists(absolute + path):
                list = os.listdir(absolute + path)
                if 'lead' in params:
                    path = path + '/' + \
                        str(params.get('lead'))+'.' + \
                        str(getDocuentFormatFromEnum(
                            params.get('format'))).lower()
                if 'service' in params:
                    path = path + '/' + \
                        str(params.get('service'))+'.' + \
                        str(getDocuentFormatFromEnum(
                            params.get('format'))).lower()
                print(path)
            else:
                if 'lead' in params:
                    path = path + '/' + \
                        str(params.get('lead'))+'.' + \
                        str(getDocuentFormatFromEnum(params.get('format'))).lower()  
                if 'service' in params:
                    path = path + '/' + \
                        str(params.get('service'))+'.' + \
                        str(getDocuentFormatFromEnum(params.get('format'))).lower()
                # os.makedirs(absolute + path)
                print(path)
                # path = path + '/' + \
                #     str(0) + '.' + \
                #     str(getDocuentFormatFromEnum(params.get('format'))).lower()
            fs = FileSystemStorage()

            tmp = fs.save(path, document)
            params['url'] = tmp
      
            document_service_serializer = DocumentServiceSerializer(
                data=params)
            if document_service_serializer.is_valid():
               
                result=document_service_serializer.save()
                data = document_service_serializer.data

                data['format'] = getDocuentFormatFromEnum(data['format'])
                data['type'] = getDocuentTypeFromEnum(data['type'])
                del data['user']
                del data['service']
                del data['url']

                # Adding into system changelog
                create_system_changelog(
                    action_performed=SystemChangelog.ActionPerformed.CREATED,
                    changed_in=SystemChangelog.TableName.DOCUMENT,
                    changed_reference_id=result.id,
                    description='Document is added.',
                    created_at=params['created_at'],
                    created_by=params['created_by']
                )

                content = {'exceptionString': [
                ],
                    'data': data,
                    'statusCode': system_returns_code.CREATED}
                return JsonResponse(content, status=system_returns_code.CREATED)
            else:
                content = serializerErrorFormatter(document_service_serializer)
                return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

    def get(self, request):
        params = request.query_params.dict()
        # Type conversion from id to string
        if 'service_id' in params:
            params['service_id'] = int(params['service_id'])
        if 'document_id' in params:
            params['document_id']= int(params['document_id'])
            
        if 'service_id' not in params and 'document_id' not in params:
            document = list(getDocumentByUser(request.user.id))
        elif 'service_id' in params:
            service = getServiceByID(params['service_id'])
            if not service:
                content = {'exceptionString': [
                    'Service Record not found.'],
                    'data': {},
                    'statusCode': system_returns_code.NOT_FOUND}
                return JsonResponse(content, status=system_returns_code.NOT_FOUND)
            document = list(getDocumentByService(service=service))
        elif 'document_id' in params:
            document = getDocumentByID(params['document_id'])

        if not document:
            content = {'exceptionString': [
                'Document Record not found.'],
                'data': {},
                'statusCode': system_returns_code.NOT_FOUND}
            return JsonResponse(content, status=system_returns_code.NOT_FOUND)

        document_service_serializer = DocumentServiceSerializer(
            document, many=True)
        data = document_service_serializer.data
        for index, value in enumerate(data):
            data[index]['format'] = getDocuentFormatFromEnum(
                data[index]['format'])
            data[index]['type'] = getDocuentTypeFromEnum(data[index]['type'])

            del data[index]['user']
            del data[index]['service']
            del data[index]['url']
        content = {
            'exceptionString': [],
            'data': data,
            'statusCode': system_returns_code.SUCCESSFUL
        }
        return JsonResponse(content, status=system_returns_code.SUCCESSFUL)

    def put(self, request):
        params = request.POST.dict()
        # Type conversion from id to string
        if 'service_id' in params:
            params['service_id'] = int(params['service_id'])
        if 'document_id' in params:
            params['document_id']= int(params['document_id'])

        document = None
        if 'document_id' not in request.query_params.dict():
            content = {'exceptionString': [
                'Please provice Document ID.'],
                'data': {},
                'statusCode': system_returns_code.BAD_REQUEST}
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)
        if 'document' in request.FILES:
            document = request.FILES.get("document", None)
            params['format'] = getDocumentFormatToEnum(
                document.name.split('.')[-1])
        if 'service_id' in params:
            service = getServiceByID(params.get('service_id'))
            if service:
                if service.user.id != request.user.id:
                    content = {'exceptionString': [
                        'Unathorized.'],
                        'data': {},
                        'statusCode': system_returns_code.UNANTTHORIZED}
                    return JsonResponse(content, status=system_returns_code.UNANTTHORIZED)

                params['service'] = service.id
            else:
                content = {'exceptionString': [
                    'Service Id not found.'],
                    'data': {},
                    'statusCode': system_returns_code.NOT_FOUND}
                return JsonResponse(content, status=system_returns_code.NOT_FOUND)

        if 'type' in params:
            params['type'] = getDocumentTypeToEnum(params.get('type'))

        if params.get('user_id') != None:
            params['user'] = int(params.get('user_id'))

        if params.get('user') == None:
            params['user'] = request.user.id
        if params.get('user') != request.user.id:
            content = {'exceptionString': [
                'Unathorized'],
                'data': {},
                'statusCode': system_returns_code.UNANTTHORIZED}
            return JsonResponse(content, status=system_returns_code.UNANTTHORIZED)

        params['updated_at'] = datetime.datetime.utcnow()
        params['updated_by'] = request.user.id

        if document:
            params['url'] = document.name

            path = str(request.user.id)+"/"+str(
                getDocuentTypeFromEnum(params.get('type')))+"/"+getDocuentFormatFromEnum(params.get('format'))
            absolute = 'service_provider/media/'

            if os.path.exists(absolute + path):
                list = os.listdir(absolute + path)
                path = path + '/' + \
                    str(len(list))+'.' + \
                    str(getDocuentFormatFromEnum(params.get('format'))).lower()
            else:
                os.makedirs(absolute + path)
                path = path + '/' + \
                    str(0) + '.' + \
                    str(getDocuentFormatFromEnum(params.get('format'))).lower()
            params['url'] = path
        document_obj = getDocumentByID(
            request.query_params.dict()['document_id'])

        if not document_obj:
            content = {'exceptionString': [
                'Document not found.'],
                'data': {},
                'statusCode': system_returns_code.NOT_FOUND}
            return JsonResponse(content, status=system_returns_code.NOT_FOUND)

        if 'url' not in params:
            params['url'] = model_to_dict(document_obj[0])['url']
        document_service_serializer = UpdateDocumentServiceSerializer(
            document_obj[0], data=params)
        if document_service_serializer.is_valid():
            if document:
                fs = FileSystemStorage()

                fs.save(path, document)
                result = document_service_serializer.save()
            else:
                result = document_service_serializer.save()
            data = document_service_serializer.data
            data['url'] = ConfigUrl.BASE_URL + 'media/'+data['url']

            data['format'] = getDocuentFormatFromEnum(data['format'])
            data['type'] = getDocuentTypeFromEnum(data['type'])
            del data['user']
            del data['service']

            # Adding into system changelog
            create_system_changelog(
                action_performed=SystemChangelog.ActionPerformed.UPDATED,
                changed_in=SystemChangelog.TableName.DOCUMENT,
                changed_reference_id=result.id,
                description='Document is updated.',
                created_at=params['updated_at'],
                created_by=params['updated_by']
            )
                
            content = {'exceptionString': [
            ],
                'data': data,
                'statusCode': system_returns_code.CREATED}
            return JsonResponse(content, status=system_returns_code.CREATED)
        else:
            content = serializerErrorFormatter(document_service_serializer)
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

    def delete(self, request):
        params = request.query_params.dict()
        # Type conversion from id to string
        if 'service_id' in params:
            params['service_id'] = int(params['service_id'])
        if 'document_id' in params:
            params['document_id']= int(params['document_id'])

        if 'document_id' not in params:
            content = {'exceptionString': [
                'Please provide the Document ID.'],
                'data': {},
                'statusCode': system_returns_code.BAD_REQUEST}
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)
        document = getDocumentByID(params.get('document_id'))
        if not document:
            content = {'exceptionString': [
                'Document record not found.'],
                'data': {},
                'statusCode': system_returns_code.NOT_FOUND}
            return JsonResponse(content, status=system_returns_code.NOT_FOUND)
        document = document[0]
        if request.user.id != document.user.id:
            content = {'exceptionString': [
                'Unathorized'],
                'data': {},
                'statusCode': system_returns_code.UNANTTHORIZED}
            return JsonResponse(content, status=system_returns_code.UNANTTHORIZED)
        params['deleted_by'] = request.user.id
        params['deleted_at'] = datetime.datetime.utcnow()
        params['user'] = request.user.id

        update_document_service_serializer = UpdateDocumentServiceSerializer(
            document, data=params, partial=True)
        if update_document_service_serializer.is_valid():
            result = update_document_service_serializer.save()
            data = update_document_service_serializer.data

            # Adding into system changelog
            create_system_changelog(
                action_performed=SystemChangelog.ActionPerformed.UPDATED,
                changed_in=SystemChangelog.TableName.DOCUMENT,
                changed_reference_id=result.id,
                description='Document is deleted.',
                created_at=params['deleted_at'],
                created_by=params['deleted_by']
            )

            content = {'exceptionString': [],
                       'data': {"document":"Document is deleted"},
                       'statusCode': system_returns_code.SUCCESSFUL}
            return JsonResponse(content, status=system_returns_code.SUCCESSFUL)
        else:
            content = serializerErrorFormatter(
                update_document_service_serializer)
            return JsonResponse(content, status=system_returns_code.SUCCESSFUL)