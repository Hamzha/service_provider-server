import datetime

from rest_framework.permissions import IsAuthenticated
from authorization.core.system_changelog.write import create_system_changelog
from authorization.models.system_changelog import SystemChangelog
from rest_framework.views import APIView
from rest_framework.response import Response
from leads.serielizer.job.create_job_serializer import CreateJobSerializer
from leads.serielizer.job.get_job_serializer import GetJobSerializer
from leads.serielizer.job.update_job_serializer import UpdateJobSerializer
from leads.serielizer.job.get_job_serializer import GetJobSerializer
from leads.core.utility.beautify_serializer_errors import beautify_serializer_errors
from leads.core.job.read import get_lead, get_all_jobs, get_job_by_job_id, get_job_by_lead_id, get_job_state_internal_value, get_job_state_display_value, get_job_by_date
from leads.core.job.write import delete_job
# from leads.core.job.write import create_job_on_firebase,update_job_status_on_firebase,delete_job_on_firebase
from leads.core.firebase.write import delete_lead_on_firebase
from rest_framework import status
from leads.core.leads.read import get_lead_by_id
from authorization.core.account.read import get_all_accounts
from leads.core.leads.read import get_lead_by_only_id
from authorization.serializer.user import LeadSerializer
from leads.core.firebase.write import create_lead_on_firebase
from leads.core.leads.read import get_lead_external_value
from transactions.core.stripe.write import stripe_create_charge
from transactions.serializer.transaction.create_transaction_serializer import CreateTransactionSerializer
import system_returns_code
from authorization.core.utility.send_push_notification import send_push_notification
from firebase_admin import messaging
from authorization.core.user_device.read import getUserDeviceByUserList


