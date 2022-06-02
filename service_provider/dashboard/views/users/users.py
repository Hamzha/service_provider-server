import datetime
from django.shortcuts import redirect, get_object_or_404, render
from django import template
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
# from django.contrib.auth.decorators import login_required
from authorization.models.user import User
from django.forms.models import model_to_dict

# from django.utils.timezone import make_aware
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from authorization.core.user.read import convertEnumtoStatus, convertEnumToGender, convertEnumToType
from django.contrib.auth.hashers import make_password
from dashboard.forms.users import RegisterForm
# @login_required(login_url="/dashboard/login/")


def userList(request):
    context = {}

    try:
        userData = []
        userData = User.objects.all()
        data = []
        for index in userData:
            type = convertEnumToType(index.type)
            status = convertEnumtoStatus(index.status)
            obj = {
                'index': index,
                'status': status,
                'type': type,
            }
            data.append(obj)
        context['usersData'] = data
        print(f'OBJEct ', context['usersData'])
        html_template = loader.get_template('users/users.html')
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))


# @login_required(login_url="/dashboard/login/")
def userCreate(request):
    if request.method == 'POST':
        user_data = request.POST.dict()
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User(
                email=form.cleaned_data["email"],
                password=make_password(form.cleaned_data["password"]),
                type=form.cleaned_data["type"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                # date_of_birth=user_data["date_of_birth"],
                # date_of_birth=make_aware(datetime.datetime.strptime(
                #     dateTime, '%Y-%m-%d %H:%M:%S')),
                gender=form.cleaned_data['gender'],
                phone_number=form.cleaned_data['phone_number'],
                home_address=form.cleaned_data['home_address'],
                street_address=form.cleaned_data['street_address'],
                apartment=form.cleaned_data['apartment'],
                status=form.cleaned_data['status'],
                city=user_data['city'],
                country=user_data['country'],
                state=user_data['state'],
                zipcode=form.cleaned_data['zipcode'])
            user.save()
            return HttpResponseRedirect('/dashboard/user/')
    else:
        form = RegisterForm()
    return render(request, 'users/new_user.html', {'form': form})

# @login_required(login_url="/dashboard/login/")


def userEdit(request, id):
    context = {}
    try:
        user = User.objects.get(id=id)
        user = model_to_dict(user)
        if user['date_of_birth'] is None:
            user['date_of_birth'] = ''
        if user['type'] == 0:
            user['type'] = 'Super Admin'
        user['gender'] = convertEnumToGender(user['gender'])
        user['type'] = convertEnumToType(user['type'])
        user['status'] = convertEnumtoStatus(user['status'])
        context = {'user': user}
        html_template = loader.get_template('users/edit_user.html')
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))


# @login_required(login_url="/dashboard/login/")
def userView(request, id):
    context = {}
    user = User.objects.get(id=id)
    user = model_to_dict(user)
    user['gender'] = convertEnumToGender(user['gender'])
    user['type'] = convertEnumToType(user['type'])
    user['status'] = convertEnumtoStatus(user['status'])
    context = {'user': user}
    html_template = loader.get_template('users/view_user.html')
    return HttpResponse(html_template.render(context, request))
# @login_required(login_url="/dashboard/login/")


def userUpdate(request, id):
    user = User.objects.get(id=id)
    user_data = request.POST.dict()
    user.type = user_data["type"],
    user.status = user_data['status'],
    user.first_name = user_data["first_name"],
    user.last_name = user_data["last_name"],
    user.gender = user_data['gender'],
    user.phone_number = user_data['phone_number'],
    user.home_address = user_data['home_address'],
    user.street_address = user_data['street_address'],
    user.apartment = user_data['apartment'],
    user.zipcode = user_data['zipcode']
    user.save()
    return redirect('/dashboard/user/')


# @login_required(login_url="/dashboard/login/")
def userDelete(request, id):
    user = User.objects.get(id=id)
    user.deleted_at = datetime.datetime.utcnow()
    user.save()
    return redirect('/dashboard/user/')
