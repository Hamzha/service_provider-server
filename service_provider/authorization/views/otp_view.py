from datetime import datetime

import pytz
import system_returns_code
from authorization.core.otp.read import get_otp
from authorization.core.utility.beautify_serializer_errors import \
    beautify_serializer_errors
from authorization.core.utility.generate_otp import generate_otp
from authorization.core.system_changelog.write import create_system_changelog
from authorization.serializer.otp.create_otp_serializer import \
    CreateOtpSerializer
from authorization.serializer.otp.validate_otp_serializer import \
    ValidateOtpSerializer
from configuration import OTP_EXPIRY
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from authorization.models.system_changelog import SystemChangelog


class OtpGenerateView(APIView):
    def post(self, request):
        data = request.data
        data['otp'] = generate_otp()
        data['created_at'] = datetime.utcnow()
        serializer = CreateOtpSerializer(data=data)
        if serializer.is_valid():
            result = serializer.save()
            # Adding into the system changelog
            create_system_changelog(
                action_performed=SystemChangelog.ActionPerformed.CREATED,
                changed_in=SystemChangelog.TableName.OTP,
                changed_reference_id=result.id,
                description='OTP is generated.',
                created_at=result.created_at,
                created_by=result.created_by
            )
            email_plaintext_message = str(
                data['otp']) + ' is your otp code. Please do not share it with anyone.'
            send_mail(
                # title:
                "OTP code from SAIS",
                # message:
                email_plaintext_message,
                # from:
                "noreply@SAIS.local",
                # to:
                [data['email']],
                fail_silently=False)
            return Response({'statusCode': system_returns_code.CREATED,
                             'data': serializer.data,'exceptionString':[]}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': beautify_serializer_errors(
                        serializer.errors),
                    'data':{}},
                status=status.HTTP_400_BAD_REQUEST)


class OtpValidateView(APIView):
    def post(self, request):
        # Getting the data and validating it
        data = request.data
        serializer = ValidateOtpSerializer(data=data)

        if serializer.is_valid():  # If input/request data is valid
            otp = get_otp(data['otp'], data['email'])

            if otp:  # If otp found
                current_time = datetime.now(tz=pytz.utc)
                difference = current_time - otp.time_added
                difference = difference.total_seconds()
                if difference < OTP_EXPIRY:
                    deleted_at=datetime.utcnow()  
                    otp.delete(None)
                    create_system_changelog(
                        action_performed=SystemChangelog.ActionPerformed.DELETED,
                        changed_in=SystemChangelog.TableName.OTP,
                        changed_reference_id=otp.id,
                        description='OTP is deleted as it has been utilize.',
                        created_at=deleted_at,
                        created_by=None
                    )
                    return Response(
                        {
                            'statusCode': system_returns_code.SUCCESSFUL,
                            'data': {"OTP":'OTP is valid'},
                            'exceptionString':[]},
                        status=status.HTTP_200_OK)
                else:
                    return Response(
                        data={
                            'statusCode': system_returns_code.BAD_REQUEST,
                            'exceptionString': ['Your otp has been expired'],
                            'data':{}},
                        status=status.HTTP_400_BAD_REQUEST)
            else:  # when otp not found
                return Response(
                    data={
                        'statusCode': system_returns_code.BAD_REQUEST,
                        'exceptionString': ['OTP not found'],
                        'data':{}},
                    status=status.HTTP_400_BAD_REQUEST)
        else:  # if input/request data not valid
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': beautify_serializer_errors(
                        serializer.errors),
                    'data':{}},
                status=status.HTTP_400_BAD_REQUEST)
