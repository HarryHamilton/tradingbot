import pandas as pd
import yfinance as yf

# Imports for API  stuff
from apscheduler.schedulers.blocking import BlockingScheduler
from oandapyV20 import API
import oandapyV20.endpoints.orders as orders
from oandapyV20.contrib.requests import MarketOrderRequest, TakeProfitDetails, StopLossDetails
from oanda_candles import Pair, Gran, CandleClient
from config import access_token, accountID





dataF = yf.download("EURUSD=X", start="2023-1-25", end="2023-2-25", interval="15m")
def signal_generator(df):
    open = df.Open.iloc[-1]  # iloc will return a specific column. by doing -1, we are returning the final column
    close = df.Close.iloc[-1]
    prev_open = df.Open.iloc[-2]
    prev_close = df.Close.iloc[-2]

    # find bearish pattern (a signal to sell)
    if close < prev_open < prev_close <= open and open > close:
        return 1

    # find bullish pattern (a signal to buy)
    elif open < close and close > prev_open > prev_close >= open:
        return 2

    # no clear pattern
    else:
        return 0


    # TO USE THE FUNCTION:
    # signal = []
    # signal.append(0)

    # Loops through each row in the dataframe and appends the signal to a new column
    # for i in range(1, len(dataF)):
    #    df = dataF[i-1:i+1]
    #    signal.append(signal_generator(df))
    # dataF["signal"] = signal

    # print(dataF.iloc[:, :])  # full dataframe
    # print(dataF.signal.value_counts())  # the number of occurances of each element in the "signal" column of the df







def get_candles(last_n_candles):
    """Grabs the last N number of candles in the market for a given pair"""
    client = CandleClient(access_token, real=False)   # real=False as this is a practice account
    collector = client.get_collector(Pair.EUR_USD, Gran.M15)
    candles = collector.grab(last_n_candles)
    return candles

    # TO USE THE FUNCTION:
    # candles = get_candles(5)
    # for candle in candles:
    #    print(candle.bid.o)
    # this will return the opening price of the last 5 candles

