# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template
from .forms import TradingForm


@login_required(login_url="/login/")
def index(request):

    context = {}
    context['segment'] = 'index'

    html_template = loader.get_template( 'index.html' )   # template loader which searches for index.html in file
    return HttpResponse(html_template.render(context, request)) # render methoda loads the html

@login_required(login_url="/login/")
def pages(request):
    context = {}
    print(request.POST)
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    if(request.path.split('/')[-1] == "ui-trade.html"):
        context['form'] = TradingForm()
    try:

        load_template      = request.path.split('/')[-1]
        context['segment'] = load_template

        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))

    except:

        html_template = loader.get_template( 'page-500.html' )
        return HttpResponse(html_template.render(context, request))
