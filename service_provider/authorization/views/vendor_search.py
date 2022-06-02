from audioop import avg
import datetime
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.forms.models import model_to_dict
from rest_framework import status
import operator


from geopy import distance
from authorization.core.user.read import getUserById
from leads.core.service.read import getServiceByCategory
from authorization.core.location.read import getLocationByUser
from authorization.core.unavailability.read import getUserUnavailibilityByUser
from leads.core.service_category.read import getServiceCategoryById
from leads.core.leads.read import getLeadByVendor
from authorization.serializer.user import UserSerializer
from authorization.core.user.read import convertEnumToGender, convertEnumToType, convertEnumtoStatus
from authorization.core.account.read import get_all_accounts
from authorization.core.utility.serializer_error_formatter import serializerErrorFormatter
from leads.core.service.read import getServiceStatefromEnum
from authorization.serializer.location import LocationSerializer
from authorization.serializer.vendor_search import VendorSearchSerializer
from authorization.core.account.read import get_account_by_user_id
from transactions.serializer.transaction.create_transaction_serializer import CreateTransactionSerializer
from transactions.models.transaction import Transaction
from transactions.core.stripe.write import stripe_create_charge
from leads.core.rating.read import get_average_rating_and_no_of_review
from leads.core.job.read import get_all_jobs
import system_returns_code
from leads.models.job import Job


