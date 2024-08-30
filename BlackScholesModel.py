from math import log, sqrt, pi, exp
from scipy.stats import norm
from datetime import datetime, date
import numpy as np
import dateutil
import pandas_datareader.data as web

import pandas as pd
from pandas import DataFrame

def d1(S,K,T,r,sigma):
    return(log(S/K)+(r+(sigma**2)/2.0)*T)/(sigma*sqrt(T))
def d2(S,K,T,r,sigma):
    return d1(S,K,T,r,sigma)-sigma*sqrt(T)


def bs_call(S, K, T, r, sigma):
    return S * norm.cdf(d1(S, K, T, r, sigma)) - K * exp(-r * T) * norm.cdf(d2(S, K, T, r, sigma))
def bs_put(S, K, T, r, sigma):
    #return K * exp(-r * T) * norm.cdf(-d2(S, K, T, r, sigma)) - S * norm.cdf(-d1(S, K, T, r, sigma))
    return K * exp(-r * T) - S + bs_call(S, K, T, r, sigma)

def orgDataReturns(df, date):
    df = df.loc['1982-04-20':date]
    #print(df)
    df = df.sort_values(by="Date")
    df = df.dropna()
    df = df.assign(close_day_before=df.Close.shift(1))
    df['returns'] = ((df.Close - df.close_day_before)/df.close_day_before)

    return df['returns']

def getCall(df, date, expiry, strikePrice):
    dfReturns = orgDataReturns(df, date)
    curDate = datetime.strptime(date, '%Y-%m-%d')#dateutil.parse(date)

    sigma = np.sqrt(252) * dfReturns.std()
    uty = web.DataReader(
        "^TNX", 'yahoo', curDate.replace(day=curDate.day - 1), curDate)['Close'].iloc[-1]
    lcp = df['Close'].iloc[-1]
    t = (datetime.strptime(expiry, "%Y-%m-%d") - curDate).days/365

    print('vars for black scholes')
    print(lcp, strikePrice, t, uty, sigma)
    return bs_call(lcp, strikePrice, t, uty, sigma)

def getPut(df, date, expiry, strikePrice):
    dfReturns = orgDataReturns(df, date)
    curDate = datetime.strptime(date, '%Y-%m-%d')#dateutil.parse(date)

    sigma = np.sqrt(252) * dfReturns.std()
    uty = web.DataReader(
        "^TNX", 'yahoo', curDate.replace(day=curDate.day - 1), curDate)['Close'].iloc[-1]
    lcp = df['Close'].iloc[-1]
    t = (datetime.strptime(expiry, "%Y-%m-%d") - curDate).days/365

    print('vars for black scholes')
    print(lcp, strikePrice, t, uty, sigma)
    return bs_put(lcp, strikePrice, t, uty, sigma)


#sigma = np.sqrt(252) * df['returns'].std()
#uty = web.DataReader(
#    "^TNX", 'yahoo', today.replace(day=today.day-1), today)['Close'].iloc[-1]
#lcp = df['Close'].iloc[-1]
#t = (datetime.strptime(expiry, "%m-%d-%Y") - datetime.utcnow()).days / 365