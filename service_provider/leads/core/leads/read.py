from leads.models.lead import Lead
from django.db.models import Q


def getLeadByVendor(id):
    return Lead.objects.filter(vendor=id)


def get_leads(user_id):
    filter_by_user = Q(
        Q(vendor=user_id) |
        Q(client=user_id)
    )
    return Lead.objects.filter(filter_by_user).order_by('-created_at')


def get_lead_by_id(id, user_id):
    try:
        filter_by_user = Q(
            Q(vendor=user_id) |
            Q(client=user_id)
        )
        id_filter = Q(id=id)
        return Lead.objects.get(id_filter, filter_by_user)
    except Lead.DoesNotExist:
        return False


def get_lead_by_only_id(id):
    try:
        return Lead.objects.get(id = id)
    except Lead.DoesNotExist:
        return False


def get_pending_lead(user_id):
    filter_by_user = Q(
        Q(vendor=user_id) |
        Q(client=user_id)
    )
    status = Q(
        state=Lead.LeadState.PENDING
    )
    return Lead.objects.filter(filter_by_user, status).order_by('-created_at')


def get_lead_external_value(state):
    return Lead.LeadState(state).name


def get_lead_internal_value(state):
    try:
        return Lead.LeadState[str(state).upper()]
    except:
        return 'NONE'