class VendorSearchView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        vendor_search_serializer = VendorSearchSerializer(
            data=request.query_params.dict())
        if vendor_search_serializer.is_valid():
            params = vendor_search_serializer.data

            if params.get('urgent') == True:
                acccounts = get_all_accounts(request.user.id)
                if acccounts:
                    services = getServiceByCategory(
                        params.get('service_category'))
                    if len(services) == 0:
                        content = {'statusCode': system_returns_code.BAD_REQUEST,
                                'exceptionString': ['No vendor available for this service.'],
                                'data': []}
                        return JsonResponse(content, status=status.HTTP_400_BAD_REQUEST)

                    service_final = calculate_distance(services, params.get(
                        'lat'), params.get('lng'), params.get('lng'))
                    params['date_time'] = datetime.datetime.strptime(
                        params.get('date_time'), '%Y-%m-%d %H:%M:%S%z')
                    # tmp_data = []
                    # for index, value in enumerate(service_final):
                    #     unavailibilities = getUserUnavailibilityByUser(
                    #         value['user'])
                    #     if unavailibilities:
                    #         for unavailability in unavailibilities:
                    #             if unavailability.start_time < params.get('date_time') and unavailability.end_time == None:
                    #                 pass
                    #             elif unavailability.start_time < params.get('date_time') < unavailability.end_time:
                    #                 pass
                    #             else:
                    #                 already_exists = False
                    #                 for tmp in tmp_data:
                    #                     if tmp['id'] == value['id']:
                    #                         already_exists = True
                    #                         break

                    #                 if already_exists == False:
                    #                     tmp_data.append(value)
                    #     else:
                    #         tmp_data.append(value)
                    # service_final = []
                    # for tmp in tmp_data:
                    #     leads = getLeadByVendor(tmp.get('user'))
                    #     already_exists = False
                    #     if leads:
                    #         for lead in leads:
                    #             if lead.job:
                    #                 if lead.job.start_datetime < params.get('date_time'):
                    #                     if lead.job.state == Job.JobState.CANCELED or lead.job.state == Job.JobState.COMPLETE:
                    #                         if already_exists == False:
                    #                             service_final.append(tmp)
                    #                             already_exists = True

                    #                 else:
                    #                     if already_exists == False:
                    #                         service_final.append(tmp)
                    #                         already_exists = True

                    #             else:
                    #                 if already_exists == False:
                    #                     service_final.append(tmp)
                    #                     already_exists = True

                    #     else:
                    #         service_final.append(tmp)
                    tmp = service_final
                    service_final = []
                    no_of_vendor = 0
                    for index, value in enumerate(tmp):
                        if no_of_vendor == 10:
                            break
                        no_of_vendor = no_of_vendor + 1
                        service_final.append(tmp[index])

                    service_final = sorted(
                        service_final, key=operator.itemgetter('distance'))
                    for index, value in enumerate(service_final):
                        rating_detail = get_average_rating_and_no_of_review(
                            value['user'])
                        all_completed_job = get_all_jobs(value['user'], state=2)
                        all_completed_job = len(all_completed_job)
                        service_final[index]['rating'] = rating_detail['total_rating']
                        service_final[index]['no_of_reviews'] = rating_detail['no_of_reviews']
                        service_final[index]['completed_job'] = all_completed_job

                        user = model_to_dict(getUserById(value['user']))
                        user_serializer = UserSerializer(user)

                        del service_final[index]['user']

                        service_final[index]['vendor'] = user_serializer.data
                        service_final[index]['vendor']['gender'] = convertEnumToGender(
                            service_final[index]['vendor']['gender'])
                        service_final[index]['vendor']['status'] = convertEnumtoStatus(
                            service_final[index]['vendor']['status'])
                        service_final[index]['vendor']['type'] = convertEnumToType(
                            service_final[index]['vendor']['type'])
                        location = getLocationByUser(
                            service_final[index]['vendor']['id'])
                        if location:
                            location_serializer = LocationSerializer(
                                data=model_to_dict(location))
                            if location_serializer.is_valid():
                                service_final[index]['location'] = location_serializer.data

                        else:
                            service_final[index]['Location'] = {}

                  
                    # if len(service_final) != 0:
                    #     acccounts = get_all_accounts(request.user.id)
                    #     if acccounts:
                    #         single_account = acccounts[0]
                    #         user = single_account.user
                    #         data = {}
                    #         data['user'] = request.user.id
                    #         data['account'] = single_account.id
                    #         data['amount'] = 75
                    #         data['type'] = Transaction.TransactionType.VENDOR_SEARCH
                    #         data['created_at'] = datetime.datetime.utcnow()
                    #         data['created_by'] = request.user.id
                    #         create_transaction_serializer = CreateTransactionSerializer(
                    #             data=data)
                    #         if create_transaction_serializer.is_valid():
                    #             # will call create transaction here
                    #             charge = stripe_create_charge(
                    #                 data['amount'], user.stripe_customer_id, single_account.stripe_payment_method_id, data)
                    #             if charge['status'] == 200:
                    #                 create_transaction_serializer.validated_data[
                    #                     'stripe_charge_id'] = charge['data'].id
                    #                 create_transaction_serializer.save()
                    #             else:
                    #                 return JsonResponse(
                    #                     {'status': status.HTTP_400_BAD_REQUEST, 'exceptionString': ['Transaction Failed Please Try Again'], 'data': []}, status=status.HTTP_400_BAD_REQUEST)
                    return JsonResponse(
                        {'data': service_final,
                        'exceptionString': [],
                        'statusCode': system_returns_code.SUCCESSFUL
                        },
                        status=system_returns_code.SUCCESSFUL)
                else:
                    content = {'statusCode': system_returns_code.BAD_REQUEST,
                               'exceptionString': ['To access the Urgent service please input a account.'],
                               'data': []}
                    return JsonResponse(content, status=status.HTTP_400_BAD_REQUEST)
                
            else:
                services = getServiceByCategory(params.get('service_category'))
                if len(services) == 0:
                    content = {'statusCode': system_returns_code.BAD_REQUEST,
                               'exceptionString': ['No vendor available for this service.'],
                               'data': []}
                    return JsonResponse(content, status=status.HTTP_400_BAD_REQUEST)

                service_final = calculate_distance(services, params.get(
                    'lat'), params.get('lng'), params.get('lng'))
                params['date_time'] = datetime.datetime.strptime(
                    params.get('date_time'), '%Y-%m-%d %H:%M:%S%z')

                # for index, value in enumerate(service_final):
                #     unavailibilities = getUserUnavailibilityByUser(
                #         value['user'])
                #     if unavailibilities:
                #         for unavailability in unavailibilities:
                #             if unavailability.start_time < params.get('date_time') and unavailability.end_time == None:
                #                 pass
                #             elif unavailability.start_time < params.get('date_time') < unavailability.end_time:
                #                 pass
                #             else:
                #                 already_exists = False
                #                 for tmp in tmp_data:
                #                     if tmp['id'] == value['id']:
                #                         already_exists = True
                #                         break

                #                 if already_exists == False:
                #                     tmp_data.append(value)
                #     else:
                #         tmp_data.append(value)
                
                # service_final = []
                # for tmp in tmp_data:
                #     leads = getLeadByVendor(tmp.get('user'))
                #     already_exists = False
                #     if leads:
                #         for lead in leads:
                #             if lead.job:
                #                 if lead.job.start_datetime < params.get('date_time') < lead.job.end_datetime:
                #                     if lead.job.state == Job.JobState.CANCELED or lead.job.state == Job.JobState.COMPLETE:
                #                         if already_exists == False:
                #                             service_final.append(tmp)
                #                             already_exists = True

                #                 else:
                #                     if already_exists == False:
                #                         service_final.append(tmp)
                #                         already_exists = True

                #             else:
                #                 if already_exists == False:
                #                     service_final.append(tmp)
                #                     already_exists = True

                #     else:
                #         service_final.append(tmp)
                tmp = service_final
                service_final = []
                no_of_vendor = 0
                for index, value in enumerate(tmp):
                    if no_of_vendor == 10:
                        break
                    accounts = get_all_accounts(tmp[index]['user'])
                    if accounts:
                        single_account = accounts[0]
                        user = single_account.user
                        data = {}
                        data['user'] = tmp[index]['user']
                        data['account'] = single_account.id
                        data['amount'] = 5
                        data['type'] = 4
                        data['created_at'] = datetime.datetime.utcnow()
                        data['created_by'] = request.user.id
                        create_transaction_serializer = CreateTransactionSerializer(
                            data=data)
                        if create_transaction_serializer.is_valid():
                            # will call create transaction here
                            # charge = stripe_create_charge(
                            #     data['amount'], user.stripe_customer_id, single_account.stripe_payment_method_id, data)
                            # charge={'status':200}
                            # if charge['status'] == 200:
                            #     create_transaction_serializer.validated_data[
                            #         'stripe_charge_id'] = charge['data'].id
                            #     create_transaction_serializer.save()
                            #     no_of_vendor = no_of_vendor + 1
                            service_final.append(tmp[index])
                service_final = sorted(
                    service_final, key=operator.itemgetter('distance'))
                for index, value in enumerate(service_final):
                    rating_detail = get_average_rating_and_no_of_review(
                        value['user'])
                    all_completed_job = get_all_jobs(value['user'], state=2)
                    all_completed_job = len(all_completed_job)
                    service_final[index]['rating'] = rating_detail['total_rating']
                    service_final[index]['no_of_reviews'] = rating_detail['no_of_reviews']
                    service_final[index]['completed_job'] = all_completed_job

                    user = model_to_dict(getUserById(value['user']))
                    user_serializer = UserSerializer(user)

                    del service_final[index]['user']

                    service_final[index]['vendor'] = user_serializer.data
                    service_final[index]['vendor']['gender'] = convertEnumToGender(
                        service_final[index]['vendor']['gender'])
                    service_final[index]['vendor']['status'] = convertEnumtoStatus(
                        service_final[index]['vendor']['status'])
                    service_final[index]['vendor']['type'] = convertEnumToType(
                        service_final[index]['vendor']['type'])
                    location = getLocationByUser(
                        service_final[index]['vendor']['id'])
                    if location:
                        location_serializer = LocationSerializer(
                            data=model_to_dict(location))
                        if location_serializer.is_valid():
                            service_final[index]['location'] = location_serializer.data

                    else:
                        service_final[index]['Location'] = {}
                
                return JsonResponse(
                    {'data': service_final,
                     'exceptionString': [],
                     'statusCode': system_returns_code.SUCCESSFUL
                     },
                    status=system_returns_code.SUCCESSFUL)

                # return JsonResponse(serializerErrorFormatter(vendor_search_serializer), status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse(serializerErrorFormatter(vendor_search_serializer), status=status.HTTP_400_BAD_REQUEST)

     
def calculate_distance(services, lat, lng, urgent):
    service_final = []
    print(services)
    for service in services:

        service_model = model_to_dict(service)
        del service_model['updated_by']
        del service_model['created_by']
        del service_model['deleted_by']
        del service_model['updated_at']
        del service_model['created_at']
        del service_model['deleted_at']
        service_model['user_status'] = 'ONLINE'
        service_model['service_state'] = getServiceStatefromEnum(
            service_model['state'])
        del service_model['state']
        del service_model['per_hour_rate']
        location = getLocationByUser(service.user)
        if location:
            service.location = location

            coords_1 = (location.lat, location.lng)
            coords_2 = (float(lat),
                        float(lng))

            service_model['distance'] = round(
                distance.distance(coords_1, coords_2).km, 2)
        else:
            service_model['distance'] = -1
        service_model['service_category'] = getServiceCategoryById(
            service_model['service_category']).name

        if urgent == True:
            if service_model['distance'] <= 10:
                service_final.append(service_model)
        else:
            service_final.append(service_model)
    return service_final