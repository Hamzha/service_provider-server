# Signal to send email after password reset
from django_rest_passwordreset.signals import reset_password_token_created
from django.dispatch import receiver
from django.core.mail import send_mail  
@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    email_plaintext_message = "%s is your code to reset password. Please do not share it with anyone." % str(reset_password_token.key)
    send_mail(
        # title:
        "Password Reset for {title}".format(title="Visualshop"),
        # message:
        email_plaintext_message,
        # from:
        "noreply@visualshop.local",
        # to:
        [reset_password_token.user.email]
    )
