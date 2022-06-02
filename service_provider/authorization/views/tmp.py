from audioop import avg
import datetime
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.forms.models import model_to_dict
from rest_framework import status
import operator
import dateutil.parser
from django.db.models import Q
from django.db.models import Avg


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
from authorization.models.user import User
from leads.models.service import Service
from transactions.serializer.transaction.create_transaction_serializer import CreateTransactionSerializer
from transactions.core.review.read import getReviewsByUser
import system_returns_code
from transactions.core.stripe.write import stripe_create_charge


class VendorSearchView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        params = request.query_params.dict()

        if 'lat' not in params or 'lng' not in params:
            content = {'data': {},
                       'exceptionString': ['latitude and longitude are required'],
                       'statusCode': system_returns_code.BAD_REQUEST}
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

        if 'date_time' not in params:
            content = {'data': {},
                       'exceptionString': ['Date Time is required'],
                       'statusCode': system_returns_code.BAD_REQUEST}
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

        if 'service_category' not in params:
            content = {'data': {},
                       'exceptionString': ['Service Category is required'],
                       'statusCode': system_returns_code.BAD_REQUEST}
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

        if 'urgent' not in params:
            content = {'data': {},
                       'exceptionString': ['Urgent attribute is required'],
                       'statusCode': system_returns_code.BAD_REQUEST}
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

        service_final = []
        services = getServiceByCategory(params.get('service_category'))
        services = services.filter(
            Q(state=Service.ServiceStatus.APPROVED) & Q(user__deleted_by__isnull=True) & Q(user__type=User.UserType.VENDOR))
        try:
            date = params.get('date_time').split(' ')
            date = date[0] + ' ' + date[1] + '+' + date[2]
            date = dateutil.parser.parse(date)
        except:
            content = {'data': {},
                       'exceptionString': ['Date Time format is not correct'],
                       'statusCode': system_returns_code.BAD_REQUEST}
            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)
        for service in services:

            service_model = model_to_dict(service)
            del service_model['updated_by']
            del service_model['created_by']
            del service_model['deleted_by']
            del service_model['updated_at']
            del service_model['created_at']
            del service_model['deleted_at']
            del service_model['state']
            del service_model['per_hour_rate']
            location = getLocationByUser(service.user)
            if location:
                service.location = location

                coords_1 = (location.lat, location.lng)
                coords_2 = (float(params.get('lat')), float(params.get('lng')))

                service_model['distance'] = round(
                    distance.distance(coords_1, coords_2).km, 2)
            else:
                service_model['distance'] = 0
                
            service_model['service_category'] = getServiceCategoryById(
                service_model['service_category']).name

            if params.get('urgent') == 'true':
                if service_model['distance'] <= 10:
                    service_final.append(service_model)
            else:
                service_final.append(service_model)
        tmp_data = []
        for index, value in enumerate(service_final):
            unavailibilities = getUserUnavailibilityByUser(value['user'])
            if unavailibilities:
                for unavailability in unavailibilities:
                    if unavailability.start_time < date and unavailability.end_time == None:
                        pass
                    elif unavailability.start_time < date < unavailability.end_time:
                        pass
                    else:
                        already_exists = False
                        for tmp in tmp_data:
                            if tmp['id'] == value['id']:
                                already_exists = True
                                break

                        if already_exists == False:
                            tmp_data.append(value)
            else:
                tmp_data.append(value)
        service_final = []
        for tmp in tmp_data:
            leads = getLeadByVendor(tmp.get('user'))
            already_exists = False
            if leads:
                for lead in leads:
                    if lead.job:
                        if lead.job.start_datetime < date < lead.job.end_datetime:
                            if lead.job.state == 2 or lead.job.state == 4:
                                if already_exists == False:
                                    service_final.append(tmp)
                                    already_exists = True

                        else:
                            if already_exists == False:
                                service_final.append(tmp)
                                already_exists = True

                    else:
                        if already_exists == False:
                            service_final.append(tmp)
                            already_exists = True

            else:
                service_final.append(tmp)
        tmp = service_final
        service_final = []
        for index, value in enumerate(tmp):
            accounts = get_all_accounts(tmp[index]['user'])
            if accounts:
                for single_account in accounts:
                    user=single_account.user
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
                        charge=stripe_create_charge(data['amount'],user.stripe_customer_id,single_account.stripe_payment_method_id,data)
                        if charge['status']==200:
                            create_transaction_serializer.validated_data['stripe_charge_id']=charge['data'].id
                            create_transaction_serializer.save()
                            service_final.append(tmp[index])
                            break
                    else:
                        content = serializerErrorFormatter(
                            create_transaction_serializer)
                        return JsonResponse(content, status=system_returns_code.BAD_REQUEST)

        service_final = sorted(
            service_final, key=operator.itemgetter('distance'))
        for index, value in enumerate(service_final):
            reviews = getReviewsByUser(getUserById(value['user']))

            if reviews:
                rating = reviews.aggregate(Avg('ratings'))
                service_final[index]['rating'] = rating['ratings__avg']
            else:
                service_final[index]['rating'] = None

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

        return JsonResponse(
            {'data': service_final,
             'exceptionString': [],
             'statusCode': system_returns_code.SUCCESSFUL
             },
            status=system_returns_code.SUCCESSFUL)
