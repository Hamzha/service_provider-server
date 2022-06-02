from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import datetime
from rest_framework.response import Response
import system_returns_code
from rest_framework import status
from authorization.core.utility.beautify_serializer_errors import beautify_serializer_errors
from authorization.serializer.configuration.create_configuration_serializer import CreateConfigurationSerializer
from authorization.serializer.configuration.get_configuration_serializer import GetConfigurationSerializer
from authorization.serializer.configuration.update_configuration_serializer import UpdateConfigurationSerializer
from authorization.core.system_changelog.write import create_system_changelog
from authorization.models.system_changelog import SystemChangelog
from authorization.core.configuration.read import get_all_configuration, get_configuration
from authorization.core.configuration.write import delete_configuration


class ConfigurationView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        user = request.user
        data['created_by'] = user.id
        data['created_at'] = datetime.datetime.utcnow()
        serialized_data = CreateConfigurationSerializer(data=data)
        if serialized_data.is_valid():
            result = serialized_data.save()
            # Adding into the system changelog
            create_system_changelog(
                action_performed=SystemChangelog.ActionPerformed.CREATED,
                changed_in=SystemChangelog.TableName.CONFIGURATION,
                changed_reference_id=result.id,
                description='Configuration has been created.',
                created_at=data['created_at'],
                created_by=data['created_by']
            )
            return Response({'statusCode': system_returns_code.CREATED,
                             'data': serialized_data.data, 'exceptionString': []},
                            status=status.HTTP_201_CREATED)
        else:
            serializer_error = beautify_serializer_errors(
                serialized_data.errors)
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': serializer_error, 'data': []},
                status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        parameters = request.GET.dict()
        hasConfigurationId = True if 'configuration_id' in parameters else False
        if hasConfigurationId:
            configuration = get_configuration(parameters['configuration_id'])
        else:
            configuration = get_all_configuration()

        if (configuration and hasConfigurationId) or (not hasConfigurationId):
            serialized_data = GetConfigurationSerializer(
                configuration, many=not hasConfigurationId)
            return Response({'statusCode': system_returns_code.SUCCESSFUL,
                             'data': serialized_data.data,
                             'exceptionString': []},
                            status=status.HTTP_200_OK)
        else:
            return Response(
                data={
                    'statusCode': system_returns_code.NOT_FOUND,
                    'exceptionString': ['This configuration does not exist'],
                    'data': []},
                status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        user = request.user
        parameters = request.query_params
        if 'configuration_id' in parameters:
            configuration_id = parameters['configuration_id']
        else:
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': ['please provide configuration_id'],
                    'data': {}},
                status=status.HTTP_400_BAD_REQUEST)
        deleted_at = datetime.datetime.utcnow()
        result = delete_configuration(configuration_id, user.id)
        if result:
            # Adding into the system changelog
            create_system_changelog(
                action_performed=SystemChangelog.ActionPerformed.DELETED,
                changed_in=SystemChangelog.TableName.CONFIGURATION,
                changed_reference_id=configuration_id,
                description='Configuration has been deleted.',
                created_at=deleted_at,
                created_by=user.id
            )
            return Response(
                data={
                    'statusCode': system_returns_code.SUCCESSFUL,
                    'data': {
                        'configuration': 'Configuration has been deleted'},
                    'exceptionString': []},
                status=status.HTTP_200_OK)
        else:
            return Response(
                data={
                    'statusCode': system_returns_code.NOT_FOUND,
                    'exceptionString': ['This Configuration does not exist'],
                    'data': {}},
                status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        data = request.data
        user = request.user
        data['updated_by'] = user.id
        data['updated_at'] = datetime.datetime.utcnow()
        if 'configuration_id' not in data:
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': ['please provide configuration_id'],
                    'data': []},
                status=status.HTTP_400_BAD_REQUEST)
        configuration = get_configuration(data['configuration_id'])
        if configuration:
            serialized_data = UpdateConfigurationSerializer(
                configuration, data=data)
            if serialized_data.is_valid():
                result = serialized_data.save()
                # Adding into the system changelog
                create_system_changelog(
                    action_performed=SystemChangelog.ActionPerformed.UPDATED,
                    changed_in=SystemChangelog.TableName.CONFIGURATION,
                    changed_reference_id=result.id,
                    description='Configuration has been updated.',
                    created_at=data['updated_at'],
                    created_by=data['updated_by']
                )
                return Response(
                    {
                        'statusCode': system_returns_code.SUCCESSFUL,
                        'data': serialized_data.data,
                        'exceptionString': []},
                    status=status.HTTP_200_OK)
            else:
                serializer_error = beautify_serializer_errors(
                    serialized_data.errors)
                return Response(
                    data={
                        'statusCode': system_returns_code.BAD_REQUEST,
                        'exceptionString': serializer_error, 'data': []},
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                data={
                    'statusCode': system_returns_code.NOT_FOUND,
                    'exceptionString': ['This configuration does not exist'],
                    'data': []},
                status=status.HTTP_404_NOT_FOUND)
