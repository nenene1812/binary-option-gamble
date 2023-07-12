import time
import requests
import re
import decimal
import json
import random
from binance.client import Client
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from coinpayments.models import Balances 
from .models import TradeSession, WfxTransaction
from datetime import datetime, timedelta
from django.db.models import Avg, Max, Min, Sum
from celery import group
from celery import Celery
import core.celery

channel_layer = get_channel_layer()

@shared_task
def get_klines():
    api_key = 'xGNir5hSwP7RmjBCbqfF59ZG21acA32ggnsXLGc07HOggWhHtsTaylvqpjFIrSde'
    secret_key = 'p28WOxaSARp5xI3Tvq229m1si99F3gRfFzUROmkoxepFqzxu4XmGn7Eu8ZHnAAhH'
    client = Client(api_key,secret_key)
    klines = client.get_klines(symbol='BTCUSDT', interval='1m')
    tradeSession = TradeSession(
        start_time = datetime.now(),
        end_time = datetime.now() + timedelta(seconds=30),
        kline_end = '2'
    )
    tradeSession.save()
    session = TradeSession.objects.last()

    async_to_sync(channel_layer.group_send)('main',{'type':'send_klines','text':'start_session'})
    time.sleep(30)
    # session = 8f82d443-fbc2-4ad9-95c3-1bd9e2d686fc

    # === tem off
    
    
    
    ValueShort = WfxTransaction.objects.filter(session = session.id, transaction_type = 1 ).aggregate(Sum('amount'))  
    MinValueShort = WfxTransaction.objects.filter(session = session.id, transaction_type = 1 ).aggregate(Min('btc_value'))['btc_value__min']
    MinValueShort = float(MinValueShort if MinValueShort != None else 0)
    ValueLong = WfxTransaction.objects.filter(session = session.id, transaction_type = 2 ).aggregate(Sum('amount'))
    MaxValueLong = WfxTransaction.objects.filter(session = session.id, transaction_type = 2 ).aggregate(Max('btc_value'))['btc_value__max']
    MaxValueLong = float(MaxValueLong if MaxValueLong != None else 0)
    
    delta = float(ValueShort['amount__sum']  if ValueShort['amount__sum'] != None else 0) - float(ValueLong['amount__sum']  if ValueLong['amount__sum'] != None else 0)
    klines = client.get_klines(symbol='BTCUSDT', interval='1m')
    open_candles,high,low,close,vol= klines[-1][1],klines[-1][2],klines[-1][3],klines[-1][4],klines[-1][5]
    new_open = 0 
    new_high = 0
    new_low = 0 
    new_close = 0 
    new_vol = 0 
    if ValueShort['amount__sum'] == None and ValueLong['amount__sum'] == None:
        new_open = open_candles
        new_high = high
        new_low = low
        new_close = close
        new_vol = vol
        # print("aa@")
    else: 
        # print("ba@")
        if delta >= 0: 
            # red candle - decrease - short 
            if open_candles > close:
                new_open = open_candles
                new_high = high
                new_low = low
                new_close = str(MinValueShort - MinValueShort*0.001) if MinValueShort != 0 else close
                new_vol = vol
            if open_candles < close:
                new_open = close 
                new_high = high
                new_low = low
                new_close = str(MinValueShort - MinValueShort*0.001) if MinValueShort != 0 else open_candles
                new_vol = vol
            if open_candles == close:
                new_open = str(float(open_candles) + float(open_candles)*0.001)
                new_high = high
                new_low = low
                new_close = str(MinValueShort - MinValueShort*0.001) if MinValueShort != 0 else close
                new_vol = vol
            
            #trans_short = WfxTransaction.objects.filter(session = session.id, transaction_type = 1 )
            WfxTransaction.objects.filter(session = session.id, transaction_type = 1 ).update(status='loss')
            
            #trans_long = WfxTransaction.objects.filter(session = session.id, transaction_type = 2 )
            WfxTransaction.objects.filter(session = session.id, transaction_type = 2 ).update(status='win')

        else: 
            # blue candle - increase - long 
            if open_candles < close:
                new_open = open_candles
                new_high = high
                new_low = low
                new_close = str(MaxValueLong + MaxValueLong*0.001) if MaxValueLong != 0 else close
                new_vol = vol
            if open_candles > close:
                new_open = close
                new_high = high
                new_low = low
                new_close = str(MaxValueLong + MaxValueLong*0.001) if MaxValueLong != 0 else open_candles 
                new_vol = vol
            if open_candles == close:
                new_open = open_candles 
                new_high = high
                new_low = low
                new_close = str(MaxValueLong + MaxValueLong*0.001) if MaxValueLong != 0 else close + close*0.01
                new_vol = vol

            #trans_short = WfxTransaction.objects.filter(session = session.id, transaction_type = 1 )
            WfxTransaction.objects.filter(session = session.id, transaction_type = 1 ).update(status='win')

            #trans_long = WfxTransaction.objects.filter(session = session.id, transaction_type = 2 )
            WfxTransaction.objects.filter(session = session.id, transaction_type = 2 ).update(status='loss')

    formatedDate = session.end_time.strftime("%Y-%m-%d %H:%M")
    a = formatedDate + ':00'
    
    datetime_object = datetime.strptime(a,"%Y-%m-%d %H:%M:%S")
    new_kline = new_open + ',' + new_high + ',' + new_low + ',' + new_close + ',' + new_vol + ',' + str(round(datetime_object.timestamp()))
    # print(new_kline)
    update_session =  TradeSession.objects.get(id = session.id)
    update_session.kline_end = new_kline
    update_session.save()
    time.sleep(25)
    # print('end_session')
    async_to_sync(channel_layer.group_send)('main',{'type':'send_klines','text':'end_session'})
    # return text_data

# @shared_task

# @shared_task
# def get_time():
#     trade = TradeSession.objects.order_by("-id")[:60]
#     array =[]
#     print('e')
#     async_to_sync(channel_layer.group_send)('time',{'type':'send_time','text':'ee'})
#     # async_to_sync(channel_layer.group_send)('main',{'type':'send_time','text':'end_session'})

# run_group = group(get_klines.s(), get_time.s())
# run_group()