class JobView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = request.GET.dict()
        user = request.user
        is_id_passed = False
        if 'state' not in data:
            data['state'] = None
        else:
            result = get_job_state_internal_value(data['state'])
            if result == "NONE":
                return Response(
                    data={
                        'statusCode': system_returns_code.BAD_REQUEST,
                        'exceptionString': ['Please provide valid state'],
                        'data': {}},
                    status=status.HTTP_400_BAD_REQUEST)
            else:
                data['state'] = result

        if 'lead_id' in data:
            is_id_passed = True
            jobs = get_job_by_lead_id(data['lead_id'], user.id)
        elif 'start_datetime' in data and 'end_datetime' in data:
            try:
                start_datetime = datetime.datetime.strptime(
                    data['start_datetime'], "%Y-%m-%d")
                end_datetime = datetime.datetime.strptime(
                    data['end_datetime'], "%Y-%m-%d")
                jobs = get_job_by_date(
                    user.id, start_datetime=start_datetime, end_datetime=end_datetime, state=data['state'])
            except ValueError:
                return Response(
                    data={
                        'statusCode': system_returns_code.BAD_REQUEST,
                        'exceptionString': ['Please provide valid data of formate Y-m-d'],
                        'data': {}},
                    status=status.HTTP_400_BAD_REQUEST)
        elif 'start_datetime' in data:
            try:
                my_date = datetime.datetime.strptime(
                    data['start_datetime'], "%Y-%m-%d")
                jobs = get_job_by_date(
                    user.id, start_datetime=my_date, state=data['state'])
            except ValueError:
                return Response(
                    data={
                        'statusCode': system_returns_code.BAD_REQUEST,
                        'exceptionString': ['Please provide valid data of formate Y-m-d'],
                        'data': {}},
                    status=status.HTTP_400_BAD_REQUEST)
        elif 'end_datetime' in data:
            try:
                my_date = datetime.datetime.strptime(
                    data['end_datetime'], "%Y-%m-%d")
                jobs = get_job_by_date(
                    user.id, end_datetime=my_date, state=data['state'])
            except ValueError:
                return Response(
                    data={
                        'statusCode': system_returns_code.BAD_REQUEST,
                        'exceptionString': ['Please provide valid data of formate Y-m-d'],
                        'data': {}},
                    status=status.HTTP_400_BAD_REQUEST)
        elif 'job_id' in data:
            is_id_passed = True
            jobs = get_job_by_job_id(data['job_id'], user.id)
        else:
            jobs = get_all_jobs(user.id, state=data['state'])

        if (jobs and is_id_passed) or (not is_id_passed):
            serialized_data = GetJobSerializer(
                jobs, many=False if is_id_passed else True)
            data = serialized_data.data
            return Response({'statusCode': system_returns_code.SUCCESSFUL,
                            'data': serialized_data.data,
                             'exceptionString': []}, status=status.HTTP_200_OK,)
        else:
            return Response(
                data={
                    'statusCode': system_returns_code.NOT_FOUND,
                    'exceptionString': ['Job not found'],
                    'data': {}},
                status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        data = request.data
        user = request.user

        data['created_by'] = user.id
        data['created_at'] = datetime.datetime.utcnow()
        data['state'] = 1

        # ===== Getting The Lead =====
        if 'lead_id' not in data:
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': ['Please provide lead_id'],
                    'data': {}},
                status=status.HTTP_400_BAD_REQUEST)
        lead = get_lead(data['lead_id'], user.id)
        # lead = get_lead_by_ovly_id(data['lead_id'])
        if not lead:
            return Response(
                data={
                    'statusCode': system_returns_code.NOT_FOUND,
                    'exceptionString': ['lead not found'],
                    'data': {}},
                status=status.HTTP_404_NOT_FOUND)
        elif lead.job is not None and lead.job.deleted_by is None:
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': ['Job is already created for this lead'],
                    'data': {}},
                status=status.HTTP_400_BAD_REQUEST)

        # ===== Serializing and validation the job =====
        serialized_data = CreateJobSerializer(data=data)
        if serialized_data.is_valid():
            # Creating the job and updating the lead
            job = serialized_data.save()

            create_system_changelog(
                action_performed=SystemChangelog.ActionPerformed.CREATED,
                changed_in=SystemChangelog.TableName.JOB,
                changed_reference_id=job.id,
                description='Job has been created.',
                created_at=data['created_at'],
                created_by=data['created_by']
            )
            # ========== Sending notification ==========
            user_lists = [lead.client.id,lead.vendor.id]
            user_devices = getUserDeviceByUserList(user_lists)
            user_devices_list=[]
            for user_device in user_devices:
                user_devices_list.append(user_device.identifier)
            notificationObj=messaging.Notification(
                title='New Job Alert',
                body='Job has been created.',
            )
            dataObj={
                'type':'created',
                'model_name':'job',
            }
            response=send_push_notification(user_devices_list,dataObj,notificationObj)
            # create_job_on_firebase(job.id,lead.client.id,lead.vendor.id,get_job_state_display_value(job.state))
            lead.job = job
            lead.save()
            if lead.urgent == True:
                account= get_all_accounts(lead.client.id).first()

                if account:
                    data_acc= {}
                    data_acc['type']= 5
                    data_acc['amount']= 75
                    data_acc['account']= account.id
                    data_acc['lead'] = lead.id
                    create_transaction_serializer= CreateTransactionSerializer(
                        data=data_acc)
                    if create_transaction_serializer.is_valid():
                        # Charging the vendor
                        charge= stripe_create_charge(
                            data_acc['amount'], lead.client.stripe_customer_id, account.stripe_payment_method_id, data_acc)
                        if charge['status'] != 200:

                            content= {'statusCode': system_returns_code.BAD_REQUEST,
                                    'data': {}, 'exceptionString': ["Unable to contact vendor because of payment issues. Please try another vendor."]}
                            return Response(content, status=system_returns_code.BAD_REQUEST)
                        create_transaction_serializer.validated_data['stripe_charge_id']= charge['data'].id
                        create_transaction_serializer.save()
                        # create_lead_on_firebase
                        # create_lead_on_firebase(lead.id, lead.client.id,
                        #                         lead.vendor.id, get_lead_external_value(lead.state))
                        content= {'statusCode': system_returns_code.CREATED,
                                  'data': serialized_data.data, 'exceptionString': []}
                        return Response(content, status=system_returns_code.CREATED)
                else:
                    content= {'statusCode': system_returns_code.BAD_REQUEST,
                            'data': {}, 'exceptionString': ["Unable to contact vendor because of payment issues. Please try another vendor."]}
                    return Response(content, status=system_returns_code.BAD_REQUEST)
            else:
                # create_lead_on_firebase(lead.id, lead.client.id,
                #         lead.vendor.id, get_lead_external_value(lead.state))
                content = {'statusCode': system_returns_code.CREATED,
                           'data': serialized_data.data, 'exceptionString': []}
                return Response(content, status=system_returns_code.CREATED)
        else:  # Invalid job detail
            serializer_error= beautify_serializer_errors(
                serialized_data.errors)
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': serializer_error,
                    'data': {}},
                status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        data= request.query_params
        user= request.user

        # Getting the job id
        if 'job_id' not in data:
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': ['Please provide job_id'],
                    'data': {}},
                status=status.HTTP_400_BAD_REQUEST)

        deleted_at= datetime.datetime.utcnow()
        result= delete_job(data['job_id'], user.id)
        if result:
            # Adding into the system changelog
            # delete_job_on_firebase(data['job_id'])
            delete_lead_on_firebase(result.id)
            create_system_changelog(
                action_performed=SystemChangelog.ActionPerformed.DELETED,
                changed_in=SystemChangelog.TableName.JOB,
                changed_reference_id=data['job_id'],
                description='Job has been deleted.',
                created_at=deleted_at,
                created_by=user.id
            )
            return Response(
                data={
                    'statusCode': system_returns_code.SUCCESSFUL,
                    'data': {"job": 'job has been deleted'},
                    'exceptionString': []},
                status=status.HTTP_200_OK)
        else:
            return Response(
                data={
                    'statusCode': system_returns_code.NOT_FOUND,
                    'exceptionString': ["Job not found"],
                    'data': {}},
                status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        # Setting Up Some Data
        data= request.data
        user= request.user
        data['updated_by']= user.id
        data['updated_at']= datetime.datetime.utcnow()

        if 'state' in data:
            data['state']= get_job_state_internal_value(data['state'])
            if data['state'] == 'NONE':
                return Response(
                    data={
                        'statusCode': system_returns_code.BAD_REQUEST,
                        'exceptionString': ['Invalid state'],
                        'data': {}},
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': ['Please provide state'],
                    'data': {}},
                status=status.HTTP_400_BAD_REQUEST)

        # Confirming if the job_id is passed or not
        if 'job_id' not in data:
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': ['Please provide job_id'],
                    'data': {}},
                status=status.HTTP_400_BAD_REQUEST)

        # Getting the job
        job= get_job_by_job_id(data['job_id'], user.id)
        if not job:
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': ['Job Not Found'],
                    'data': {}},
                status=status.HTTP_400_BAD_REQUEST)
        lead=job.lead_job
        # Incase if the job is cancelled dont need to update
        if job.state == 4 and data['state'] == 4:
            return Response({'statusCode': system_returns_code.BAD_REQUEST, 'exceptionString': [
                            'You can not update the cancelled job'], 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        elif data['state'] == 4:  # In case of cancellation update only state
            job.state= 4
            job.save()
            # update_job_status_on_firebase(job.id,get_job_state_display_value(data['state']))
            # Adding into the system changelog
            create_system_changelog(
                action_performed=SystemChangelog.ActionPerformed.UPDATED,
                changed_in=SystemChangelog.TableName.JOB,
                changed_reference_id=job.id,
                description='Job has been cancelled.',
                created_at=data['updated_at'],
                created_by=data['updated_by']
            )
            # ========== Sending notification ==========
            user_lists = [lead.client.id,lead.vendor.id]
            user_devices = getUserDeviceByUserList(user_lists)
            user_devices_list=[]
            for user_device in user_devices:
                user_devices_list.append(user_device.identifier)
            notificationObj=messaging.Notification(
                title='Job Cancelled',
                body='Job has been cancelled.',
            )
            dataObj={
                'type':'updated',
                'model_name':'job',
            }
            response=send_push_notification(user_devices_list,dataObj,notificationObj)
            return Response({'statusCode': system_returns_code.SUCCESSFUL, 'data': {
                            "job": 'Job jas been cancelled'}, 'exceptionString': []}, status=status.HTTP_200_OK)

        serialized_data= UpdateJobSerializer(job, data=data)
        if serialized_data.is_valid():
            # Checking if state is updated for firebase to update state
            is_state_updated= False
            if job.state != data['state']:
                is_state_updated= True

            # updating the data
            result = serialized_data.save()

            # Updating in the database if state updated
            # if is_state_updated:
            #     update_job_status_on_firebase(job.id,get_job_state_display_value(data['state']))
            result= serialized_data.save()
            create_system_changelog(
                action_performed=SystemChangelog.ActionPerformed.UPDATED,
                changed_in=SystemChangelog.TableName.JOB,
                changed_reference_id=result.id,
                description='Job has been updated.',
                created_at=data['updated_at'],
                created_by=data['updated_by']
            )
            # ========== Sending notification ==========
            user_lists = [lead.client.id,lead.vendor.id]
            user_devices = getUserDeviceByUserList(user_lists)
            user_devices_list=[]
            for user_device in user_devices:
                user_devices_list.append(user_device.identifier)
            notificationObj=messaging.Notification(
                title='Job updated',
                body='Job has been updated.',
            )
            dataObj={
                'type':'updated',
                'model_name':'job',
            }
            response=send_push_notification(user_devices_list,dataObj,notificationObj)
            return Response({'statusCode': system_returns_code.SUCCESSFUL,
                            'data': serialized_data.data,
                             'exceptionString': []}, status=status.HTTP_200_OK)
        else:
            serializer_error= beautify_serializer_errors(
                serialized_data.errors)
            return Response(
                data={
                    'statusCode': system_returns_code.BAD_REQUEST,
                    'exceptionString': serializer_error,
                    'data': {}},
                status=status.HTTP_400_BAD_REQUEST)
