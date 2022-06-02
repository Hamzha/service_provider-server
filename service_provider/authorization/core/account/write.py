from authorization.models.account import Account
import stripe
from configuration import STRIP_API_KEY
import stripe
stripe.api_key=STRIP_API_KEY

def delete_account(account_id, userId):
    try:
        account=Account.objects.get(
            pk=account_id,
            user=userId,
            deleted_by=None)
        account.delete(userId)
        return account
    except Account.DoesNotExist:
        return False
