import datetime
from authorization.models.location import Location
from django.forms.models import model_to_dict


def deleteLocation(user, user_id):
    tmp = Location.objects.filter(user=user.id).update(
        deleted_by=user_id,
        deleted_at=datetime.datetime.utcnow()
    )
    if tmp:
        return True
    else:
        return False


def updateLocation(user, updated_by, lat, lng):
    tmp = Location.objects.filter(user=user.id).update(
        updated_by=updated_by,
        updated_at=datetime.datetime.utcnow(),
        lat=lat,
        lng=lng,
        deleted_by=None,
        deleted_at=None
    )
    if tmp:
        return True
    else:
        return False
