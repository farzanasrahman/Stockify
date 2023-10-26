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


@login_required
def buy_stock(request):
    """
    Allows the logged-in user to buy stocks.

    :param request: The HTTP request object.
    :return: Renders the buy stock page with stock details if GET request,
             else, processes the stock purchase and returns to buy stock page.
    """
    context = {}
    response_message = ''
    nasdqs = StockList.objects.all()
    tickers = [str(nasdq.symbol) for nasdq in nasdqs]
    unit_prices = utils.unit_price_fetch('MSFT')

    if request.method == 'POST':
        stock_name = request.POST.get('stock_name')
        amount = int(request.POST.get('amount'))
        unit_price = utils.unit_price_fetch(stock_name)
        total_price = unit_price * amount
        user = request.user

        if user.profile.balance >= total_price:
            with transaction.atomic():
                stock_deposit = StockDeposit(user=request.user,
                                             stock_name=stock_name,
                                             amount=amount,
                                             unit_price=unit_price,
                                             total_price=total_price)
                stock_deposit.save()
                user.profile.adjust_balance(total_price, 'decrement')
            messages.success(request, 'Successfully Purchased!')
            return redirect('buy-stock')
        else:
            response_message = 'Not sufficient Balance!'
            messages.warning(request, response_message)
            return redirect('buy-stock')

    context = {
        'tickers': tickers,
        'unit_prices': unit_prices
    }

    return render(request, 'stock/buy_stock.html', context)
