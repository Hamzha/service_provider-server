import datetime
from django.shortcuts import redirect, get_object_or_404, render
from django import template
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
# from django.contrib.auth.decorators import login_required
from leads.models.service_category import ServiceCategory
from django.forms.models import model_to_dict

# from django.utils.timezone import make_aware
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.hashers import make_password
from dashboard.forms.service_category import RegisterServiceCategory
# @login_required(login_url="/dashboard/login/")


def serviceCategoryList(request):
    context = {}
    try:
        servicesData = []
        servicesData = ServiceCategory.objects.filter(
            deleted_at__isnull=True).order_by('-id')
        # paginator = Paginator(servicesData, len(servicesData))
        # page = request.GET.get('page')
        # print(f'Page {page} request==> {request}')
        # try:
        #     servicesData = paginator.page(page)
        # except PageNotAnInteger:
        #     servicesData = paginator.page(1)
        # except EmptyPage:
        #     servicesData = paginator.page(paginator.num_pages)
        context['servicesData'] = servicesData
        html_template = loader.get_template(
            'service_category/service_category.html')
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    # except:
    #     html_template = loader.get_template('home/page-500.html')
    #     return HttpResponse(html_template.render(context, request))


# @login_required(login_url="/dashboard/login/")
def serviceCategoryCreate(request):
    if request.method == 'POST':
        form = RegisterServiceCategory(request.POST)
        if form.is_valid():
            services = ServiceCategory(
                parent_id=form.cleaned_data["parent_id"],
                name=form.cleaned_data["name"],
                created_at=datetime.datetime.utcnow()
            )
            services.save()
            return HttpResponseRedirect('/dashboard/service_category/')
    else:
        form = RegisterServiceCategory()
    return render(request, 'service_category/new_service_category.html', {'form': form})

# @login_required(login_url="/dashboard/login/")


def serviceCategoryEdit(request, id):
    context = {}
    try:
        services = ServiceCategory.objects.get(id=id)
        services = model_to_dict(services)
        context = {'services': services, 'id': id}
        html_template = loader.get_template(
            'service_category/edit_service_category.html')
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))
   # except:
        # html_template = loader.get_template('home/page-500.html')
        # return HttpResponse(html_template.render(context, request))


# @login_required(login_url="/dashboard/login/")
def serviceCategoryView(request, id):
    context = {}
    services = ServiceCategory.objects.get(id=id)
    services = model_to_dict(services)
    context = {'services': services, 'id': id}
    html_template = loader.get_template(
        'service_category/view_service_category.html')
    return HttpResponse(html_template.render(context, request))
# @login_required(login_url="/dashboard/login/")


def serviceCategoryUpdate(request, id):
    services = ServiceCategory.objects.get(id=id)
    services_data = request.POST.dict()
    services.name = services_data["name"],
    services.parent_id = services_data['parent_id'],

    services.save()
    return redirect('/dashboard/service_category/')


# @login_required(login_url="/dashboard/login/")
def serviceCategoryDelete(request, id):
    services = ServiceCategory.objects.get(id=id)
    services.deleted_at = datetime.datetime.utcnow()
    services.save()
    return redirect('/dashboard/service_category/')
