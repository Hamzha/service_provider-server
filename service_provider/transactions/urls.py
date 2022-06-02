from django.urls import path
from transactions.views.transaction_view import TransactionView
urlpatterns = [
    path('transaction', TransactionView.as_view()),
]
