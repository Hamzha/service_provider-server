from authorization.models.user_device import UserDevice
from django.db.models import Q


def getUserDeviceByID(id):
    delete_condition = Q(deleted_by__isnull=True)
    id_condition = Q(id=id)
    return UserDevice.objects.filter(delete_condition & id_condition).first()

def getUserDeviceByUser(user):
    delete_condition = Q(deleted_by__isnull=True)
    user_condition = Q(user=user)
    return UserDevice.objects.filter(delete_condition & user_condition)


def getUserDeviceByUserList(users):
    delete_condition = Q(deleted_by__isnull=True)
    user_condition = Q(user__in=users)
    return UserDevice.objects.filter(delete_condition & user_condition)

def getUserDeviceByIdentifier(device_identifier,user):
    delete_condition = Q(deleted_by__isnull=True)
    device_id_condition = Q(identifier=device_identifier)
    user_id_condition = Q(user=user)
    return UserDevice.objects.filter(delete_condition & device_id_condition & user_id_condition)
    