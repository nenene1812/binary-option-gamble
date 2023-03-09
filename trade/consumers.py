# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from time import sleep
from .tasks import  get_klines #,get_time
from coinpayments.models import Balances
from channels.db import database_sync_to_async
from .models import WfxTransaction, TradeSession
from datetime import datetime, timedelta
from django.utils import timezone
from binance.client import Client
from django.db.models import Avg, Max, Min, Sum
import time
import asyncio
import random
# import redis

class TransactionConsumer(AsyncWebsocketConsumer):

    

    @database_sync_to_async
    def get_balance(self):
        return Balances.objects.get(user=self.scope['user'].id)

    @database_sync_to_async
    def get_session(self):
        return TradeSession.objects.last()
 
    @database_sync_to_async
    def get_amount(self,session_id):
        amount = WfxTransaction.objects.filter(session = session_id, status = 'win',user=self.scope['user'].id ).aggregate(Sum('amount')) 
        return amount['amount__sum']

    async def connect(self):
        if self.scope['user'].id:
            await self.channel_layer.group_add(
                'main',
                self.channel_name
            )

            await self.accept()
            session =  await self.get_session()
            await self.send(text_data=json.dumps({
                            'message': {"start":round((session.start_time).timestamp()), "end": round((session.end_time).timestamp())}
                        }))
        else:
            await self.close()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
                'main',
                self.channel_name
            )
        
    # Receive message from WebSocket
    # async def receive(self, text_data):
    #     if self.scope['user'].id:
    #         now = timezone.now()
    #         session =  await self.get_session()

    #         #check session 
    #         if now >= session.start_time and now <= session.end_time:
    #             text_data_json = json.loads(text_data)
    #             message = text_data_json['message']
    #             new_dict = json.loads(message)
    #             balance =  await self.get_balance()

    #             #check balance 
    #             if float(new_dict['amount']) <= float(balance.balance):
    #                 # {"type":1, "amount":1.00}
                    
    #                 api_key = 'xGNir5hSwP7RmjBCbqfF59ZG21acA32ggnsXLGc07HOggWhHtsTaylvqpjFIrSde'
    #                 secret_key = 'p28WOxaSARp5xI3Tvq229m1si99F3gRfFzUROmkoxepFqzxu4XmGn7Eu8ZHnAAhH'
    #                 client = Client(api_key,secret_key)
    #                 lastPrice = client.get_ticker(symbol='BTCUSDT')['lastPrice']
    #                 new_transaction = WfxTransaction(
    #                     user = self.scope['user'],
    #                     session = session,
    #                     transaction_type = new_dict['type'],
    #                     status = 'pending',
    #                     amount = new_dict['amount'],
    #                     btc_value = float(lastPrice)
    #                 )
                    
    #                 balance.balance -= float(new_dict['amount'])
    #                 await database_sync_to_async(balance.save)()
    #                 await database_sync_to_async(new_transaction.save)()
    #             else:
    #                 await self.send(text_data=json.dumps({
    #                         'message': "Balance not enough"
    #                     }))
    #             # await database_sync_to_async(balance.save)()
    #             # Send message to room group
    #             await self.channel_layer.group_send(
    #                 'main',
    #                 {
    #                     'type': 'chat_message',
    #                     'message': message
    #                 }
    #             )
    #         else:
    #             await self.send(text_data=json.dumps({
    #                         'message': "Session invalid"
    #                     }))          
    #     else:
    #         await self.close()

    # # Receive message from room group
    # async def chat_message(self, event):
    #     message = event['message']
    #     # Send message to WebSocket
    #     await self.send(text_data=json.dumps({
    #         'message': message
    #     }))

    async def send_klines(self, event):
        message = event['text']
        session =  await self.get_session()
        
        if message == 'start_session':
            await self.send(text_data=json.dumps({
                            'message': {"start":round((session.start_time).timestamp()), "end": round((session.end_time).timestamp())}
                        }))
        elif message == 'end_session':
            amount = await self.get_amount(session.id)
            if amount is not None:
                final_amount = amount + amount *0.95
                balance =  await self.get_balance()
                balance.balance += float(final_amount)
                await database_sync_to_async(balance.save)()
                await self.send(text_data=json.dumps({
                                'message': {"win":final_amount}
                            })) 




# redis_client = redis.StrictRedis(host='localhost', port=6379, db=3)
class TimeConsumer(AsyncWebsocketConsumer):


    @database_sync_to_async
    def get_chart(self):
        trade = TradeSession.objects.order_by("-id")[:60]
        array =[]
        api_key = 'xGNir5hSwP7RmjBCbqfF59ZG21acA32ggnsXLGc07HOggWhHtsTaylvqpjFIrSde'
        secret_key = 'p28WOxaSARp5xI3Tvq229m1si99F3gRfFzUROmkoxepFqzxu4XmGn7Eu8ZHnAAhH'
        now = timezone.now()
        client = Client(api_key,secret_key)
        klines = client.get_klines(symbol='BTCUSDT', interval='1m')
        for i in trade:
            if str(i.kline_end) != '2':
                array.append(i.kline_end)    
        formatedDate = now.strftime("%Y-%m-%d %H:%M")
        a = formatedDate + ':00'
        datetime_object = datetime.strptime(a,"%Y-%m-%d %H:%M:%S")   
        new_date = str(round(datetime_object.timestamp()))
        new = ''
        if trade[0].kline_end != '2':
            new_close = trade[0].kline_end.split(",")[3]
            rd_down = float(new_close) - float(new_close)*0.001
            rd_up = float(new_close) + float(new_close)*0.001
            rd_close =random.uniform(rd_down,rd_up)
            new = klines[-1][1] + ',' + klines[-1][2] + ',' + klines[-1][3] + ',' + str(rd_close) + ',' + klines[-1][5] + ',' + new_date
            #print(new)
            array.remove(trade[0].kline_end)
        else:
            # new_open + ',' + new_high + ',' + new_low + ',' + new_close + ',' + new_vol + ',' + formatedDate  
            new = klines[-1][1] + ',' + klines[-1][2] + ',' + klines[-1][3] + ',' + klines[-1][4] + ',' + klines[-1][5] + ',' + new_date
            #print(new)
        array.append(new)
        return array
    
    async def connect(self):
        if self.scope['user'].id:
            await self.channel_layer.group_add(
                'chart',
                self.channel_name
            )
            await self.accept()
            while True:
                chart =  await self.get_chart()
                await self.send(text_data=json.dumps({
                                'message': chart
                            })) 
                await asyncio.sleep(2)
        

        else:
            await self.close()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
                'chart',
                self.channel_name
            )
    
        