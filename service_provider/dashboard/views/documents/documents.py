import datetime
from django.shortcuts import redirect,  render
from django import template
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
# from django.contrib.auth.decorators import login_required
from leads.models.job import Job
from django.forms.models import model_to_dict

from dashboard.forms.jobs import RegisterJobs
from authorization.models.configuration import Configuration

# @login_required(login_url="/dashboard/login/")


def configList(request):
    context = {}
    try:
        configData = []
        configData = Configuration.objects.all()
        context['configData'] = configData
        print(f'configData { configData }')
        html_template = loader.get_template(
            'configuration/config.html')
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    # except:
    #     html_template = loader.get_template('home/page-500.html')
    #     return HttpResponse(html_template.render(context, request))


# @login_required(login_url="/dashboard/login/")


def configEdit(request, id):
    context = {}
    try:
        config = Configuration.objects.get(id=id)
        context = {'config': config, 'id': id}
        html_template = loader.get_template(
            'configuration/edit_config.html')
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))
   # except:
        # html_template = loader.get_template('home/page-500.html')
        # return HttpResponse(html_template.render(context, request))


# @login_required(login_url="/dashboard/login/")
def configView(request, id):
    context = {}
    config = Configuration.objects.get(id=id)
    context = {'config': config, 'id': id}
    html_template = loader.get_template(
        'configuration/view_config.html')
    return HttpResponse(html_template.render(context, request))
# @login_required(login_url="/dashboard/login/")


def configUpdate(request, id):
    services = Job.objects.get(id=id)
    services_data = request.POST.dict()
    services.name = services_data["name"],
    services.parent_id = services_data['parent_id'],
    services.save()
    return redirect('/dashboard/jobs/')
