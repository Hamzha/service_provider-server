import datetime
from django.shortcuts import redirect,  render
from django import template
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
# from django.contrib.auth.decorators import login_required
from leads.models.job import Job
from django.forms.models import model_to_dict

# from django.utils.timezone import make_aware
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from dashboard.forms.jobs import RegisterJobs
from leads.core.job.read import get_all_jobs


def convertEnumtoState(status):
    if not status:
        return 'NONE'
    return Job.JobState(int(status)).name


# @login_required(login_url="/dashboard/login/")


def jobsList(request):
    context = {}
    try:
        jobsData = []
        data = []
        jobsData = Job.objects.filter(deleted_at__isnull=True).order_by('-id')
        for index in jobsData:
            action = convertEnumtoState(index.state)
            obj = {
                'index': index,
                'action': action,
            }
            data.append(obj)
        context['jobsData'] = data
        html_template = loader.get_template(
            'jobs/jobs.html')
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    # except:
    #     html_template = loader.get_template('home/page-500.html')
    #     return HttpResponse(html_template.render(context, request))


# @login_required(login_url="/dashboard/login/")
# def jobsCreate(request):
#     if request.method == 'POST':
#         form = RegisterJobs(request.POST)
#         if form.is_valid():
#             services = Job(
#                 parent_id=form.cleaned_data["parent_id"],
#                 name=form.cleaned_data["name"],
#                 created_at=datetime.datetime.utcnow()
#             )
#             services.save()
#             return HttpResponseRedirect('/dashboard/service_category/')
#     else:
#         form = RegisterJobs()
#     return render(request, 'service_category/new_service_category.html', {'form': form})

# @login_required(login_url="/dashboard/login/")


def jobsEdit(request, id):
    context = {}
    try:
        jobs = Job.objects.get(id=id)
        jobs = model_to_dict(jobs)
        print('jobs', jobs['state'])
        jobs['state'] = convertEnumtoState(jobs['state'])
        context = {'job': jobs, 'id': id}
        html_template = loader.get_template(
            'jobs/edit_jobs.html')
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))
   # except:
        # html_template = loader.get_template('home/page-500.html')
        # return HttpResponse(html_template.render(context, request))


# @login_required(login_url="/dashboard/login/")
def jobsView(request, id):
    context = {}
    jobs = Job.objects.get(id=id)
    jobs.state = convertEnumtoState(jobs.state)
    context = {'job': jobs, 'id': id}
    html_template = loader.get_template(
        'jobs/view_jobs.html')
    return HttpResponse(html_template.render(context, request))
# @login_required(login_url="/dashboard/login/")


def jobsUpdate(request, id):
    services = Job.objects.get(id=id)
    services_data = request.POST.dict()
    services.name = services_data["name"],
    services.parent_id = services_data['parent_id'],
    services.save()
    return redirect('/dashboard/jobs/')


# @login_required(login_url="/dashboard/login/")
def jobsDelete(request, id):
    services = Job.objects.get(id=id)
    services.deleted_at = datetime.datetime.utcnow()
    services.save()
    return redirect('/dashboard/jobs/')
