from django import template
from django.template import loader
from django.http import HttpResponse
from django.db.models import Q
# from django.contrib.auth.decorators import login_required
from transactions.models.transaction import Transaction

# from django.utils.timezone import make_aware
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# @login_required(login_url="/dashboard/login/")
def transaction_listing(request, user_id):
    context = {}
    context['id'] = user_id
    try:
        # transactions_data = []
        transactions_data = Transaction.objects.filter(
            Q(lead__client__id=user_id) | Q(lead__vendor__id=user_id))
        paginator = Paginator(transactions_data, len(transactions_data))
        page = request.GET.get('page')
        if transactions_data:
            try:
                transactions_data = paginator.page(page)
            except PageNotAnInteger:
                transactions_data = paginator.page(1)
            except EmptyPage:
                transactions_data = paginator.page(paginator.num_pages)
            context['transactions_data'] = transactions_data
        else:
            context['transactions_data'] = {'err': 'No Data Found'}
        html_template = loader.get_template('transactions/transactions.html')
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

# @login_required(login_url="/dashboard/login/")


def transaction_view(request, transaction_id):
    context = {}
    context['id'] = transaction_id
    try:
        # transactions_data = []
        transactions_data = Transaction.objects.filter(
            Q(lead__client__id=transaction_id) | Q(lead__vendor__id=transaction_id))
        paginator = Paginator(transactions_data, len(transactions_data))
        page = request.GET.get('page')
        if transactions_data:
            try:
                transactions_data = paginator.page(page)
            except PageNotAnInteger:
                transactions_data = paginator.page(1)
            except EmptyPage:
                transactions_data = paginator.page(paginator.num_pages)
            context['transactions_data'] = transactions_data
        else:
            context['transactions_data'] = {'err': 'No Data Found'}
        html_template = loader.get_template(
            'transactions/transactionsDetails.html')
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    # except:
    #     html_template = loader.get_template('home/page-500.html')
    #     return HttpResponse(html_template.render(context, request))
