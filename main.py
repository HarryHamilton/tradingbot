import pandas as pd
import yfinance as yf

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


signal = []
signal.append(0)

# Loops through each row in the dataframe and appends the signal to a new column
for i in range(1, len(dataF)):
    df = dataF[i-1:i+1]
    signal.append(signal_generator(df))
dataF["signal"] = signal

print(dataF.iloc[:, :])  # full dataframe
print(dataF.signal.value_counts())  # the number of occurances of each element in the "signal" column of the df
