import requests
import json
import yfinance as yf
import numpy as np
import pandas as pd
import pandas_datareader as web
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta, date
import base64
from io import BytesIO


def stock_fetch_api(symbols):
    """
    Fetch the stock data for given symbols.

    This function fetches the daily stock data for each symbol in the provided list
    and returns it in a structured format.

    :param symbols: List of stock symbols/tickers to fetch data for.
    :type symbols: list
    :return: A dictionary containing stock data for each symbol.
    :rtype: dict
    """
    stock_data = {}
    for symbol in symbols:
        stock = yf.Ticker(symbol)
        data = stock.history(period='1d')
        stock_data[symbol] = data.to_dict(orient='list')

    processed_data = {}
    for key, val in stock_data.items():
        processed_data[key] = []
        for stk, price in val.items():
            price = round(price[0], 3)
            processed_data[key].append(price)

    return processed_data


def unit_price_fetch(symbol):
    """
    Fetch the unit price of a given stock symbol for the most recent trading day.

    :param symbol: Stock ticker/symbol for which to fetch the unit price.
    :type symbol: str
    :return: Unit price of the stock on the most recent trading day.
    :rtype: float
    """
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d")
    data = data.to_dict(orient='records')
    unit_price = round(data[0]['Open'], 5)
    return unit_price