from django.conf.urls.defaults import url
from surlex import Surlex

def surl(surlex, *args, **kwargs):
    return url(Surlex(surlex).translate(), *args, **kwargs)
