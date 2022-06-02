from django import template
from django.forms import model_to_dict
from django.template import loader
from django.http import HttpResponse
from django.db.models import Q
# from django.contrib.auth.decorators import login_required
from transactions.models.transaction import Transaction
from authorization.models.account import Account
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# @login_required(login_url="/dashboard/login/")
def account_listing(request, user_id):
    context = {}
    context['id'] = user_id
    try:
        # accounts_data = []
        accounts_data = Account.objects.filter(Q(user__id=user_id))
        paginator = Paginator(accounts_data, len(accounts_data))
        page = request.GET.get('page')
        if accounts_data:
            try:
                accounts_data = paginator.page(page)
            except PageNotAnInteger:
                accounts_data = paginator.page(1)
            except EmptyPage:
                accounts_data = paginator.page(paginator.num_pages)
            context['accountsData'] = accounts_data
        else:
            context['accountsData'] = {}
        html_template = loader.get_template('card_accounts/accounts.html')
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))


def account_view(request, account_id):
    context = {}
    context['id'] = account_id
    try:
        # accounts_data = []
        account_data = Account.objects.get(id=account_id)
        if account_data:
            context['accountData'] = account_data
        else:
            context['accountData'] = {}
        logger.debug('context 2=>', model_to_dict(context['accountData']))
        
        html_template = loader.get_template('card_accounts/view_account.html')
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))
