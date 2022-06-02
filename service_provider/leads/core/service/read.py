from authorization.models.user import User
from leads.models.service_category import ServiceCategory
from leads.models.service import Service
from django.db.models import Q


def getServiceCategoryByName(name):
    try:
        return ServiceCategory.objects.filter(name=name).first().id
    except:
        return "NONE"


def getServiceCategoryById(id):
    try:
        return ServiceCategory.objects.filter(id=id).first().id
    except:
        return "NONE"

def isServiceAlreadyRegister(id,user):
    try:
        return Service.objects.filter(service_category__id=id,user=user,deleted_by=None)
    except:
        return False

def getServiceStatefromEnum(state):
    return Service.ServiceStatus(state).name


def getEnumFromServieStatus(state):
    try:
        return Service.ServiceStatus[str(state).upper()]
    except:
        return 'NONE'


def getServiceCategoryfromID(service_category_id):
    return ServiceCategory.objects.filter(id=service_category_id).first().name


def serviceExistOrNot(service_id):
    return Service.objects.filter(id=service_id).exists()


def serviceAlreadyDeletedOrNot(service_id):
    condition1 = Q(id=service_id)
    condition2 = Q(deleted_by__isnull=True)
    return Service.objects.filter(condition1 & condition2).exists()


def getServiceByID(service_id):
    condition1 = Q(id=service_id)
    condition2 = Q(deleted_by__isnull=True)
    return Service.objects.filter(condition1 & condition2).first()


def getServiceByCategory(service_category_id):
    condition1 = Q(service_category=service_category_id)
    condition2 = Q(deleted_by__isnull=True)
    return Service.objects.filter(condition1 & condition2)


def getAllServices(user):
    return Service.objects.filter(user=user,deleted_by=None)
