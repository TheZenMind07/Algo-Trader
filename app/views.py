# -*- encoding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template
from .forms import TradingForm, StockForm, DummyForm
from .algos.connect import *
from .algos.kc_other_apis import *
import json
from .algos.dictfield_copy import *
from django.http import JsonResponse
from .algos.renko_macd_strategy import *
from .algos.square_off import *


@login_required(login_url="/login/")
def index(request):
    print(request.POST)
    context = {}
    context['segment'] = 'index'
    context['form'] = DummyForm()
    context = {
        "daypnl" : False,
        "abspnl" :False,
        "holdings": False,
        "holdingsCount": False,
        "positionsCount" : False,
        'positions' : False
    }

    # if(request.method == 'POST'):
    #     if(request.POST.get('form_type') == "formRefreshIndex"):
    holdings = get_holdings()
    position_list = get_positions()
    positions = position_list['net']
    daypnl = float(0)
    abspnl = float(0)
    holding_value = float(0)
    holding_count = len(holdings)
    position_count = len(positions)
    position_value = float(0)
    for holding in holdings:
        daypnl += float(holding["day_change"])*float(holding["quantity"])
        abspnl += float(holding["pnl"])
        holding_value += float(holding["last_price"])*float(holding["quantity"])
    for position in positions:
        position_value += float(position["value"])
        # print(position["value"])
    context['daypnl'] = round(daypnl,4)
    context['abspnl'] = round(abspnl,4)
    context['holdings'] = round(holding_value,4 )
    context['holdingsCount'] = holding_count
    context['positionsCount'] = position_count
    context['positions'] = position_value
    # print(context)






    html_template = loader.get_template( 'index.html' )   # template loader which searches for index.html in file
    return HttpResponse(html_template.render(context, request)) # render methoda loads the html

@login_required(login_url="/login/")
def pages(request):
    print(request.path)
    holding_list = get_holdings()
    position_list = get_positions()
    context = {
        "holdinglist": False,
        "positionlist" : False
    }
    print(request.POST.get('status'))
    if(request.method == 'POST'):
        if(request.POST.get('form_type') == "formRefreshIndex"):
            zerodhaSession()
        elif(request.POST.get('form_type') == "formTrade"):
            form = TradingForm(request.POST)
            if form.is_valid():
                print(form.cleaned_data)
                strategy = form.cleaned_data['trading_field']
                capital = form.cleaned_data['trading_amount']
                if(strategy == "1" and request.POST.get('status') == "start"):
                    # renko_macd_algo(capital)
                    print("renko")

                elif(request.POST.get('status') == "end"):
                    print("endsession")
                    sqaure_off_positions()

        elif(request.POST.get('form_type') == "formInvest"):
            form = StockForm(request.POST)
            if form.is_valid():
                print(form.cleaned_data)
                if(request.POST.get('action') == "buy"):
                    if(request.POST.get('limit_price') == 0.0):
                        placeMarketOrderLT(form.cleaned_data['nse_code'],"buy", form.cleaned_data['quantity'])
                    else :
                        placeLimitOrderLT(form.cleaned_data['nse_code'],"buy", form.cleaned_data['quantity'], form.cleaned_data['limit_price'])
                elif(request.POST.get('action') == "sell"):
                    if(request.POST.get('limit_price') == 0.0):
                        placeMarketOrderLT(form.cleaned_data['nse_code'],"sell", form.cleaned_data['quantity'])
                    else :
                        placeLimitOrderLT(form.cleaned_data['nse_code'],"sell", form.cleaned_data['quantity'], form.cleaned_data['limit_price'])

    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    if(request.path.split('/')[-1] == "ui-trade.html"):
        context['form'] = TradingForm()
        context["positionlist"] = position_list['net']
        # print(context["positionlist"])

    elif(request.path.split('/')[-1] == "ui-stocks.html"):
        context['form'] = StockForm()
        context["holdinglist"] = holding_list
        # print(context["holdinglist"])

    elif(request.path.split('/')[-1] == "charts-morris.html"):
        chartmfholdings = dictlist_mf(get_mfholdings())
        chartstockholdings = dictlist_stock(get_holdings())
        position_list = get_positions()
        chartpositions = dictlist_position(position_list['net'])
        mf_total = 0
        position_total = 0
        stock_toatl = 0
        # print()
        print(chartpositions)
        for holding in chartstockholdings:
            stock_toatl += holding["value"]
        for position in chartpositions:
            position_total += position["value"]
        for mf in chartmfholdings:
            mf_total += mf["value"]

        summary_dict = [
                        { "label" : "Stock", "value" : stock_toatl },
                        { "label" : "Position", "value" : position_total },
                        { "label" : "Mutual Fund", "value" : mf_total }
                        ]
        if request.is_ajax():
            return JsonResponse({'chartmf': chartmfholdings,
                                 'chartposition' : chartpositions,
                                 'chartholdings': chartstockholdings,
                                 'summarychart' :summary_dict}, status = 200)

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
