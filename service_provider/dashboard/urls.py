from django.urls import path
from dashboard.views.views import login_view,  index, pages
from dashboard.views.users.users import userList, userCreate, userEdit, userUpdate, userView, userDelete
from dashboard.views.transactions.transactions import transaction_listing, transaction_view
from dashboard.views.accounts.accounts import account_listing, account_view
from dashboard.views.services_category.services_category import serviceCategoryList, serviceCategoryCreate, serviceCategoryEdit, serviceCategoryView, serviceCategoryUpdate, serviceCategoryDelete
from dashboard.views.jobs.jobs import jobsList, jobsEdit, jobsView, jobsUpdate, jobsDelete
from dashboard.views.changeLogs.changeLogs import changeLogs_listing, changeLogs_view
from django.contrib.auth.views import LogoutView

from dashboard.views.configurations.config import configList, configView, configEdit, configUpdate
urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', login_view, name="register"),
    # users URLS start
    path('user/view/transactions/<user_id>/',
         transaction_listing, name="viewUserTransactions"),
    path('user/view/transactions/<transaction_id>/',
         transaction_view, name="viewTransaction"),
    path('user/view/accounts/<user_id>/',
         account_listing, name="viewUserAccount"),
    path('user/view/account/<account_id>/',
         account_view, name="viewAccount"),
    path('user/', userList, name="listingUser"),
    path('user/create/', userCreate, name="createUser"),
    path('user/edit/<id>/', userEdit, name="editUser"),
    path('user/view/<id>/', userView, name="viewUser"),
    path('user/update/<id>/', userUpdate, name="updateUser"),
    path('user/delete/<id>/', userDelete, name="userDelete"),
    # users URLS End
    # Service Category URLS Start
    path('service_category/', serviceCategoryList,
         name="listingServiceCategory"),
    path('service_category/create/', serviceCategoryCreate,
         name="createServiceCategory"),
    path('service_category/edit/<id>/',
         serviceCategoryEdit, name="editServiceCategory"),
    path('service_category/view/<id>/',
         serviceCategoryView, name="viewServiceCategory"),
    path('service_category/update/<id>/',
         serviceCategoryUpdate, name="updateServiceCategory"),
    path('service_category/delete/<id>/',
         serviceCategoryDelete, name="deleteServiceCategory"),
    # Service Category URLS End
    # Service Category URLS Start
    path('services/', serviceCategoryList,
         name="listingServices"),
    path('services/create/', serviceCategoryCreate,
         name="createServiceCategory"),
    path('services/edit/<id>/',
         serviceCategoryEdit, name="editServices"),
    path('services/view/<id>/',
         serviceCategoryView, name="viewServices"),
    path('services/update/<id>/',
         serviceCategoryUpdate, name="updateServices"),
    path('services/delete/<id>/',
         serviceCategoryDelete, name="deleteServices"),
    # Service Category URLS End
    # Jobs URLS Start
    path('jobs/', jobsList,
         name="listingJobs"),
    #     path('jobs/create/', jobsCreate,
    #          name="createJobs"),
    #     path('jobs/edit/<id>/',
    #          jobsEdit, name="editJobs"),
    path('jobs/view/<id>/',
         jobsView, name="viewJobs"),
    #     path('jobs/update/<id>/',
    #          jobsUpdate, name="updateJobs"),
    path('jobs/delete/<id>/',
         jobsDelete, name="deleteJobs"),
    # Jobs URLS End
    # Chage Logs URLS Start
    path('change-logs/', changeLogs_listing,
         name="listingChangeLogs"),

    path('change-logs/<id>/',
         changeLogs_view, name="viewChangeLogs"),
    # Jobs URLS End
    # Leads URLS Start
    #     path('leads/', jobsList,
    #          name="listingLeads"),
    #     path('leads/create/', jobsCreate,
    #          name="createLeads"),
    #     path('leads/edit/<id>/',
    #          jobsEdit, name="editLeads"),
    #     path('leads/view/<id>/',
    #          jobsView, name="viewLeads"),
    #     path('leads/update/<id>/',
    #          jobsUpdate, name="updateLeads"),
    #     path('leads/delete/<id>/',
    #          jobsDelete, name="deleteLeads"),
    # Leads URLS End
    # Configurations URLS Start
    path('config/', configList,
         name="listingConfig"),

    path('config/edit/<id>/',
         configEdit, name="editConfig"),
    path('config/view/<id>/',
         configView, name="viewConfig"),
    path('config/update/<id>/', configUpdate, name="updateConfig"),
    # Configuration URLS End
    # Leads URLS Start
    path('documents/', jobsList,
         name="listingLeads"),
    path('documents/view/<id>/',
         jobsView, name="viewLeads"),
    path('documents/update/<id>/',
         jobsUpdate, name="updateLeads"),
    path('documents/delete/<id>/',
         jobsDelete, name="deleteLeads"),
    # Leads URLS End
    path("logout/", LogoutView.as_view(), name="logout"),
    path('', index, name='home'),
    #     re_path(r'^.*\.*', pages, name='pages'),
]
