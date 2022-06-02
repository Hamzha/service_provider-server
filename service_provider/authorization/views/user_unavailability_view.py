from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from authorization.serializer.user_unavailability.create_user_unavailability_serializer import CreateUserUnavailabilitySerializer
from authorization.serializer.user_unavailability.get_user_unavailability_serializer import GetUserUnavailabilitySerializer
from authorization.serializer.user_unavailability.update_user_unavailability_serializer import UpdateUserUnavailabilitySerializer
import datetime
from rest_framework.response import Response
import system_returns_code
from rest_framework import status
from authorization.core.utility.beautify_serializer_errors import \
    beautify_serializer_errors
from authorization.core.system_changelog.write import create_system_changelog
from authorization.models.system_changelog import SystemChangelog
from authorization.core.unavailability.read import getUserUnavailibilityByUser

class UserUnavailabilityView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        parameters = request.data
        user = request.user
        parameters['user'] = user.id
        parameters['created_by'] = user.id
        parameters['created_at'] = datetime.datetime.utcnow()

        serialized_data = CreateUserUnavailabilitySerializer(data=parameters)
        if serialized_data.is_valid():
            result=serialized_data.save()
            create_system_changelog(
                action_performed=SystemChangelog.ActionPerformed.CREATED,
                changed_in=SystemChangelog.TableName.UserUnavailability,
                changed_reference_id=result.id,
                description='UserUnavailability created',
                created_at=parameters['created_at'],
                created_by=parameters['created_by']
            )
            return Response(
                {'statusCode': system_returns_code.CREATED, 'data': [serialized_data.data],'exceptionString':[]}, status=status.HTTP_201_CREATED)
        else:
            serializer_error = beautify_serializer_errors(serialized_data.errors)
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': serializer_error,
                    'data':{}},
                status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        user = request.user
        user_unavailability=getUserUnavailibilityByUser(user.id)
        if user_unavailability:
            serialized_data=GetUserUnavailabilitySerializer(user_unavailability,many=True)

            return Response(
                {'statusCode': system_returns_code.SUCCESSFUL, 'data': serialized_data.data,'exceptionString':[]}, status=status.HTTP_200_OK)

        else:
            return Response(
                data={
                    'statusCode': system_returns_code.NOT_FOUND,
                    'exceptionString': ['UserUnavailability not found'],
                    'data':{}},
                status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        data=request.data
        user = request.user
        data['user']=user.id
        data['updated_by'] = user.id
        data['updated_at'] = datetime.datetime.utcnow()
        user_unavailability=getUserUnavailibilityByUser(user.id)
        if user_unavailability:
            serialized_data=UpdateUserUnavailabilitySerializer(user_unavailability[0],data=data)
            if serialized_data.is_valid():
                result=serialized_data.save()
                create_system_changelog(
                    action_performed=SystemChangelog.ActionPerformed.UPDATED,
                    changed_in=SystemChangelog.TableName.UserUnavailability,
                    changed_reference_id=result.id,
                    description='UserUnavailability updated',
                    created_at=data['updated_at'],
                    created_by=data['updated_by']
                )
                return Response(
                    {'statusCode': system_returns_code.SUCCESSFUL, 'data': serialized_data.data,'exceptionString':[]}, status=status.HTTP_200_OK)
            else:
                serializer_error = beautify_serializer_errors(serialized_data.errors)
                return Response(
                    data={
                        'statusCode': system_returns_code.BAD_REQUEST,
                        'exceptionString': serializer_error,
                        'data':[]},
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                data={
                    'statusCode': system_returns_code.NOT_FOUND,
                    'exceptionString': ['UserUnavailability not found'],
                    'data':{}},
                status=status.HTTP_404_NOT_FOUND)