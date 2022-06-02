from transactions.models.transaction import Transaction
from django.db.models import Q

def get_transaction(transaction_id,authenticated_user_id):
    try:
        account_detail = Transaction.objects.get(
            Q(pk=transaction_id, deleted_by=None),Q(Q(
            lead__client__id=authenticated_user_id) | Q(lead__vendor__id=authenticated_user_id)))
        return account_detail
    except Transaction.DoesNotExist:
        return False


def get_all_transaction(authenticated_user_id,type=None):
    if type:
        return Transaction.objects.filter(Q(deleted_by=None,type=type),Q(Q(
            lead__client__id=authenticated_user_id) | Q(lead__vendor__id=authenticated_user_id)))
    else:
        return Transaction.objects.filter(Q(deleted_by=None),Q(Q(
            lead__client__id=authenticated_user_id) | Q(lead__vendor__id=authenticated_user_id)))

def get_transaction_type_internal_value(state):
    try:
        return Transaction.TransactionType[str(state).upper()]
    except:
        return 'NONE'

def get_transaction_type_display_value(state):
    try:
        return Transaction.TransactionType(state).name
    except:
        return 'NONE'
