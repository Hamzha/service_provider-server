
from authorization.models.user import User
import datetime
from django.utils.timezone import make_aware
from django.contrib.auth.hashers import make_password
from configuration import STRIP_API_KEY
import stripe
stripe.api_key=STRIP_API_KEY

def addUser(parameters):
    if 'date_of_birth' in parameters:
        parameters['date_of_birth'] = make_aware(datetime.datetime.strptime(
            parameters.get('date_of_birth'), '%Y-%m-%d %H:%M:%S'))
    user = User.objects.create(**parameters)
    return user


def updateUser(parameters):
    if 'date_of_birth' in parameters:
        parameters['date_of_birth'] = make_aware(datetime.datetime.strptime(
            parameters.get('date_of_birth'), '%Y-%m-%d %H:%M:%S'))
    user = User.objects.filter(email=parameters['email']).update(**parameters)
    return user


def deleteUser(user, user_id):
    User.delete(user, user_id)


def updateUserByEmail(email, parameters):
    User.objects.filter(email=email).update(
        **parameters
    )


def updatePassword(email, password):
    user = User.objects.filter(email=email).first()
    user.password = make_password(password)
    user.save()
    return user

def stripe_create_customer(name,email,phone_number):
    try:
        customer = stripe.Customer.create(
            name=name,
            email=email,
            metadata={
                'phone_number':phone_number,
            }
        )
        return customer
    except:
        return False

