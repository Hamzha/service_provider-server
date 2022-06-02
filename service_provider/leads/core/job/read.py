from django.db.models import Q
from leads.models.lead import Lead
from leads.models.job import Job


def get_lead(id, authenticated_user_id):
    try:
        return Lead.objects.get(Q(pk=id), Q(
            client=authenticated_user_id) | Q(vendor=authenticated_user_id))
    except Lead.DoesNotExist:
        return False


# Getting jobs from lead model based on client or vendor id
def get_all_jobs(authenticated_user_id,state=None):
    basic_filter=Q(deleted_by=None, job__deleted_by=None)
    filter_by_user=Q(Q(client=authenticated_user_id) | Q(vendor=authenticated_user_id))
    jobs = []
    leads = Lead.objects.filter(basic_filter,filter_by_user)
    for lead in leads:
        if state:
            if lead.job and lead.job.state==state:
                jobs.append(lead.job)
                
        else:
            if lead.job:
                jobs.append(lead.job)
    return jobs


def get_job_by_job_id(id, authenticated_user_id):
    try:
        job_detail = Lead.objects.get(Q(deleted_by=None, job__deleted_by=None, job__id=id), Q(
            client=authenticated_user_id) | Q(vendor=authenticated_user_id))
        job = job_detail.job
        if job:
            return job
        else:
            False
    except Lead.DoesNotExist:
        return False


def get_job_by_lead_id(id, authenticated_user_id):
    try:
        job_detail = Lead.objects.get(Q(deleted_by=None, job__deleted_by=None, id=id), Q(
            client=authenticated_user_id) | Q(vendor=authenticated_user_id))
        job = job_detail.job
        if job:
            return job
        else:
            return False
    except Lead.DoesNotExist:
        return False


def get_job_by_date(
        authenticated_user_id,
        end_datetime=None,
        start_datetime=None,
        state=None):
    jobs = []

    if end_datetime and start_datetime:
        leads = Lead.objects.filter(Q(deleted_by=None,
                                      job__deleted_by=None,
                                      job__start_datetime__year__gte=start_datetime.year,
                                      job__start_datetime__month__gte=start_datetime.month,
                                      job__start_datetime__day__gte=start_datetime.day,
                                      job__end_datetime__year__lte=end_datetime.year,
                                      job__end_datetime__month__lte=end_datetime.month,
                                      job__end_datetime__day__lte=end_datetime.day),
                                    Q(client=authenticated_user_id) | Q(vendor=authenticated_user_id))
    if end_datetime:
        leads = Lead.objects.filter(Q(deleted_by=None,
                                      job__deleted_by=None,
                                      job__end_datetime__year=end_datetime.year,
                                      job__end_datetime__month=end_datetime.month,
                                      job__end_datetime__day=end_datetime.day),
                                    Q(client=authenticated_user_id) | Q(vendor=authenticated_user_id))
    else:
        leads = Lead.objects.filter(Q(deleted_by=None,
                                      job__deleted_by=None,
                                      job__start_datetime__year=start_datetime.year,
                                      job__start_datetime__month=start_datetime.month,
                                      job__start_datetime__day=start_datetime.day),
                                    Q(client=authenticated_user_id) | Q(vendor=authenticated_user_id))

    for lead in leads:
        if state:
            if lead.job and  lead.job.state==state:
                jobs.append(lead.job)
        else:
            if lead.job:
                jobs.append(lead.job)
    return jobs


def get_job_state_internal_value(state):
    try:
        print(str(state).upper())
        return Job.JobState[str(state).upper()]
    except BaseException:
        return 'NONE'


def get_job_state_display_value(state):
    try:
        return Job.JobState(state).name
    except BaseException:
        return 'NONE'
