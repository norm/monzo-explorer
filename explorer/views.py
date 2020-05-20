import json
import os

from django.views.generic import RedirectView, TemplateView
from django.http import HttpResponseRedirect

from monzo import MonzoOAuth2Client
from monzo.utils import load_token_from_file

from explorer.settings import (
    MONZO_CLIENT_KEY,
    MONZO_SECRET_KEY,
    MONZO_REDIRECT_URL,
)
from apps.monzo.models import Transaction


class Home(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if os.path.isfile('monzo.json'):
            context['authenticated'] = True
            context['recent_transactions'] = Transaction.objects.all()
        else:
            context['authenticated'] = False
            oauth_client = MonzoOAuth2Client(
                MONZO_CLIENT_KEY,
                MONZO_SECRET_KEY,
                redirect_uri = MONZO_REDIRECT_URL,
            )
            context['oauth_url'] = oauth_client.authorize_token_url()[0]
        return context


class Callback(RedirectView):
    template_name = 'callback.html'

    def get(self, *args, **kwargs):
        code = self.request.GET['code']
        if code is None:
            return HttpResponseRedirect('/')
        oauth_client = MonzoOAuth2Client(
            MONZO_CLIENT_KEY,
            MONZO_SECRET_KEY,
            redirect_uri = MONZO_REDIRECT_URL,
        )
        oauth_client.fetch_access_token(code)
        
        # fix the monzo.json file
        token = load_token_from_file(r'monzo.json')
        token['client_secret'] = code
        with open('monzo.json', 'w') as token_file:
            json.dump(token, token_file)

        return HttpResponseRedirect('/')
