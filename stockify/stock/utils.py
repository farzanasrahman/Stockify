import requests
import json
import math
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


def get_predictions(symbol,date_end):
    """
    Generate stock price predictions using an LSTM model.

    This function fetches historical stock prices, constructs and trains an LSTM model,
    and predicts the closing stock price of a company for a given day, using data up to
    the date specified.

    Parameters
    ----------
    symbol : str
        The stock ticker symbol (as used in stock market exchanges) 
        for which predictions are to be made.
    date_end : str
        End date for the historical data period, in 'YYYY-MM-DD' format.

    Returns
    -------
    tuple
        A tuple containing three elements:
        
        - `valid` (pd.DataFrame): Actual stock prices from `training_data_len` onwards.
        - `train` (pd.DataFrame): The training data up until `training_data_len`.
        - `pred_price` (np.array): Predicted stock price for the next day.

    Notes
    -----
    The function uses the stock data from Yahoo Finance, scales it using a MinMax Scaler, 
    and prepares it for training the LSTM (Long Short-Term Memory) model. The model is trained 
    with the historical closing prices of the stock and uses it to make future predictions.

    The model architecture consists of two LSTM layers followed by two Dense layers. It uses 
    'adam' optimizer and mean squared error loss function for the training process.

    Examples
    --------
    >>> valid, train, pred_price = get_predictions("AAPL", "2020-12-31")
    >>> print(pred_price)
    [[300.1234]]
    """

    start_date = '2012-01-01'
    end_date = date_end

    # Get the stock quote
    df = yf.download(symbol, start=start_date, end=end_date)
    

    #Create a new Dataframe with only 'Close' column
    data = df.filter(['Close'])
    #Convert the dataframe to a numpy array
    dataset = data.values
    #Get the number of rows to train the model on
    training_data_len = math.ceil(len(dataset) *0.80)
    # Scaling the data in between the range(0,1)

    scaler = MinMaxScaler(feature_range=(0,1))
    scaled_data = scaler.fit_transform(dataset)

    #Create training data set
    # Create the scaled trained dataset
    train_data = scaled_data[0:training_data_len, :]
    #Split the data into x_train and y_train datasets
    x_train = []
    y_train = []
    for i in range(60,len(train_data)):
        x_train.append(train_data[i-60:i, 0])
        y_train.append(train_data[i,0])
        if i<=60:
            #print(x_train)
            #print(y_train)
            print()

    #Convert the x_train and y_train to numpy arrays 
    x_train , y_train = np.array(x_train), np.array(y_train) # type: ignore
    #Reshape the data
    x_train = np.reshape(x_train,(x_train.shape[0],x_train.shape[1],1))
    #print(x_train.shape)

    #Build the LSTM Model
    model = Sequential()
    model.add(LSTM(50,return_sequences=True,input_shape=(x_train.shape[1],1)))
    model.add(LSTM(50,return_sequences=False))
    model.add(Dense(25))
    model.add(Dense(1))

    model.compile(optimizer='adam', loss ='mean_squared_error')

    #Train the model
    model.fit(x_train,y_train, batch_size =1, epochs =1)

    #Create testing data set
    #Create a new array containing scaled values from index 1543-2002
    test_data = scaled_data[training_data_len -60: , : ]
    #Create the dataset x_test and y_test
    x_test = []
    y_test = dataset[training_data_len:, : ]
    for i in range(60,len(test_data)):
        x_test.append(test_data[i-60:i,0])

    #Convert the data to a numpy array
    x_test = np.array(x_test)

    #Reshape the data
    x_test = np.reshape(x_test, (x_test.shape[0],x_test.shape[1],1))

    #Get the models predicted proce values 
    predictions = model.predict(x_test)
    predictions = scaler.inverse_transform(predictions) #Unscaling the value

    #Plot the data
    train =data[:training_data_len]
    valid = data[training_data_len:]
    valid['Predictions'] = predictions


    new_df = df.filter(['Close'])
    last_60_days = new_df[-60:].values
    # Scale the data to be values between 0 and 1
    last_60_days_scaled = scaler.transform(last_60_days)
    #Create an empty list
    X_test = []
    #Append the last 60 days
    X_test.append(last_60_days_scaled)
    #Conver the X_test dataset to a numpy array
    X_test = np.array(X_test)
    # Reshape the data
    X_test = np.reshape(X_test,(X_test.shape[0],X_test.shape[1],1))
    # Get the predicted scale price
    pred_price = model.predict(X_test)
    #undo the scaling
    pred_price = scaler.inverse_transform(pred_price)





