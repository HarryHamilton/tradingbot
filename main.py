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


def trading_job():
    candles = get_candles(5)

    # Create a dataframe
    dfstream = pd.DataFrame(columns=["Open", "Close", "High", "Low"])
    for index, candle in enumerate(candles):
        dfstream.loc[index, ["Open"]] = float(str(candle.bid.o))
        dfstream.loc[index, ["Close"]] = float(str(candle.bid.c))
        dfstream.loc[index, ["High"]] = float(str(candle.bid.h))
        dfstream.loc[index, ["Low"]] = float(str(candle.bid.l))

    dfstream["Open"] = dfstream["Open"].astype(float)
    dfstream["Close"] = dfstream["Close"].astype(float)
    dfstream["High"] = dfstream["High"].astype(float)
    dfstream["Low"] = dfstream["Low"].astype(float)

    signal = signal_generator(dfstream.iloc[:-1,:])  # Check if we have an engulfing pattern on the data we just found

    # executes order
    client = API(access_token)

    # Use previous candle range as the stop loss distance
    SLTPRatio = 2.  # stop loss take profit ratio
    previous_candle_range = abs(dfstream["High"].iloc[-2] - dfstream["Low"].iloc[-2])  # Get range, high - low price
    open_price = float(str(candle.bid.o))

    # Stop loss
    SLBuy = open_price - previous_candle_range
    SLSell = open_price + previous_candle_range

    # Take profit
    TPBuy = open_price + previous_candle_range * SLTPRatio
    TPSell = open_price - previous_candle_range * SLTPRatio

    # print(dfstream.iloc[:-1,:])
    # print("--")
    # print(TPBuy, " ", SLBuy, " ", TPSell, " ", SLSell)

    # SELL
    if signal == 1:
        market_order = MarketOrderRequest(instrument="EUR_USD",
                                          units=-1000,
                                          takeProfitOnFill=TakeProfitDetails(price=TPSell).data,
                                          stopLossOnFill=StopLossDetails(price=SLSell).data)
        r = orders.OrderCreate(accountID, data=market_order.data)
        rv = client.request(r)
        print(rv)
    # BUY
    elif signal == 2:
        market_order = MarketOrderRequest(instrument="EUR_USD",
                                          units=+10000,
                                          takeProfitOnFill=TakeProfitDetails(price=TPBuy).data,
                                          stopLossOnFill=StopLossDetails(price=SLBuy).data)
        r = orders.OrderCreate(accountID, data=market_order.data)
        rv = client.request(r)
        print(rv)

trading_job()



