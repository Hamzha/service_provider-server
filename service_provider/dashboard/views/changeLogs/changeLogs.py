from django import template
from django.template import loader
from django.http import HttpResponse
# from django.contrib.auth.decorators import login_required
from authorization.models.system_changelog import SystemChangelog

# @login_required(login_url="/dashboard/login/")


def convertEnumtoAction(status):
    if not status:
        return 'NONE'
    return SystemChangelog.ActionPerformed(int(status)).name


def convertEnumtoTable(status):
    if not status:
        return 'NONE'
    return SystemChangelog.TableName(int(status)).name


def changeLogs_listing(request):
    context = {}
    try:
        data = []
        changeLogsData = SystemChangelog.objects.all()
        for index in changeLogsData:
            action = convertEnumtoAction(
                index.action_performed)
            table = convertEnumtoTable(index.changed_in)
            obj = {
                'index': index,
                'action': action,
                'table': table
            }
            data.append(obj)
        context['changeLogsData'] = data
        html_template = loader.get_template('change_logs/changeLogs.html')
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))


def changeLogs_view(request, id):
    context = {}
    context['id'] = id
    try:
        # accounts_data = []
        changeLogsData = SystemChangelog.objects.get(id=id)
        action = convertEnumtoAction(
            changeLogsData.action_performed)
        table = convertEnumtoTable(changeLogsData.changed_in)
        obj = {
            'index': changeLogsData,
            'action': action,
            'table': table
        }
        print(f'Obj {obj}')
        context['changeLogsData'] = obj

        html_template = loader.get_template('change_logs/view_changeLogs.html')
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))
