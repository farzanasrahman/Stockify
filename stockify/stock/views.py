from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
import pandas as pd
from . models import StockDeposit,StockList
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from . import utils
from django.db import transaction
import numpy as np
from django.http import JsonResponse

# Create your views here.

def stock_fetch(request):
    """
    Fetch stock data and render it in a template.

    :param request: The HTTP request object.
    :return: Rendered template with stock data.
    """
    
    nasdqs = StockList.objects.all()
    tickers = [str(nasdq.symbol) for nasdq in nasdqs]
    
    data = utils.stock_fetch_api(tickers)

    context = {'data': data}

    return render(request, 'stock/stocktable.html', context)
