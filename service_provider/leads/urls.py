from unicodedata import name
from django.urls import path
from rest_framework_simplejwt import views as jwt_views
# from authorization.views import HelloViews
from leads.views.service_category import ServiceCategoryView
from leads.views.service import Service
from leads.views.job_view import JobView
from leads.views.lead import LeadViews
from leads.views.rating_view import RatingView
from leads.views.rating_response_view import RatingResponseView

urlpatterns = [
    path('service_category', ServiceCategoryView.as_view()),
    path('service', Service.as_view()),
    path('job',JobView.as_view()),
    path('lead', LeadViews.as_view()),
    path('rating', RatingView.as_view()),
    path('rating_response',RatingResponseView.as_view()),
]
