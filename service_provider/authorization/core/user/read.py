from authorization.models.user import User
import datetime
from django.db.models import Q


def checkEmailAvailability(email):
    user_delete_condition = Q(deleted_by__isnull=True)
    user_email_condition = Q(email=email)

    return User.objects.filter(user_delete_condition & user_email_condition).exists()


def checkDateTimeFormat(date_time):
    try:
        datetime.datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
        return False
    except ValueError:
        return True


def getUserById(id):
    return User.objects.filter(id=id).first()


def getUserByEmail(email):
    return User.objects.filter(
        email=email).first()


def checkUserdelete(user):
    if user.deleted_by:
        return True
    else:
        return False


def getUserByEmail(email):
    return User.objects.filter(email=email).first()


def getUserByPhoneNumber(phone_number):
    return User.objects.filter(phone_number=phone_number).first()


def convertStatusToEnum(status):
    return User.UserStatus[str(status).upper()]


def convertEnumtoStatus(status):
    if not status:
        return 'NONE'
    return User.UserStatus(int(status)).name


def convertGenderToEnum(gender):
    return User.UserGender[str(gender).upper()]


def convertEnumToGender(gender):
    return User.UserGender(gender).name


def convertTypeToEnum(type):
    return User.UserType[str(type).upper()]


def convertEnumToType(type):
    if not type:
        return 'NONE'
    return User.UserType(type).name


def getParameters():
    return ['email', 'first_name', 'last_name', 'date_of_birth', 'phone_number',
                     'type', 'status', 'gender', 'home_address', 'street_address', 'apartment',
                     'city', 'state', 'zipcode', 'country', 'password']
