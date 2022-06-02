from django.db.models import Q
from authorization.models.user_unavailability import UserUnavailability
from django.utils import timezone

def updateUserUnavailability(id, params):
    unavailibility_delete_condition = Q(deleted_by__isnull=True)
    unavailibility_user_condition = Q(id=id)
    return UserUnavailability.objects.filter(
        unavailibility_delete_condition & unavailibility_user_condition).update(**params)

def deleteUserUnavailability(user_id,unavailability_id=None):
    if unavailability_id:
        try:
            data=UserUnavailability.objects.get(id=unavailability_id,user__id=user_id,deleted_by=None)
            data.delete(user_id)
            return data
        except UserUnavailability.DoesNotExist:
            return False
    else:
        results=UserUnavailability.objects.filter(user__id=user_id,deleted_by=None)
        deleted_at = timezone.now()
        for result in results:
            result.deleted_at=deleted_at
            result.deleted_by=user_id
        UserUnavailability.objects.bulk_update(results,['deleted_at','deleted_by'])
        return results
