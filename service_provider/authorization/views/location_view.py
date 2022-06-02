from functools import partial
from rest_framework import status
import datetime
import json
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from authorization.serializer.location import LocationSerializer, UpdateLocationSerializer
from django.forms.models import model_to_dict
from authorization.core.location.read import getLocationByUser
from authorization.core.location.write import deleteLocation,  deleteLocation
from authorization.core.user.read import getUserByEmail, checkEmailAvailability, checkUserdelete
from authorization.core.user.read import getUserById
from authorization.core.utility.serializer_error_formatter import serializerErrorFormatter
from authorization.core.location.read import checkLocationDelete
from authorization.models.system_changelog import SystemChangelog
from authorization.core.system_changelog.write import create_system_changelog
import system_returns_code
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class LocationView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            params = json.loads(request.body)
        except:
            return JsonResponse({'statusCode': system_returns_code.BAD_REQUEST, 'exceptionString': ['Missing parameters.'], 'data': {}}, status=system_returns_code.BAD_REQUEST)

        if 'user_id' not in params:
            user = getUserById(request.user.id)
        else:
            user = getUserById(params.get('user_id'))
        if not user:
            return JsonResponse({'statusCode': system_returns_code.NOT_FOUND, 'exceptionString': ['Please provice a valid user.'], 'data': {}}, status=system_returns_code.NOT_FOUND)

        if user.id != request.user.id:
            return JsonResponse({'statusCode': system_returns_code.UNANTTHORIZED, 'exceptionString': ['Unathorized.'], 'data': {}}, status=system_returns_code.UNANTTHORIZED)

        params['user'] = user.id
        location_serializer = LocationSerializer(data=params)

        location = getLocationByUser(
            getUserById(user.id))

        if location:
            params['updated_by'] = request.user.id
            params['updated_at'] = datetime.datetime.utcnow()
            params['deleted_by'] = None
            params['deleted_at'] = None
            location_serializer = LocationSerializer(
                location, data=params, partial=True)

            if location_serializer.is_valid():
                result = location_serializer.save()
                # Adding system changelog
                create_system_changelog(
                    action_performed=SystemChangelog.ActionPerformed.UPDATED,
                    changed_in=SystemChangelog.TableName.LOCATION,
                    changed_reference_id=result.id,
                    description='Location updated.',
                    created_at=params['updated_at'],
                    created_by=params['updated_by']
                )
                data = location_serializer.data
                logger.debug(data)
                return JsonResponse(
                    {'statusCode': system_returns_code.SUCCESSFUL,
                        'data': data,
                        'exceptionString': []},
                    status=system_returns_code.SUCCESSFUL)

            else:
                content = serializerErrorFormatter(location_serializer)
                return JsonResponse(content, status=system_returns_code.BAD_REQUEST)
        params['created_by'] = request.user.id
        params['created_at'] = datetime.datetime.utcnow()
        if location_serializer.is_valid():
            result=location_serializer.save()
            data = location_serializer.data

            # Adding system changelog
            create_system_changelog(
                action_performed=SystemChangelog.ActionPerformed.CREATED,
                changed_in=SystemChangelog.TableName.LOCATION,
                changed_reference_id=result.id,
                description='Location created.',
                created_at=params['created_at'],
                created_by=params['created_by']
            )

            return JsonResponse(
                {'statusCode': system_returns_code.CREATED,
                 'data': data,
                 'exceptionString': []},
                status=system_returns_code.CREATED)
        else:
            content = serializerErrorFormatter(location_serializer)
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

    def get(self, request):
        params = request.query_params.dict()
        if 'user_id' in params:
            user = getUserById(params.get('user_id'))
        else:
            user = getUserById(request.user.id)
        if not user:
            return JsonResponse(
                {'statusCode': system_returns_code.NOT_FOUND,
                 'exceptionString': ['Please provice a valid user.'],
                 'data': {}},
                status=system_returns_code.NOT_FOUND)

        if user.id != request.user.id:
            return JsonResponse(
                {'statusCode': system_returns_code.UNANTTHORIZED,
                 'exceptionString': ['Unathorized.'],
                 'data': {}},
                status=system_returns_code.UNANTTHORIZED)
        if checkUserdelete(user):
            return JsonResponse(
                {'statusCode': system_returns_code.NOT_FOUND,
                 'exceptionString': ['Please provice a valid user.'],
                 'data': {}},
                status=system_returns_code.NOT_FOUND)
        location = getLocationByUser(
            user)

        if not location:
            return JsonResponse(
                {'statusCode': system_returns_code.NOT_FOUND,
                 'exceptionString': ['Please provice a valid user.'],
                 'data': {}},
                status=system_returns_code.NOT_FOUND)

        if location.deleted_by:
            return JsonResponse(
                {'statusCode': system_returns_code.NOT_FOUND,
                 'exceptionString': ['Please provice a valid user.'],
                 'data': {}},
                status=system_returns_code.NOT_FOUND)
        location_serializer = LocationSerializer(data=model_to_dict(location))
        if location_serializer.is_valid():

            data = location_serializer.data

            return JsonResponse({'statusCode': system_returns_code.SUCCESSFUL,
                                 'exceptionString': [],
                                 'data': data},
                                status=system_returns_code.SUCCESSFUL)
        else:
            error = []
            for key, value in location_serializer.errors.items():
                error.append(key + " : "+value[0])
            content = {'statusCode': system_returns_code.BAD_REQUEST,
                       'exceptionString': error,
                       'data': {}}
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

    def delete(self, request):
        params = request.query_params.dict()
        if 'user_id' not in params:
            return JsonResponse(
                {'statusCode': system_returns_code.BAD_REQUEST,
                 'exceptionString': ['Please provice a valid user.'],
                 'data': {}},
                status=system_returns_code.BAD_REQUEST)
        user = getUserById(params.get('user_id'))
        if not user:
            return JsonResponse(
                {'statusCode': system_returns_code.NOT_FOUND,
                 'exceptionString': ['Please provice a valid user.'],
                 'data': {}},
                status=system_returns_code.NOT_FOUND)
        if user.id != request.user.id:
            return JsonResponse(
                {'statusCode': system_returns_code.UNANTTHORIZED,
                 'exceptionString': ['unathorized.'],
                 'data': {}},
                status=system_returns_code.UNANTTHORIZED)

        if checkUserdelete(user) == True:
            return JsonResponse(
                {'statusCode': system_returns_code.NOT_FOUND,
                 'exceptionString': ['Please provice a valid user.'],
                 'data': {}},
                status=system_returns_code.NOT_FOUND)
        location = getLocationByUser(user.id)

        if checkLocationDelete(location) == True:
            return JsonResponse(
                {'statusCode': system_returns_code.NOT_FOUND,
                 'exceptionString': ['Location already deleted.'],
                 'data': {}},
                status=system_returns_code.NOT_FOUND)

        data = model_to_dict(location)
        data['deleted_by'] = request.user.id
        data['deleted_at'] = datetime.datetime.utcnow()
        location_serializer = UpdateLocationSerializer(location, data=data)
        if location_serializer.is_valid():
            result =location_serializer.save()
            # Adding into changelog
            create_system_changelog(
                action_performed=SystemChangelog.ActionPerformed.DELETED,
                changed_in=SystemChangelog.TableName.LOCATION,
                changed_reference_id=result.id,
                description='Location deleted.',
                created_at=data['deleted_at'],
                created_by=data['deleted_by']
            )
            return JsonResponse(
                {'statusCode': system_returns_code.SUCCESSFUL,
                 'exceptionString': [],
                 'data': {"location":"Location is deleted."}},
                status=status.HTTP_200_OK)
        else:
            content = serializerErrorFormatter(location_serializer)
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

    # def put(self, request):
    #     try:
    #         params = json.loads(request.body)
    #     except:
    #         return JsonResponse({'responseCode': 400, 'response': "Please Provide paramters."})
    #     if 'location_user' not in params:
    #         return JsonResponse(
    #             {'statusCode': status.HTTP_400_BAD_REQUEST,
    #              'exceptionString': ['Please provice a valid user.'],
    #              'data': ''},
    #             status=status.HTTP_400_BAD_REQUEST)
    #     if checkEmailAvailability(params.get('location_user')) == False:
    #         return JsonResponse(
    #             {'statusCode': status.HTTP_400_BAD_REQUEST,
    #              'exceptionString': ['Please provice a valid user.'],
    #              'data': ''},
    #             status=status.HTTP_400_BAD_REQUEST)
    #     if checkUserdelete(getUserByEmail(params.get('location_user'))):
    #         return JsonResponse(
    #             {'statusCode': status.HTTP_400_BAD_REQUEST,
    #              'exceptionString': ['Please provice a valid user.'],
    #              'data': ''},
    #             status=status.HTTP_400_BAD_REQUEST)
    #     user = getUserByEmail(params.get('location_user'))
    #     updateLocation(user=user, updated_by=request.user.id,
    #                    lat=params.get('lat'), lng=params.get('lng'))
    #     return JsonResponse(
    #         {'statusCode': status.HTTP_200_OK,
    #          'exceptionString': '',
    #          'data': 'Location is Updated.'},
    #         status=status.HTTP_200_OK)
