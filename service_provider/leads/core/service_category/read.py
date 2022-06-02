from leads.models.service_category import ServiceCategory
from django.db.models import Q


def getAllServiceCategories(parent_id=None):
    if parent_id:
        return ServiceCategory.objects.filter(deleted_by__isnull=True,parent_id=parent_id).order_by('id')
    else:
        return ServiceCategory.objects.filter(deleted_by__isnull=True).order_by('id')


def getServiceCategory(service_category):
    final = {}
    for tmp in service_category:
        if(tmp.parent_id == 0):
            final[tmp.name] = list(service_category.filter(
                Q(parent_id=tmp.id)
            ).values_list('name', 'id'))

    return final


def getServiceCategoryById(id):
    return ServiceCategory.objects.filter(id=id).first()
