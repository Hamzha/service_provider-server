from firebase_admin import messaging


def send_push_notification(registration_token,dataObject=None,notificationObj=None):
    message = messaging.MulticastMessage(
        data=dataObject,
        notification=notificationObj,
        tokens=registration_token,
    )
    response = messaging.send_multicast(message)
    return response