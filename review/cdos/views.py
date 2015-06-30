from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render, render_to_response

# Create your views here.
from django.template import RequestContext
from cdos.client import Client


def home(request):
    client = Client(settings.CAS_SETTINGS["client_id"],
                    settings.CAS_SETTINGS["client_secret"],
                    settings.SIGNIN_BACK,
                    settings.CAS_SETTINGS["authorization_uri"],
                    settings.CAS_SETTINGS["token_uri"],
                    settings.CAS_SETTINGS["openid_uri"],
                    settings.CAS_SETTINGS["user_api_uri"])
    uri = client.get_authorization_code_uri(scope="get_user_info get_user_group")
    return render_to_response('home.html', {"uri": uri, "CBS_URL": settings.CBS_URL}, context_instance=RequestContext(request))
