import json
from leads.models.lead import Lead
from django.db.models import Q
from firebase_admin import db

def create_lead_on_firebase(lead_id,client_id,vendor_id,lead_state):
    path='service_messages/'+str(lead_id)
    ref = db.reference(path)
    data={
        'client_id':client_id,
        'vendor_id':vendor_id,
        'messages':None,
        'lead_state':lead_state
    }
    ref.set(data)

def update_lead_status_on_firebase(job_id,job_status):
    path='service_messages/'+str(job_id)
    ref = db.reference(path)
    ref.child('job_state').set(job_status)

def delete_lead_on_firebase(job_id):
    job_id_path='service_messages/'+str(job_id)
    job_id_deleted_path='deleted_service_messages/'+str(job_id)

    # Getting all the messages
    all_message=None
    ref = db.reference(job_id_path)
    all_message=ref.get()

    # Deleting the messages from service_message
    ref = db.reference(job_id_path)
    ref.delete()

    # Keeping the record of message in job_id_deleted_message
    ref = db.reference(job_id_deleted_path)
    ref.set(all_message)
