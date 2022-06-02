import datetime
from authorization.models.location import Location
from django.db.models import Q


def getLocationByUser(user):
    condition1 = Q(user=user)
    condition2 = Q(deleted_by=None)
    return Location.objects.filter(condition1 & condition2).first()

def getLocationById(id):
    condition1 = Q(id=id)
    condition2 = Q(deleted_by=None)
    return Location.objects.filter(condition1 & condition2).first()
def checkLocationDelete(location):
    if location.deleted_by:
        return True
    else:
        return False
