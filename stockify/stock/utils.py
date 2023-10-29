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


def get_dates(end_dates):
    """
    Generate a list of years between a fixed start date and a specified end date.

    This function returns a list of unique years that fall between January 1, 2012, 
    and the provided `end_dates`. The primary purpose is to identify the range of years 
    covered by a dataset with the aforementioned constraints.

    Parameters:
    -----------
    end_dates : str
        The end date as a string in the format "YYYY-MM-DD".

    Returns:
    --------
    List[int]
        A list of unique years between January 1, 2012, and the provided `end_dates`.

    Example:
    --------
    >>> get_dates("2015-06-30")
    [2012, 2013, 2014, 2015]

    Notes:
    ------
    The function uses the date format "%Y-%m-%d" and begins its range from January 1, 2012.
    """
    date_format = "%Y-%m-%d"
    datetime_obj = datetime.strptime(end_dates, date_format)
    start_date = date(2012, 1, 1)
    end_date = datetime_obj.date()

    current_date = start_date
    years = []

    while current_date <= end_date:
        years.append(current_date.year)
        current_date += timedelta(days=1)

    return years


def get_graph():
    """
    Capture the current Matplotlib plot as a base64-encoded PNG.

    This function captures the active Matplotlib figure, encodes it as a PNG, and 
    then converts the PNG bytes into a base64 encoded string. This base64 string 
    can be used directly for embedding the image into web pages.

    Returns:
    --------
    str
        A base64-encoded PNG representation of the current Matplotlib plot.

    Example:
    --------
    >>> plt.plot([1, 2, 3], [1, 2, 3])
    >>> base64_str = get_graph()

    Notes:
    ------
    Ensure a plot is active (i.e., has been created) before calling this function.
    The function uses the `plt.savefig` method from Matplotlib to capture the plot.
    """

    buffer = BytesIO()
    plt.savefig(buffer, format ='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()

    return graph

def get_plot(valid, train):
    """
    Generate a plot visualizing training data, validation data, and predictions.

    This function uses Matplotlib to visualize the `Close` prices from both the 
    training and validation datasets, along with the predictions for the validation set.
    The resulting plot is then captured as a base64 encoded string for easy embedding 
    into web pages or other outputs.

    Parameters:
    -----------
    valid : pandas.DataFrame
        The validation dataset containing columns 'Close' and 'Predictions'.
    train : pandas.DataFrame
        The training dataset containing a 'Close' column.

    Returns:
    --------
    str
        A base64-encoded PNG representation of the generated plot.

    Example:
    --------
    >>> train_data = pd.DataFrame({'Close': [1, 2, 3, 4, 5]})
    >>> valid_data = pd.DataFrame({'Close': [5, 6, 7], 'Predictions': [5.1, 6.1, 7.1]})
    >>> base64_str = get_plot(valid_data, train_data)
    >>> print(base64_str[:50])  # Displaying the first 50 characters of the encoded string
    'iVBORw0KG...'

    Notes:
    ------
    The function relies on a helper function `get_graph` to capture the plot as a 
    base64 string.
    """

    plt.switch_backend('AGG')
    plt.figure(figsize=(15,6))
    plt.title('Model')
    plt.xlabel('Date', fontsize = 18)
    plt.ylabel('Close Price USD $')
    plt.plot(train['Close'])
    plt.plot(valid[['Close','Predictions']])
    plt.xticks(rotation=45)
    plt.legend(['Train', 'Val', 'Predictions'], loc='upper right')
    plt.tight_layout()
    graph = get_graph()

    return graph


def pred_date(end_date):
    """
    Calculate the next date given an input date.

    Given an input date in the format "YYYY-MM-DD", this function returns the 
    next date as a string in the same format.

    Parameters:
    -----------
    end_date : str
        A date string in the format "YYYY-MM-DD".

    Returns:
    --------
    str
        The next date in the format "YYYY-MM-DD".

    Example:
    --------
    >>> end_date = "2023-05-01"
    >>> next_date = pred_date(end_date)
    >>> print(next_date)
    '2023-05-02'

    Notes:
    ------
    The function utilizes the datetime module to perform the date manipulations.
    """

    date_format = "%Y-%m-%d"
    date_obj = datetime.strptime(end_date, date_format)
    next_date = date_obj + timedelta(days=1)
    next_date_string = next_date.strftime(date_format)

    return next_date_string









