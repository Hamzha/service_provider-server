from django.db.models import Q
from authorization.models.user_unavailability import UserUnavailability


def getUserUnavailibilityByUser(user_id):
    try:
        unavailibility_delete_condition = Q(deleted_by__isnull=True)
        unavailibility_user_condition = Q(user=user_id)
        return UserUnavailability.objects.filter(unavailibility_delete_condition & unavailibility_user_condition)
    except UserUnavailability.DoesNotExist:
        return False


def getUserUnavailibilityByID(id):
    unavailibility_delete_condition = Q(deleted_by__isnull=True)
    unavailibility_user_condition = Q(id=id)
    return UserUnavailability.objects.filter(unavailibility_delete_condition & unavailibility_user_condition).first()