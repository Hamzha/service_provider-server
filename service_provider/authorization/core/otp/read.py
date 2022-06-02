from authorization.models.otp import Otp


def get_otp(otp, email):
    result = Otp.objects.filter(email=email).order_by('-id')
    if result:
        latest_otp = result[0]
        if latest_otp.deleted_at != None:
            return False
        if latest_otp.otp == otp: # otp matched
            return latest_otp
        else: # otp did not matched
            return False
    else: # otp not found
        return False
