from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import system_returns_code
# import firebase_auth
from firebase_admin import auth
from rest_framework.response import Response

class FirebaseAuthView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        user=request.user
        credential=auth.create_custom_token(str(user.id))
        return Response({'statusCode': system_returns_code.CREATED,
                             'data': {'token':credential},'exceptionString':[]}, status=status.HTTP_201_CREATED)
        