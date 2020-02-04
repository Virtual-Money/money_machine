import requests
import hashlib
import hmac
import base64
import time
from datetime import datetime
import os
from tokens import *
from config import *

def log_error(error):
    filename = 'error_log.txt'

    if os.path.exists(filename):
        append_write = 'a' # append if already exists
    else:
        append_write = 'w' # make a new file if not

    efile = open(filename,append_write)
    efile.write(str(datetime.now())+": "+str(error) + "\n")
    efile.close()

def telegram_bot_sendtext(bot_message):
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()

def convert(d):
    volume = []
    close = []
    open = []
    time = []
    for entry in d:
        volume.append(entry['volumeto'])
        close.append(entry['close'])
        open.append(entry['open'])
        time.append(entry['time'])
    return volume, close, open, time

#request data from crypto compare
def fetch_data(length, time, sym):
    length = str(length)
    api_uri = 'https://min-api.cryptocompare.com/data/'+time+'?fsym='+sym+'&tsym=USD&limit='+length+'&e=Bitstamp&api_key='+key
    return requests.get(api_uri).json()['Data']

#bybit stuff
def timestamp():
    return int(round(time.time() * 1000))

def get_bal():
    url = 'https://api.bybit.com/position/list'
    param_str = 'api_key=' + api_key + '&timestamp=' + str(timestamp())
    
    message = bytes(param_str, 'utf-8')
    secret = bytes(private_key, 'utf-8')

    sign = hmac.new(secret, message, digestmod=hashlib.sha256).digest().hex()
    
    p = url + '?' + param_str + '&sign=' + sign
    response = requests.get(p).json()
    return response['result'][0]

def open_order(last_price):
    balance = get_bal()['wallet_balance']
    usdbal = int( last_price*balance*amountOfFunds*leverage )
    url = 'https://api.bybit.com/open-api/order/create'
    side = 'side=Buy'
    symbol = 'symbol=BTCUSD'
    order_type = 'order_type=Market'
    qty = 'qty='+str(usdbal)
    price = 'price='
    time_in_force = 'time_in_force='
    param_str = 'api_key='+api_key+'&'+order_type+'&'+price+'&'+qty+'&'+side+'&'+symbol+'&'+time_in_force+'&timestamp='+str(timestamp())

    message = bytes(param_str, 'utf-8')
    secret = bytes(private_key, 'utf-8')

    sign = hmac.new(secret, message, digestmod=hashlib.sha256).digest().hex()

    p = url + '?' + param_str + '&sign=' + sign
    response = requests.post(p).json()
    return response

def close_position():
    openp = get_bal()['size']

    url = 'https://api.bybit.com/open-api/order/create'
    side = 'side=Sell'
    symbol = 'symbol=BTCUSD'
    order_type = 'order_type=Market'
    qty = 'qty='+str(openp)
    price = 'price='
    time_in_force = 'time_in_force='
    param_str = 'api_key='+api_key+'&'+order_type+'&'+price+'&'+qty+'&'+side+'&'+symbol+'&'+time_in_force+'&timestamp='+str(timestamp())
    
    message = bytes(param_str, 'utf-8')
    secret = bytes(private_key, 'utf-8')
    
    sign = hmac.new(secret, message, digestmod=hashlib.sha256).digest().hex()
    
    p = url + '?' + param_str + '&sign=' + sign
    response = requests.post(p).json()
    
    
    return response
