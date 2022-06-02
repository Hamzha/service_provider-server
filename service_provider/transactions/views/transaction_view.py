import datetime

import system_returns_code
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from transactions.core.transaction.read import (get_all_transaction,
                                                get_transaction, get_transaction_type_internal_value)
from transactions.core.transaction.write import delete_transaction
from authorization.core.system_changelog.write import create_system_changelog
from authorization.models.system_changelog import SystemChangelog
from transactions.core.utility.beautify_serializer_errors import \
    beautify_serializer_errors
from transactions.serializer.transaction.create_transaction_serializer import \
    CreateTransactionSerializer
from transactions.serializer.transaction.get_transaction_serializer import \
    GetTransactionSerializer
from transactions.serializer.transaction.update_transaction_serializer import \
    UpdateTransactionSerializer
from leads.core.rating.read import get_average_rating
from transactions.core.stripe.write import stripe_create_charge

class TransactionView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        parameters = request.GET.dict()
        hasTransactionId = True if 'transaction_id' in parameters else False
        transaction_type_id=None
        user=request.user

        if 'transaction_type' in parameters:
            transaction_type_id=get_transaction_type_internal_value(parameters["transaction_type"])
            if transaction_type_id =='NONE':
                return Response(
                    data={
                        'statusCode': system_returns_code.BAD_REQUEST,
                        'exceptionString': ['Invalid transaction type'], 'data': {}},
                    status=status.HTTP_400_BAD_REQUEST)

        if hasTransactionId:
            transaction = get_transaction(parameters['transaction_id'],user.id)
        else:
            transaction = get_all_transaction(user.id,transaction_type_id)

        # Send even empty array of transaction but send error if a specific
        # transaction does not exit
        if (transaction and hasTransactionId) or (not hasTransactionId):
            serialized_data = GetTransactionSerializer(
                transaction, many=not hasTransactionId)
            data=serialized_data.data
            if hasTransactionId:
                client_rating=get_average_rating(data['client']['id'])
                vendor_rating=get_average_rating(data['vendor']['id'])
                data['client']['total_rating']=client_rating
                data['vendor']['total_rating']=vendor_rating
            else:
                users=[]
                for transaction in data:
                    client_rating_found=False
                    vendor_rating_found=False
                    for user in users:
                        if user['id']==transaction['client']['id']:
                            client_rating_found=True
                            transaction['client']['total_rating']=user['rating']
                        if user['id']==transaction['vendor']['id']:
                            vendor_rating_found=True
                            transaction['vendor']['total_rating']=user['rating']
                    if not client_rating_found:
                        rating=get_average_rating(transaction['client']['id'])
                        users.append({'id':transaction['client']['id'],'rating':rating})
                    if not vendor_rating_found:
                        rating=get_average_rating(transaction['vendor']['id'])
                        users.append({'id':transaction['vendor']['id'],'rating':rating})    

            return Response({'statusCode': system_returns_code.SUCCESSFUL,
                             'data': data, 'exceptionString': []}, status=status.HTTP_200_OK)
        else:
            return Response(
                data={
                    'statusCode': system_returns_code.NOT_FOUND,
                    'exceptionString': ['This transaction does not exist'], 'data': {}},
                status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        data = request.data
        user = request.user

        data['created_by'] = user.id
        data['created_at'] = datetime.datetime.utcnow()
        # Making sure that account and leads are passed to serializer error will handle by serializer
        if 'account_id' not in data:
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': ['Please provide account_id'], 'data': {}},
                status=status.HTTP_400_BAD_REQUEST)
        if 'lead_id' not in data:
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': ['Please provide lead_id'], 'data': {}},
                status=status.HTTP_400_BAD_REQUEST)
        # Converting display value of type to internal value
        if 'type' not in data:
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': ['Invalid transaction type'], 'data': {}},
                status=status.HTTP_400_BAD_REQUEST)
        type = get_transaction_type_internal_value(data['type'])
        if type == 'NONE':
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': ['Invalid transaction type'], 'data': {}},
                status=status.HTTP_400_BAD_REQUEST)

        data['type'] = type
        data['account'] = data['account_id']
        data['lead'] = data['lead_id']
        serialized_data = CreateTransactionSerializer(data=data)
        if serialized_data.is_valid():
            # Charging the client
            account=serialized_data.validated_data['account']
            charge=stripe_create_charge(data['amount'],user.stripe_customer_id,account.stripe_payment_method_id,data)
            if charge['status'] != 200:
                return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': charge['exception'], 'data': {}},
                status=status.HTTP_400_BAD_REQUEST)
            else:
                serialized_data.validated_data['stripe_charge_id']=charge['data'].id
            # Creating the transaction
            result=serialized_data.save()
            # Adding into the system changelog
            create_system_changelog(
                action_performed=SystemChangelog.ActionPerformed.CREATED,
                changed_in=SystemChangelog.TableName.TRANSACTION,
                changed_reference_id=result.id,
                description='Transaction has been created.',
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
                    'exceptionString': serializer_error, 'data': {}},
                status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        parameters = request.query_params
        if 'transaction_id' in parameters:
            transaction_id = parameters['transaction_id']
        else:
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': ['please provide transaction_id'], 'data': {}},
                status=status.HTTP_400_BAD_REQUEST)
        deleted_at=datetime.datetime.utcnow()   
        result = delete_transaction(transaction_id, user.id)
        if result:
            # Adding into the system changelog
            create_system_changelog(
                action_performed=SystemChangelog.ActionPerformed.DELETED,
                changed_in=SystemChangelog.TableName.TRANSACTION,
                changed_reference_id=transaction_id,
                description='Transaction has been deleted.',
                created_at=deleted_at,
                created_by=user.id
            )
            return Response(
                data={
                    'statusCode': system_returns_code.SUCCESSFUL,
                    'data': {"transaction":'Transaction has been deleted'}, 'exceptionString': []},
                status=status.HTTP_200_OK)
        else:
            return Response(
                data={
                    'statusCode': system_returns_code.NOT_FOUND,
                    'exceptionString': ['This Transaction does not exist'], 'data': {}},
                status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        # Setting Up Some Data
        data = request.data
        user = request.user
        data['updated_by'] = user.id
        data['updated_at'] = datetime.datetime.utcnow()

        # Converting display value of type to internal value
        if 'type' not in data:
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': ['Invalid transaction type'], 'data': {}},
                status=status.HTTP_400_BAD_REQUEST)
        type = get_transaction_type_internal_value(data['type'])
        data['type'] = type
        if type == 'NONE':
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': ['Invalid transaction type'], 'data': {}},
                status=status.HTTP_400_BAD_REQUEST)

        # Confirming if the transaction id is passed or not
        if 'transaction_id' not in data:
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': ['please provide transaction_id'], 'data': {}},
                status=status.HTTP_400_BAD_REQUEST)

        # Gettting the transaction
        transaction = get_transaction(data['transaction_id'])

        if transaction:  # Transaction found so proceed updation
            serialized_data = UpdateTransactionSerializer(
                transaction, data=data)
            if serialized_data.is_valid():  # Checking if data to be updated is provided correctly
                result=serialized_data.save()
                # Adding into the system changelog
                create_system_changelog(
                    action_performed=SystemChangelog.ActionPerformed.UPDATED,
                    changed_in=SystemChangelog.TableName.TRANSACTION,
                    changed_reference_id=result.id,
                    description='Transaction has been updated.',
                    created_at=data['updated_at'],
                    created_by=data['updated_by']
                )
                return Response({'statusCode': system_returns_code.SUCCESSFUL,
                                 'data': serialized_data.data, 'exceptionString': []}, status=status.HTTP_200_OK)
            else:
                serializer_error = beautify_serializer_errors(
                    serialized_data.errors)
                return Response(
                    data={
                        'statusCode': system_returns_code.BAD_REQUEST,
                        'exceptionString': serializer_error, 'data': {}},
                    status=status.HTTP_400_BAD_REQUEST)
        else:  # Transaction Not Found
            return Response(
                data={
                    'statusCode': system_returns_code.NOT_FOUND,
                    'exceptionString': ['This transaction does not exist'], 'data': {}},
                status=status.HTTP_404_NOT_FOUND)
