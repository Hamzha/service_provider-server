from django.urls import path,include
from rest_framework_simplejwt import views as jwt_views
# from authorization.views import HelloViews
from authorization.views.location_view import LocationView
from authorization.views.user_view import UserView
from authorization.views.user_registration_view import UserRegistrationView
from authorization.views.document_view import DocumentView
from authorization.views.account_view import AccountView
from authorization.views.user_unavailability_view import UserUnavailabilityView
from authorization.views.otp_view import OtpGenerateView, OtpValidateView
from authorization.views.user_device_view import UserDecideView
from authorization.views.vendor_search import VendorSearchView
from authorization.views.configuration import ConfigurationView
from authorization.views.firebase_auth import FirebaseAuthView
from authorization.views.user_phone_email_validate_view import UserPhoneEmailvalidate
from authorization.views.signals.password_reset import password_reset_token_created

urlpatterns = [
    path('token/', jwt_views.TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(),
         name='token_refresh'),
    path('firebase-token/', FirebaseAuthView.as_view(),
         name='firebase-auth-view'),

    # ====== Location CRUD ======
    path('location', LocationView.as_view(), name='location'),

    # ====== User CRUD ======
    path('user', UserView.as_view()),

    # ====== User Registration ======
    path('register', UserRegistrationView.as_view()),

    # ====== Reset Password ======
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),


    # ====== Documenttion CRUD ======
    path('document', DocumentView.as_view()),

    # ====== User Unavailability ======
    path('user_unavailibility', UserUnavailabilityView.as_view()),

    # ====== Accounts CRUDS ======
    path('account', AccountView.as_view()),

    # ===== otp cruds =====
    path('otp_generate', OtpGenerateView.as_view()),
    path('otp_validate', OtpValidateView.as_view()),

    # ===== User Device CRUDS ======
    path('user_device', UserDecideView.as_view()),

    # ====== Vendor serach ======
    path('vendor_search', VendorSearchView.as_view()),
    #     path('reset_password', update.UpdatePasswordView.as_view(), name='update-password')

    # ===== configuration CRUDS ======
    path('configuration', ConfigurationView.as_view()),

     # ====== validate email and username ======
     path('vaildate_email_phone', UserPhoneEmailvalidate.as_view()),

]