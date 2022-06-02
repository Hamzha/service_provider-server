from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from leads.core.service_category.read import getAllServiceCategories, getServiceCategory
from django.http import JsonResponse
from leads.serielizer.service_category import ServiceCategorySerlizer
import system_returns_code


class ServiceCategoryView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = request.query_params
        if 'parent_id' in data:
            service_categories = getAllServiceCategories(parent_id=data['parent_id'])
        else:
            service_categories = getAllServiceCategories()
        
        if not service_categories:
            content = {'statusCode': system_returns_code.BAD_REQUEST,
                       'data': {}, 'exceptionString': ['No Service Category found.']}

            return JsonResponse(content, status=system_returns_code.BAD_REQUEST)
        # data = getServiceCategory(service_categories)
        service_category_serlizer = ServiceCategorySerlizer(
            service_categories, many=True)
        content = {'statusCode': system_returns_code.SUCCESSFUL,
                   'data': service_category_serlizer.data, 'exceptionString': []}
        return JsonResponse(content, status=system_returns_code.SUCCESSFUL)
