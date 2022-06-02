import json
from leads.models.lead import Lead
from django.db.models import Q
from firebase_admin import db

def delete_job(id, authenticated_user_id):
    try:
        lead = Lead.objects.get(Q(deleted_by=None, job__deleted_by=None, job__id=id), Q(
            client=authenticated_user_id) | Q(vendor=authenticated_user_id))
        job = lead.job
        if job:
            job.delete(authenticated_user_id)
            return lead
        else:
            False
    except Lead.DoesNotExist:
        return False
