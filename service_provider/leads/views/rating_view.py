import datetime
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from leads.core.rating.read import get_all_ratings_by_job_id
from leads.core.rating.read import get_all_ratings_by_user_id
from leads.core.job.read import get_job_by_job_id
from leads.core.rating.read import get_rating
from leads.core.rating.write import delete_rating
from leads.serielizer.rating.get_rating_serializer import GetRatingSerializer
from leads.serielizer.rating.create_rating_serializer import CreateRatingSerializer
from leads.core.utility.beautify_serializer_errors import beautify_serializer_errors
from rest_framework.response import Response
from rest_framework import status
import system_returns_code
from authorization.models.system_changelog import SystemChangelog
from authorization.core.system_changelog.write import create_system_changelog
from leads.core.rating.write import create_rating
from leads.serielizer.rating.update_rating_serializer import UpdateRatingSerializer
import collections
from authorization.models.user import User
from leads.core.rating.read import get_new_user_rating


class RatingView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        user = request.user
        data['created_by'] = user.id
        data['created_at'] = datetime.datetime.utcnow()
        if 'job_id' not in data:
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': ['Please provide job_id'],
                    'data': {}},
                status=status.HTTP_400_BAD_REQUEST)

        serialized_data = CreateRatingSerializer(data=data)
        if serialized_data.is_valid():
            # Verifying if job belongs to the user
            job = get_job_by_job_id(data['job_id'], user.id)
            
            if not job:
                return Response(
                    data={
                        'statusCode': system_returns_code.BAD_REQUEST,
                        'exceptionString': ['Please provide valid job_id'],
                        'data': {}},
                    status=status.HTTP_400_BAD_REQUEST)
            lead=job.lead_job
            
            # Verifying if the rating is given already
            ratings = get_all_ratings_by_job_id(data['job_id'])
            for rating in ratings:
                if rating.created_by == user.id:
                    return Response(
                        data={
                            'statusCode': system_returns_code.BAD_REQUEST,
                            'exceptionString': ['You have already provided rating for this job'],
                            'data': {}},
                        status=status.HTTP_400_BAD_REQUEST)

            # Creating the rating
            validated_data = serialized_data.validated_data
            validated_data = list(validated_data.items())
            validated_data.append(('job', job))
            validated_data.sort()
            validated_data = collections.OrderedDict(validated_data)
            if user.type==User.UserType.VENDOR:
                validated_data['user']=lead.client
                user_to_rate=lead.client
            else:
                validated_data['user']=lead.vendor
                user_to_rate=lead.vendor

            rating = create_rating(validated_data)
            create_system_changelog(
                action_performed=SystemChangelog.ActionPerformed.CREATED,
                changed_in=SystemChangelog.TableName.RATING,
                changed_reference_id=rating.id,
                description='Rating has been created',
                created_at=data['created_at'],
                created_by=data['created_by']
            )

            # Updating the user rating
            new_rating=get_new_user_rating(user_to_rate.rating,user_to_rate.no_of_reviews,rating)
            user_to_rate.rating=new_rating
            user_to_rate.no_of_reviews=user_to_rate.no_of_reviews + 1
            user_to_rate.save()

            serialized_data = GetRatingSerializer(rating)
            return Response({'statusCode': system_returns_code.CREATED,
                             'data': serialized_data.data,
                             'exceptionString': []},
                            status=status.HTTP_201_CREATED)
        else:
            serializer_error = beautify_serializer_errors(
                serialized_data.errors)
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': serializer_error,
                    'data': {}},
                status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        data = request.data
        user = request.user

        if 'job_id' in data:
            ratings = get_all_ratings_by_job_id(data['job_id'])
        else:
            ratings = get_all_ratings_by_user_id(user.id)

        serialized_data = GetRatingSerializer(ratings, many=True)
        return Response({'statusCode': system_returns_code.SUCCESSFUL,
                         'data': serialized_data.data,
                         'exceptionString': []}, status=status.HTTP_200_OK,)

    def put(self, request):
        data = request.data
        user = request.user
        data['updated_by'] = user.id
        data['updated_at'] = datetime.datetime.utcnow()
        if 'rating_id' not in data:
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': ['Please provide rating_id'],
                    'data': {}},
                status=status.HTTP_400_BAD_REQUEST)
                
        if 'response' in data:
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': ['You can not update your response'],
                    'data': {}},
                status=status.HTTP_400_BAD_REQUEST)

        rating = get_rating(data['rating_id'], user.id)        
        if not rating:
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': ['Rating not found'],
                    'data': {}},
                status=status.HTTP_400_BAD_REQUEST)

        serialized_data = UpdateRatingSerializer(rating, data=data)
        if serialized_data.is_valid():
            rating = serialized_data.save()
            create_system_changelog(
                action_performed=SystemChangelog.ActionPerformed.UPDATED,
                changed_in=SystemChangelog.TableName.RATING,
                changed_reference_id=rating.id,
                description='Rating has been updated',
                created_at=data['updated_at'],
                created_by=data['updated_by']
            )
            data = serialized_data.data
            del data['job']
            return Response({'statusCode': system_returns_code.SUCCESSFUL,
                             'data': data,
                             'exceptionString': []},
                            status=status.HTTP_200_OK)
        else:
            serializer_error = beautify_serializer_errors(
                serialized_data.errors)
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': serializer_error,
                    'data': {}},
                status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        parameters = request.query_params
        if 'rating_id' not in parameters:
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': ['Please provide rating_id'],
                    'data': {}},
                status=status.HTTP_400_BAD_REQUEST)
        result = delete_rating(parameters['rating_id'], user.id)
        deleted_at = datetime.datetime.utcnow()
        if result:
            create_system_changelog(
                action_performed=SystemChangelog.ActionPerformed.DELETED,
                changed_in=SystemChangelog.TableName.RATING,
                changed_reference_id=parameters['rating_id'],
                description='Rating has been deleted',
                created_at=deleted_at,
                created_by=user.id
            )
            return Response({'statusCode': system_returns_code.SUCCESSFUL,
                             'data': {'rating': "Rating has been deleted"},
                             'exceptionString': []},
                            status=status.HTTP_200_OK)
        else:
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': ['Rating not found'],
                    'data': {}},
                status=status.HTTP_400_BAD_REQUEST)
