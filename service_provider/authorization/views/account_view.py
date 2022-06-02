import datetime

import system_returns_code
from authorization.core.account.read import (get_account, get_all_accounts,
                                             get_lazzy_deleted_account)
from authorization.core.account.write import delete_account
from authorization.core.system_changelog.write import create_system_changelog
from transactions.core.stripe.write import stripe_attach_payment_method,stripe_create_payment_method,stripe_detach_payment_method,stripe_update_payment_detail
from authorization.core.utility.beautify_serializer_errors import \
    beautify_serializer_errors
from authorization.serializer.account.create_account_serializer import \
    CreateAccountSerializer
from authorization.serializer.account.get_account_serializer import \
    GetAccountSerializer
from authorization.serializer.account.restore_account_serializer import \
    RestoreAccountSerializer
from authorization.serializer.account.update_account_serializer import \
    UpdateAccountSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from authorization.models.account import Account
from django.contrib.auth.hashers import make_password
from django.conf import settings
from authorization.models.system_changelog import SystemChangelog


class AccountView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        parameters = request.data
        user = request.user
        parameters['user'] = user.id
        parameters['created_by'] = user.id
        parameters['created_at'] = datetime.datetime.utcnow()
        serilizedData = False
        isRestored=False

        # Checking Situation where account exist but has been deleted partially
        if 'card_number' in parameters:
            parameters['card_number_hashed'] = make_password(parameters['card_number'],settings.SECRET_KEY)
            account_detail = get_lazzy_deleted_account(
                parameters['card_number_hashed'], user.id)
            if account_detail:
                isRestored=True
                parameters['deleted_by'] = None
                parameters['deleted_at'] = None
                parameters['updated_by'] = user.id
                parameters['updated_at'] = datetime.datetime.utcnow()
                serilizedData = RestoreAccountSerializer(
                    account_detail, data=parameters)
        else:
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': ['Please provide card_number'],
                    'data':''},
                status=status.HTTP_400_BAD_REQUEST)

        # If above situation not exist
        if not serilizedData:
            serilizedData = CreateAccountSerializer(data=parameters)

        if serilizedData.is_valid():

            # Creating the payment method
            payment_method=stripe_create_payment_method("card",parameters['card_number'],parameters['expire_month'],parameters['expire_year'],parameters['cvv'])
            if payment_method['status']!=200:
                return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': payment_method['exception'],
                    'data':{}},
                status=status.HTTP_400_BAD_REQUEST)

            # Attaching the payment method to stripe
            attached_payment_method=stripe_attach_payment_method(user.stripe_customer_id,payment_method['data'].id)
            if attached_payment_method['status']!=200:
                return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': attached_payment_method['exception'],
                    'data':{}},
                status=status.HTTP_400_BAD_REQUEST)
            else:
                serilizedData.validated_data['stripe_payment_method_id']=attached_payment_method['data'].id

            result=serilizedData.save()
            # Adding into the system changelog
            if isRestored:
                create_system_changelog(
                    action_performed=SystemChangelog.ActionPerformed.UPDATED,
                    changed_in=SystemChangelog.TableName.ACCOUNT,
                    changed_reference_id=result.id,
                    description='Account was deleted by the user. It is restored now.',
                    created_at=parameters['created_at'],
                    created_by=parameters['created_by']
                )
            else:
                create_system_changelog(
                    action_performed=SystemChangelog.ActionPerformed.CREATED,
                    changed_in=SystemChangelog.TableName.ACCOUNT,
                    changed_reference_id=result.id,
                    description='Account has been created.',
                    created_at=parameters['created_at'],
                    created_by=parameters['created_by']
                )
            return Response(
                {'statusCode': system_returns_code.CREATED, 'data': serilizedData.data,'exceptionString':[]}, status=status.HTTP_201_CREATED)
        else:
            serializer_error = beautify_serializer_errors(serilizedData.errors)
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': serializer_error,
                    'data':{}},
                status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        parameters = request.GET.dict()
        user = request.user
        hasAccountId = True if 'account_id' in parameters else False

        if hasAccountId:
            account = get_account(parameters['account_id'], user.id)
        else:
            account = get_all_accounts(user.id)

        # Send even empty array of accounts but send error if a specific
        # account does not exit
        if (account and hasAccountId) or (not hasAccountId):
            serialized_data = GetAccountSerializer(
                account, many=not hasAccountId)
            return Response(
                {'statusCode': system_returns_code.SUCCESSFUL, 'data': serialized_data.data,'exceptionString':[]}, status=status.HTTP_200_OK)
        else:
            return Response(
                data={
                    'statusCode': system_returns_code.NOT_FOUND,
                    'exceptionString': ['Account does not exist'],
                    'data':{}},
                status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        # Setting Up Some Data
        parameters = request.data
        user = request.user
        parameters['updated_by'] = user.id
        parameters['updated_at'] = datetime.datetime.utcnow()

        # Confirming if the account id is passed or not
        if 'account_id' not in parameters:
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': ['account_id is required'],
                    'data':{}},
                status=status.HTTP_400_BAD_REQUEST)

        if 'card_number' in parameters:
            parameters['card_number_hashed'] = make_password(parameters['card_number'],settings.SECRET_KEY)

        account = get_account(parameters['account_id'], user.id)
        if account:
            serialized_data = UpdateAccountSerializer(account, data=parameters)
            if serialized_data.is_valid():
                
                # ====== Updating or creating new card if card number change from the strip end ======
                if account.card_number != str(parameters['card_number']) or account.cvv != str(parameters['cvv']): # Account number is updated so creating new payment method and deleting previous             
                    # Creating the payment method
                    payment_method=stripe_create_payment_method("card",parameters['card_number'],parameters['expire_month'],parameters['expire_year'],parameters['cvv'])
                    if payment_method['status']!=200:
                        return Response(
                        data={
                            'statusCode': system_returns_code.BAD_REQUEST,
                            'exceptionString': payment_method['exception'],
                            'data':{}},
                        status=status.HTTP_400_BAD_REQUEST)
                    # Attaching the payment method to stripe
                    attached_payment_method=stripe_attach_payment_method(user.stripe_customer_id,payment_method['data'].id)
                    if attached_payment_method['status']!=200:
                        return Response(
                        data={
                            'statusCode': system_returns_code.BAD_REQUEST,
                            'exceptionString': attached_payment_method['exception'],
                            'data':{}},
                        status=status.HTTP_400_BAD_REQUEST)
                    else:
                        serialized_data.validated_data['stripe_payment_method_id']=attached_payment_method['data'].id
                    # Deleting the previous payment method
                    stripe_account_deleted=stripe_detach_payment_method(account.stripe_payment_method_id)
                else:
                    stripe_updated_Account=stripe_update_payment_detail(account.stripe_payment_method_id,parameters['expire_month'],parameters['expire_year'])
                    if stripe_updated_Account['status']!=200:
                        return Response(
                            data={
                                'statusCode': system_returns_code.BAD_REQUEST,
                                'exceptionString': stripe_updated_Account['exception'],
                                'data':{}},
                            status=status.HTTP_400_BAD_REQUEST)


                result=serialized_data.save()
                # Adding into the system changelog
                create_system_changelog(
                    action_performed=SystemChangelog.ActionPerformed.UPDATED,
                    changed_in=SystemChangelog.TableName.ACCOUNT,
                    changed_reference_id=result.id,
                    description='Account has been updated.',
                    created_at=parameters['updated_at'],
                    created_by=parameters['updated_by']
                )
                return Response(
                    {'statusCode': system_returns_code.SUCCESSFUL, 'data': serialized_data.data,'exceptionString':[]}, status=status.HTTP_200_OK)
            else:
                serializer_error = beautify_serializer_errors(
                    serialized_data.errors)
                return Response(
                    data={
                        'statusCode': system_returns_code.BAD_REQUEST,
                        'exceptionString': serializer_error,
                        'data':{}},
                    status=status.HTTP_400_BAD_REQUEST)
        else:  # Account Not Found
            return Response(
                data={
                    'statusCode': system_returns_code.NOT_FOUND,
                    'exceptionString': ['Account does not exist'],
                    'data':{}},
                status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        user = request.user
        parameters = request.query_params
        if 'account_id' in parameters:
            account_id=parameters['account_id']
        else:
            return Response(
                    data={
                        'statusCode': system_returns_code.BAD_REQUEST,
                        'exceptionString': ['account_id is required'],
                        'data':{}},
                    status=status.HTTP_400_BAD_REQUEST)
        deleted_at=datetime.datetime.utcnow()          
        result = delete_account(account_id, user.id)
        if result:
            # Deleting the account from stripe end also
            stripe_account=stripe_detach_payment_method(result.stripe_payment_method_id)
            # Adding into the system changelog
            create_system_changelog(
                action_performed=SystemChangelog.ActionPerformed.DELETED,
                changed_in=SystemChangelog.TableName.ACCOUNT,
                changed_reference_id=parameters['account_id'],
                description='Account has been deleted.',
                created_at=deleted_at,
                created_by=user.id
            )
            return Response(
                data={
                    'statusCode': system_returns_code.SUCCESSFUL,
                    'data': {'account':'Account has been deleted'},
                    'exceptionString':[]},
                status=status.HTTP_200_OK)
        else:
            return Response(
                data={
                    'statusCode': system_returns_code.NOT_FOUND,
                    'exceptionString': ['Account does not exist'],
                    'data':{}},
                status=status.HTTP_404_NOT_FOUND)
