from transactions.models.transaction import Transaction


def delete_transaction(transaction_id, userId):
    try:
        Transaction.objects.get(
            pk=transaction_id,
            deleted_by=None).delete(userId)
        return True
    except Transaction.DoesNotExist:
        return False
