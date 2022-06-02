from rest_framework.views import APIView
from rest_framework.response import Response
import system_returns_code
from rest_framework import status
from leads.core.rating.read import get_all_ratings_by_job_id
from leads.core.rating.read import get_rating
from authorization.models.user import User
from leads.serielizer.rating.get_rating_serializer import GetRatingSerializer

class RatingResponseView(APIView):
    def post(self, request):
        data = request.data
        user = request.user

        if 'response' not in data or 'rating_id' not in data or data['response']==None or len(data['response'])==0:
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': ['Please response and rating_id'],
                    'data': {}},
                status=status.HTTP_400_BAD_REQUEST)

        rating=get_rating(data['rating_id'])
        if not rating:
            return Response(
            data={
                'statusCode': system_returns_code.BAD_REQUEST,
                'exceptionString': ['Rating not found'],
                'data': {}},
            status=status.HTTP_400_BAD_REQUEST)
        # Get lead od particular rating
        lead=rating.job.lead_job

        # Validating if the response is already provided
        if rating.response:
            return Response(
            data={
                'statusCode': system_returns_code.BAD_REQUEST,
                'exceptionString': ['Response for this rating is already given'],
                'data': {}},
            status=status.HTTP_400_BAD_REQUEST)

        # Validating if rating is being updated by either client or vendor instead of third person
        if not(lead.client==user or lead.vendor==user):
            return Response(
            data={
                'statusCode': system_returns_code.BAD_REQUEST,
                'exceptionString': ['You are not authorize to give rating'],
                'data': {}},
            status=status.HTTP_400_BAD_REQUEST)

        # Validating if the creator of rating is not updating the response
        if rating.user==user:
            return Response(
            data={
                'statusCode': system_returns_code.BAD_REQUEST,
                'exceptionString': ['You are not authorize to create response for your own rating'],
                'data': {}},
            status=status.HTTP_400_BAD_REQUEST)

        rating.response=data['response']
        rating.save()

        rating_serializer=GetRatingSerializer(rating)
        return Response({'statusCode': system_returns_code.SUCCESSFUL,
                         'data': rating_serializer.data,
                         'exceptionString': []}, status=status.HTTP_200_OK,)

 