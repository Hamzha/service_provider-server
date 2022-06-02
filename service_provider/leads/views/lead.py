from datetime import datetime
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from uritemplate import partial
from leads.serielizer.lead import LeadSerlizer, CreateLeadSerializer
from leads.core.service.read import getServiceByID
from leads.core.leads.read import get_pending_lead, get_leads, get_lead_by_id, get_lead_internal_value
from leads.core.job.read import get_lead
from authorization.core.utility.serializer_error_formatter import serializerErrorFormatter
from authorization.core.account.read import get_all_accounts
from leads.core.firebase.write import create_lead_on_firebase
from leads.core.leads.read import get_lead_external_value
from transactions.core.stripe.write import stripe_create_charge
from transactions.serializer.transaction.create_transaction_serializer import CreateTransactionSerializer
import system_returns_code
from authorization.serializer.location import LocationSerializerWithoutUser
from leads.serielizer.leads.update_lead_serializer import UpdateLeadSerializer
from leads.models.lead import Lead
from django.forms.models import model_to_dict
from authorization.core.utility.send_push_notification import send_push_notification
from firebase_admin import messaging
from authorization.core.user_device.read import getUserDeviceByUserList

class LeadViews(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        params = request.data

        if 'service_id' not in params:
            content = {'statusCode': system_returns_code.BAD_REQUEST,
                       'data': {}, 'exceptionString': ['Please provide Service Id.']}
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

        if 'urgent' not in params:
            content = {'statusCode': system_returns_code.BAD_REQUEST,
                       'data': {}, 'exceptionString': ['Please provide Urgent parameter.']}
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)
        else:
            if params['urgent'] == 'false':
                params['urgent'] = False
            elif params['urgent'] == 'true':
                params['urgent'] = True
            else:
                content = {'statusCode': system_returns_code.BAD_REQUEST,
                           'data': {}, 'exceptionString': ['Please provide Urgent parameter correctly.']}
                return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

        if 'lng' not in params or 'lat' not in params:
            content = {'statusCode': system_returns_code.BAD_REQUEST,
                       'data': {}, 'exceptionString': ['Please provide lng and lat']}
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)
        else:
            location_data = {}
            location_data['lat'] = params.get('lat')
            location_data['lng'] = params.get('lng')
            location_data['created_at'] = datetime.utcnow()
            location_data['created_by'] = request.user.id
            location_serializer = LocationSerializerWithoutUser(
                data=location_data)
            if location_serializer.is_valid():
                location = location_serializer.save()
            else:
                content = serializerErrorFormatter(location_serializer)
                return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

        service = getServiceByID(params['service_id'])
        if not service:
            content = {'statusCode': system_returns_code.BAD_REQUEST,
                       'data': {}, 'exceptionString': ['Please provide a valid Service Id.']}
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)
        data = {}
        data['service'] = service.id
        data['urgent'] = params['urgent']
        data['vendor'] = service.user.id
        data['client'] = request.user.id
        data['created_at'] = datetime.utcnow()
        data['created_by'] = request.user.id
        data['location'] = location.id
        if 'description' in params:
            data['description'] = params['description']
        if 'quotation_description' in params:
            data['quotation_description'] = params['quotation_description']
        if 'quotation_price' in params:
            data['quotation_price'] = params['quotation_price']

        data['state'] = Lead.LeadState.PENDING
        lead_serializer = CreateLeadSerializer(data=data)
        if lead_serializer.is_valid():
            data = lead_serializer.save()
            # data = lead_serializer
            if data.urgent == False:
                account = get_all_accounts(data.vendor.id).first()

                if account:
                    data_tmp = {}
                    data_tmp['type'] = 2
                    data_tmp['amount'] = 5
                    data_tmp['account'] = account.id
                    data_tmp['lead'] = data.id
                    create_transaction_serializer = CreateTransactionSerializer(
                        data=data_tmp)
                    if create_transaction_serializer.is_valid():
                        # Charging the vendor
                        charge = stripe_create_charge(
                            data_tmp['amount'], data.vendor.stripe_customer_id, account.stripe_payment_method_id, data_tmp)
                        if charge['status'] != 200:
                            data.delete(None)
                            content = {'statusCode': system_returns_code.BAD_REQUEST,
                                    'data': {}, 'exceptionString': ["Unable to contact vendor because of payment issues. Please try another vendor."]}
                            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)
                        create_transaction_serializer.validated_data['stripe_charge_id'] = charge['data'].id
                        create_transaction_serializer.save()
            # create_lead_on_firebase
            create_lead_on_firebase(data.id, data.client.id,
                                    data.vendor.id, get_lead_external_value(data.state))
            content = {'statusCode': system_returns_code.CREATED,
                            'data': lead_serializer.data, 'exceptionString': []}
            # ========== Sending notification ==========
            user_lists = [data.client.id,data.vendor.id]
            user_devices = getUserDeviceByUserList(user_lists)
            user_devices_list=[]
            for user_device in user_devices:
                user_devices_list.append(user_device.identifier)
            notificationObj=messaging.Notification(
                title='New Lead Alert',
                body='Lead has been generated against the service.',
            )
            dataObj={
                'type':'created',
                'model_name':'lead',
            }
            response=send_push_notification(user_devices_list,dataObj,notificationObj)
            return JsonResponse(content, status=system_returns_code.CREATED)
        else:
            content = serializerErrorFormatter(lead_serializer)
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

    def get(self, request):
        data = request.GET.dict()
        user = request.user
        is_id_passed = False

        if 'pending' in data:
            lead_serializer = get_pending_lead(user.id)
        if 'lead_id' in data:
            is_id_passed = True
            lead_serializer = get_lead_by_id(data['lead_id'], user.id)
            if not lead_serializer:
                content = {'statusCode': system_returns_code.NOT_FOUND,
                           'exceptionString': ['lead not found'],
                           'data': {}}
                return JsonResponse(content, status=system_returns_code.NOT_FOUND)
        else:
            lead_serializer = get_leads(user.id)

        if (lead_serializer and is_id_passed) or (not is_id_passed):
            serialized_data = LeadSerlizer(
                lead_serializer, many=False if is_id_passed else True)
            content = {'statusCode': system_returns_code.SUCCESSFUL,
                       'exceptionString': [],
                       'data': serialized_data.data}
            return JsonResponse(content, status=system_returns_code.SUCCESSFUL)
        else:
            content = serializerErrorFormatter(lead_serializer)
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

    def put(self, request):
        data = request.data
        user = request.user
        data['updated_by'] = user.id
        data['updated_at'] = datetime.utcnow()
        if 'state' in data:
            data['state'] = get_lead_internal_value(data['state'])
            if(data['state'] == 'NONE'):
                content = {'statusCode': system_returns_code.BAD_REQUEST,
                           'exceptionString': ['Please provide valid state'],
                           'data': {}}
                return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

        if 'lead_id' not in data:
            content = {'statusCode': system_returns_code.BAD_REQUEST,
                       'exceptionString': ['Please provide lead_id'],
                       'data': {}}
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)
        lead = get_lead(data['lead_id'], user.id)

        if not lead:
            content = {'statusCode': system_returns_code.BAD_REQUEST,
                       'exceptionString': ['Lead not found'], 'data': {}}
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

        serialized_data = UpdateLeadSerializer(lead, data=data, partial=True)
        if serialized_data.is_valid():
            serialized_data.save()
            # ========== Sending notification ==========
            user_lists = [lead.vendor.id,lead.client.id]
            user_devices = getUserDeviceByUserList(user_lists)
            user_devices_list = []
            for user_device in user_devices:
                user_devices_list.append(user_device.identifier)
            notificationObj=messaging.Notification(
                title='Lead Updated',
                body='Lead has been updated.',
            )
            dataObj={
                'type':'updated',
                'model_name':'lead',
            }
            response=send_push_notification(user_devices_list,dataObj,notificationObj)
            content = {'statusCode': system_returns_code.SUCCESSFUL,
                       'data': serialized_data.data, 'exceptionString': []}
            return JsonResponse(content, status=system_returns_code.SUCCESSFUL)
        else:
            content = serializerErrorFormatter(serialized_data)
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)