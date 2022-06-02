from authorization.models.account import Account


def get_all_accounts(user_id):
    return Account.objects.filter(user=user_id, deleted_by=None)


def get_account(account_id, user_id):
    try:
        account_detail = Account.objects.get(
            pk=account_id, user=user_id, deleted_by=None)
        return account_detail
    except Account.DoesNotExist:
        return False


def get_lazzy_deleted_account(card_number_hashed, user_id):
    try:
        account_detail = Account.objects.get(
            card_number_hashed=card_number_hashed,
            user=user_id,
            deleted_by__isnull=False)
        return account_detail
    except Account.DoesNotExist:
        return False

def get_account_by_user_id(user_id):
    try:
        account_detail = Account.objects.get(user=user_id, deleted_by=None)
        return account_detail
    except Account.DoesNotExist:
        return False