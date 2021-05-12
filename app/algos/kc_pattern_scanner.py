# -*- coding: utf-8 -*-
"""
Zerodha Kite Connect - candlestick pattern scanner

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""

from kiteconnect import KiteConnect, KiteTicker
import pandas as pd
import datetime as dt
import os
import time
import numpy as np
import sys


cwd = os.chdir("/home/rajkp/code/Projects/Django-Dashboard/boilerplate-code-django-dashboard/app/algos")

#generate trading session
access_token = open("access_token.txt",'r').read()
key_secret = open("api_key.txt",'r').read().split()
kite = KiteConnect(api_key=key_secret[0])
kite.set_access_token(access_token)

#get dump of all NSE instruments
instrument_dump = kite.instruments("NSE")
instrument_df = pd.DataFrame(instrument_dump)

def instrumentLookup(instrument_df,symbol):
    """Looks up instrument token for a given script from instrument dump"""
    try:
        return instrument_df[instrument_df.tradingsymbol==symbol].instrument_token.values[0]
    except:
        return -1
    
def tokenLookup(instrument_df,symbol_list):
    """Looks up instrument token for a given script from instrument dump"""
    token_list = []
    for symbol in symbol_list:
        token_list.append(int(instrument_df[instrument_df.tradingsymbol==symbol].instrument_token.values[0]))
    return token_list

def fetchOHLC(ticker,interval,duration):
    """extracts historical data and outputs in the form of dataframe"""
    instrument = instrumentLookup(instrument_df,ticker)
    data = pd.DataFrame(kite.historical_data(instrument,dt.date.today()-dt.timedelta(duration), dt.date.today(),interval))
    data.set_index("date",inplace=True)
    return data

def doji(ohlc_df):    
    """returns dataframe with doji candle column"""
    df = ohlc_df.copy()
    avg_candle_size = abs(df["close"] - df["open"]).median()
    df["doji"] = abs(df["close"] - df["open"]) <=  (0.05 * avg_candle_size)
    return df

def maru_bozu(ohlc_df):    
    """returns dataframe with maru bozu candle column"""
    df = ohlc_df.copy()
    avg_candle_size = abs(df["close"] - df["open"]).median()
    df["h-c"] = df["high"]-df["close"]
    df["l-o"] = df["low"]-df["open"]
    df["h-o"] = df["high"]-df["open"]
    df["l-c"] = df["low"]-df["close"]
    df["maru_bozu"] = np.where((df["close"] - df["open"] > 2*avg_candle_size) & \
                               (df[["h-c","l-o"]].max(axis=1) < 0.005*avg_candle_size),"maru_bozu_green",
                               np.where((df["open"] - df["close"] > 2*avg_candle_size) & \
                               (abs(df[["h-o","l-c"]]).max(axis=1) < 0.005*avg_candle_size),"maru_bozu_red",False))
    df.drop(["h-c","l-o","h-o","l-c"],axis=1,inplace=True)
    return df

def hammer(ohlc_df):    
    """returns dataframe with hammer candle column"""
    df = ohlc_df.copy()
    df["hammer"] = (((df["high"] - df["low"])>3*(df["open"] - df["close"])) & \
                   ((df["close"] - df["low"])/(.001 + df["high"] - df["low"]) > 0.6) & \
                   ((df["open"] - df["low"])/(.001 + df["high"] - df["low"]) > 0.6)) & \
                   (abs(df["close"] - df["open"]) > 0.1* (df["high"] - df["low"]))
    return df


def shooting_star(ohlc_df):    
    """returns dataframe with shooting star candle column"""
    df = ohlc_df.copy()
    df["sstar"] = (((df["high"] - df["low"])>3*(df["open"] - df["close"])) & \
                   ((df["high"] - df["close"])/(.001 + df["high"] - df["low"]) > 0.6) & \
                   ((df["high"] - df["open"])/(.001 + df["high"] - df["low"]) > 0.6)) & \
                   (abs(df["close"] - df["open"]) > 0.1* (df["high"] - df["low"]))
    return df

def levels(ohlc_day):    
    """returns pivot point and support/resistance levels"""
    high = round(ohlc_day["high"][-1],2)
    low = round(ohlc_day["low"][-1],2)
    close = round(ohlc_day["close"][-1],2)
    pivot = round((high + low + close)/3,2)
    r1 = round((2*pivot - low),2)
    r2 = round((pivot + (high - low)),2)
    r3 = round((high + 2*(pivot - low)),2)
    s1 = round((2*pivot - high),2)
    s2 = round((pivot - (high - low)),2)
    s3 = round((low - 2*(high - pivot)),2)
    return (pivot,r1,r2,r3,s1,s2,s3)

def trend(ohlc_df,n):
    "function to assess the trend by analyzing each candle"
    df = ohlc_df.copy()
    df["up"] = np.where(df["low"]>=df["low"].shift(1),1,0)
    df["dn"] = np.where(df["high"]<=df["high"].shift(1),1,0)
    if df["close"][-1] > df["open"][-1]:
        if df["up"][-1*n:].sum() >= 0.7*n:
            return "uptrend"
    elif df["open"][-1] > df["close"][-1]:
        if df["dn"][-1*n:].sum() >= 0.7*n:
            return "downtrend"
    else:
        return None
   
def res_sup(ohlc_df,ohlc_day):
    """calculates closest resistance and support levels for a given candle"""
    level = ((ohlc_df["close"][-1] + ohlc_df["open"][-1])/2 + (ohlc_df["high"][-1] + ohlc_df["low"][-1])/2)/2
    p,r1,r2,r3,s1,s2,s3 = levels(ohlc_day)
    l_r1=level-r1
    l_r2=level-r2
    l_r3=level-r3
    l_p=level-p
    l_s1=level-s1
    l_s2=level-s2
    l_s3=level-s3
    lev_ser = pd.Series([l_p,l_r1,l_r2,l_r3,l_s1,l_s2,l_s3],index=["p","r1","r2","r3","s1","s2","s3"])
    sup = lev_ser[lev_ser>0].idxmin()
    res = lev_ser[lev_ser<0].idxmax()
    return (eval('{}'.format(res)), eval('{}'.format(sup)))

def candle_type(ohlc_df):    
    """returns the candle type of the last candle of an OHLC DF"""
    candle = None
    if doji(ohlc_df)["doji"][-1] == True:
        candle = "doji"    
    if maru_bozu(ohlc_df)["maru_bozu"][-1] == "maru_bozu_green":
        candle = "maru_bozu_green"       
    if maru_bozu(ohlc_df)["maru_bozu"][-1] == "maru_bozu_red":
        candle = "maru_bozu_red"        
    if shooting_star(ohlc_df)["sstar"][-1] == True:
        candle = "shooting_star"        
    if hammer(ohlc_df)["hammer"][-1] == True:
        candle = "hammer"       
    return candle

def candle_pattern(ohlc_df,ohlc_day):    
    """returns the candle pattern identified"""
    pattern = None
    signi = "low"
    avg_candle_size = abs(ohlc_df["close"] - ohlc_df["open"]).median()
    sup, res = res_sup(ohlc_df,ohlc_day)
    
    if (sup - 1.5*avg_candle_size) < ohlc_df["close"][-1] < (sup + 1.5*avg_candle_size):
        signi = "HIGH"
        
    if (res - 1.5*avg_candle_size) < ohlc_df["close"][-1] < (res + 1.5*avg_candle_size):
        signi = "HIGH"
    
    if candle_type(ohlc_df) == 'doji' \
        and ohlc_df["close"][-1] > ohlc_df["close"][-2] \
        and ohlc_df["close"][-1] > ohlc_df["open"][-1]:
            pattern = "doji_bullish"
    
    if candle_type(ohlc_df) == 'doji' \
        and ohlc_df["close"][-1] < ohlc_df["close"][-2] \
        and ohlc_df["close"][-1] < ohlc_df["open"][-1]:
            pattern = "doji_bearish" 
            
    if candle_type(ohlc_df) == "maru_bozu_green":
        pattern = "maru_bozu_bullish"
    
    if candle_type(ohlc_df) == "maru_bozu_red":
        pattern = "maru_bozu_bearish"
        
    if trend(ohlc_df.iloc[:-1,:],7) == "uptrend" and candle_type(ohlc_df) == "hammer":
        pattern = "hanging_man_bearish"
        
    if trend(ohlc_df.iloc[:-1,:],7) == "downtrend" and candle_type(ohlc_df) == "hammer":
        pattern = "hammer_bullish"
        
    if trend(ohlc_df.iloc[:-1,:],7) == "uptrend" and candle_type(ohlc_df) == "shooting_star":
        pattern = "shooting_star_bearish"
        
    if trend(ohlc_df.iloc[:-1,:],7) == "uptrend" \
        and candle_type(ohlc_df) == "doji" \
        and ohlc_df["high"][-1] < ohlc_df["close"][-2] \
        and ohlc_df["low"][-1] > ohlc_df["open"][-2]:
        pattern = "harami_cross_bearish"
        
    if trend(ohlc_df.iloc[:-1,:],7) == "downtrend" \
        and candle_type(ohlc_df) == "doji" \
        and ohlc_df["high"][-1] < ohlc_df["open"][-2] \
        and ohlc_df["low"][-1] > ohlc_df["close"][-2]:
        pattern = "harami_cross_bullish"
        
    if trend(ohlc_df.iloc[:-1,:],7) == "uptrend" \
        and candle_type(ohlc_df) != "doji" \
        and ohlc_df["open"][-1] > ohlc_df["high"][-2] \
        and ohlc_df["close"][-1] < ohlc_df["low"][-2]:
        pattern = "engulfing_bearish"
        
    if trend(ohlc_df.iloc[:-1,:],7) == "downtrend" \
        and candle_type(ohlc_df) != "doji" \
        and ohlc_df["close"][-1] > ohlc_df["high"][-2] \
        and ohlc_df["open"][-1] < ohlc_df["low"][-2]:
        pattern = "engulfing_bullish"
       
    return "Significance - {}, Pattern - {}".format(signi,pattern)

##############################################################################################
tickers = ["BHEL",
"CONCOR",
"ASTRAL",
"INDHOTEL",
"DALBHARAT",
"COFORGE",
"ITI",
"IPCALAB",
"SUMICHEM",
"DHANI",
"DIXON",
"SUNTV",
"FEDERALBNK",
"OFSS",
"COROMANDEL",
"RECLTD",
"VOLTAS",
"ISEC",
"AUBANK",
"BALKRISIND",
"GSPL",
"HAL",
"POLYCAB",
"TATACHEM",
"SUPREMEIND",
"LTTS",
"BHARATFORG",
"HATSUN",
"TVSMOTOR",
"GMRINFRA",
"TRENT",
"MOTILALOFS",
"L&TFH",
"ATUL",
"AIAENG",
"GLAXO",
"JSWENERGY",
"SKFINDIA",
"IDBI",
"PRESTIGE",
"NHPC",
"ATGL",
"TIINDIA",
"SJVN",
"MINDAIND",
"CANBK",
"VINATIORGA",
"BANKINDIA",
"OIL",
"BBTC",
"PFC",
"GODREJAGRO",
"AAVAS",
"EXIDEIND",
"WHIRLPOOL",
"MAXHEALTH",
"GODREJPROP",
"VBL",
"3MINDIA",
"METROPOLIS",
"ASTRAZEN",
"MGL",
"SRF",
"APOLLOTYRE",
"MFSL",
"BATAINDIA",
"UNIONBANK",
"VGUARD",
"ZYDUSWELL",
"PFIZER",
"BAYERCROP",
"IRCTC",
"CASTROLIND",
"SANOFI",
"ABFRL",
"FORTIS",
"CESC",
"PERSISTENT",
"GODREJIND",
"MPHASIS",
"PHOENIXLTD",
"CHOLAHLDNG",
"DEEPAKNTR",
"HONAUT",
"TATACOMM",
"JMFINANCIL",
"LICHSGFIN",
"CUMMINSIND",
"GICRE",
"THERMAX",
"SOLARINDS",
"SRTRANSFIN",
"LAURUSLABS",
"IDFCFIRSTB",
"CUB",
"NIACL",
"NAVINFLUOR",
"OBEROIRLTY",
"TATAELXSI",
"RELAXO",
"MANAPPURAM",
"CRISIL",
"AMARAJABAT",
"GUJGASLTD",
"BANKBARODA",
"AARTIIND",
"M&MFIN",
"ASHOKLEY",
"PGHL",
"PIIND",
"GILLETTE",
"ABCAPITAL",
"APLLTD",
"CROMPTON",
"NAM-INDIA",
"ABB",
"TTKPRESTIG",
"SUVENPHAR",
"IDEA",
"BEL",
"SCHAEFFLER",
"ZEEL",
"RBLBANK",
"RAMCOCEM",
"GLENMARK",
"RAJESHEXPO",
"SUNDRMFAST",
"EMAMILTD",
"ENDURANCE",
"SYNGENE",
"AKZOINDIA",
"LALPATHLAB",
"HINDZINC",
"TATAPOWER",
"JKCEMENT",
"ESCORTS",
"SUNDARMFIN",
"IIFLWAM",
"IBULHSGFIN",
"CREDITACC",
"KANSAINER",
"MINDTREE",
"PAGEIND",
"CHOLAFIN",
"AJANTPHARM",
"NATCOPHARM",
"JINDALSTEL",
"TORNTPOWER",
"SAIL",
"INDIAMART",
"GAIL",
"HINDPETRO",
"JUBLFOOD",
"ADANITRANS",
"BOSCHLTD",
"IGL",
"SIEMENS",
"PETRONET",
"ICICIPRULI",
"ACC",
"MARICO",
"AMBUJACEM",
"BERGEPAINT",
"PIDILITIND",
"INDUSTOWER",
"ABBOTINDIA",
"BIOCON",
"MCDOWELL-N",
"PGHH",
"DMART",
"MRF",
"DLF",
"GODREJCP",
"COLPAL",
"HDFCAMC",
"YESBANK",
"VEDL",
"BAJAJHLDNG",
"DABUR",
"INDIGO",
"ALKEM",
"CADILAHC",
"MOTHERSUMI",
"HAVELLS",
"ADANIENT",
"UBL",
"SBICARD",
"PEL",
"BANDHANBNK",
"MUTHOOTFIN",
"TORNTPHARM",
"ICICIGI",
"LUPIN",
"LTI",
"APOLLOHOSP",
"ADANIGREEN",
"NAUKRI",
"NMDC",
"PNB",
"AUROPHARMA",
"COALINDIA",
"IOC",
"NTPC",
"ULTRACEMCO",
"BPCL",
"TATASTEEL",
"TATACONSUM",
"SUNPHARMA",
"TATAMOTORS",
"GRASIM",
"SHREECEM",
"SBIN",
"EICHERMOT",
"RELIANCE",
"BAJAJ-AUTO",
"INDUSINDBK",
"BRITANNIA",
"SBILIFE",
"UPL",
"ONGC",
"ADANIPORTS",
"POWERGRID",
"NESTLEIND",
"BHARTIARTL",
"TITAN",
"HEROMOTOCO",
"ASIANPAINT",
"MARUTI",
"ITC",
"ICICIBANK",
"HCLTECH",
"M&M",
"LT",
"INFY",
"BAJAJFINSV",
"DRREDDY",
"HDFCBANK",
"CIPLA",
"HDFCLIFE",
"TCS",
"AXISBANK",
"HINDUNILVR",
"JSWSTEEL",
"TECHM",
"BAJFINANCE",
"WIPRO",
"DIVISLAB",
"KOTAKBANK",
"HINDALCO",
"HDFC"]
#####################################################################################################


def main():
    a,b = 0,0
    while a < 10:
        try:
            pos_df = pd.DataFrame(kite.positions()["day"])
            break
        except:
            print("can't extract position data..retrying")
            a+=1
    while b < 10:
        try:
            ord_df = pd.DataFrame(kite.orders())
            break
        except:
            print("can't extract order data..retrying")
            b+=1
    
    for ticker in tickers:
        try:
            ohlc = fetchOHLC(ticker, '5minute',5)
            ohlc_day = fetchOHLC(ticker, 'day',30) 
            ohlc_day = ohlc_day.iloc[:-1,:]       
            cp = candle_pattern(ohlc,ohlc_day) 
            # print(ticker, ": ",cp)   
            # if len(pos_df.columns)==0:
            #     # if macd_xover[ticker] == "bullish" and renko_param[ticker]["brick"] >=2:
            #     #     placeSLOrder(ticker,"buy",quantity,renko_param[ticker]["lower_limit"])
            #     # if macd_xover[ticker] == "bearish" and renko_param[ticker]["brick"] <=-2:
            #     #     placeSLOrder(ticker,"sell",quantity,renko_param[ticker]["upper_limit"])
            # if len(pos_df.columns)!=0 and ticker not in pos_df["tradingsymbol"].tolist():
            #     # if macd_xover[ticker] == "bullish" and renko_param[ticker]["brick"] >=2:
            #     #     placeSLOrder(ticker,"buy",quantity,renko_param[ticker]["lower_limit"])
            #     # if macd_xover[ticker] == "bearish" and renko_param[ticker]["brick"] <=-2:
            #     #     placeSLOrder(ticker,"sell",quantity,renko_param[ticker]["upper_limit"])
            # if len(pos_df.columns)!=0 and ticker in pos_df["tradingsymbol"].tolist():
            #     if pos_df[pos_df["tradingsymbol"]==ticker]["quantity"].values[0] == 0:
            #         if macd_xover[ticker] == "bullish" and renko_param[ticker]["brick"] >=2:
            #             placeSLOrder(ticker,"buy",quantity,renko_param[ticker]["lower_limit"])
            #         if macd_xover[ticker] == "bearish" and renko_param[ticker]["brick"] <=-2:
            #             placeSLOrder(ticker,"sell",quantity,renko_param[ticker]["upper_limit"])
            #     if pos_df[pos_df["tradingsymbol"]==ticker]["quantity"].values[0] > 0:
            #         order_id = ord_df.loc[(ord_df['tradingsymbol'] == ticker) & (ord_df['status'].isin(["TRIGGER PENDING","OPEN"]))]["order_id"].values[0]
            #         ModifyOrder(order_id,renko_param[ticker]["lower_limit"])
            #     if pos_df[pos_df["tradingsymbol"]==ticker]["quantity"].values[0] < 0:
            #         order_id = ord_df.loc[(ord_df['tradingsymbol'] == ticker) & (ord_df['status'].isin(["TRIGGER PENDING","OPEN"]))]["order_id"].values[0]
            #         ModifyOrder(order_id,renko_param[ticker]["upper_limit"])
        except:
            print("skipping for ",ticker)
        
# Continuous execution        
# starttime=time.time()
# timeout = time.time() + 60*60*1  # 60 seconds times 60 meaning the script will run for 1 hr
# while time.time() <= timeout:
#     try:
#         print("passthrough at ",time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
#         main()
#         time.sleep(300 - ((time.time() - starttime) % 300.0)) # 300 second interval between each new execution
#     except KeyboardInterrupt:
#         print('\n\nKeyboard exception received. Exiting.')
#         exit()
        
        
        
capital = 3000 #position size
# macd_xover = {}
# renko_param = {}
# for ticker in tickers:
    # renko_param[ticker] = {"brick_size":renkoBrickSize(ticker),"upper_limit":None, "lower_limit":None,"brick":0}
    # macd_xover[ticker] = None
    
#create KiteTicker object
kws = KiteTicker(key_secret[0],kite.access_token)
tokens = tokenLookup(instrument_df,tickers)

start_minute = dt.datetime.now().minute
def on_ticks(ws,ticks):
    global start_minute
    # renkoOperation(ticks)
    now_minute = dt.datetime.now().minute
    if abs(now_minute - start_minute) >= 5:
        start_minute = now_minute
        main(capital)

def on_connect(ws,response):
    ws.subscribe(tokens)
    ws.set_mode(ws.MODE_LTP,tokens)


def pattern_scanner():
    while True:
        now = dt.datetime.now()
        if (now.hour >= 9):
            kws.on_ticks=on_ticks
            kws.on_connect=on_connect
            kws.connect()
        if (now.hour >= 14 and now.minute >= 30):
            sys.exit()