# -*- coding: utf-8 -*-
"""
Zerodha Kite Connect Intro

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""
from kiteconnect import KiteConnect
import os


cwd = os.chdir("/home/rajkp/code/Projects/Django-Dashboard/boilerplate-code-django-dashboard/app/algos")

#generate trading session
access_token = open("access_token.txt",'r').read()
key_secret = open("api_key.txt",'r').read().split()
kite = KiteConnect(api_key=key_secret[0])
kite.set_access_token(access_token)


# Fetch quote details
quote = kite.quote("NSE:INFY")

# Fetch last trading price of an instrument
ltp = kite.ltp("NSE:INFY")

# Fetch order details
orders = kite.orders()
positions = kite.positions()
mfholdings = kite.mf_holdings()

def get_mfholdings():

# Fetch position details
def get_positions():
        positions = kite.positions()
        return positions


# Fetch holding details
def get_holdings():
        holdings = kite.holdings()
        return holdings