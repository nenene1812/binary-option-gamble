from django.shortcuts import render
from rest_framework import permissions
from django.shortcuts import render
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView
)
from rest_framework import permissions
from coinpayments.permissions import IsOwner
import os
from .models import TradeSession, WfxTransaction
from rest_framework.response import Response
from rest_framework import generics,status, views
from rest_framework import pagination
from .serializers import (WfxTransactionSerializer,CreateWfxTransactionSerializer)
from coinpayments.models import Balances
from django.utils import timezone
from binance.client import Client
from datetime import datetime, timedelta
from django.conf import settings

class Pagination(pagination.PageNumberPagination):       
       page_size = 5

def index(request):
    return render(request, 'trade/index.html')

def room(request, room_name):
    return render(request, 'trade/room.html', {
        'room_name': room_name
    })


class WfxTransactionAPI(generics.GenericAPIView):
    serializer_class = CreateWfxTransactionSerializer
    permission_classes = (permissions.IsAuthenticated,IsOwner,)
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        balance = Balances.objects.get(user=self.request.user)
        now = timezone.now()
        session = TradeSession.objects.last()
        if now >= session.start_time and now <= session.end_time:
            if float(data['amount']) <= float(balance.balance):
                
                try:
                    api_key = settings.API_KEY_BINANCE
                    secret_key = settings.SECRET_KEY_BINANCE
                    client = Client(api_key,secret_key)
                    lastPrice = client.get_ticker(symbol='BTCUSDT')['lastPrice']
                    new_transaction = WfxTransaction(
                    user = self.request.user,
                    session = session,
                    transaction_type = data['transaction_type'],
                    status = 'pending',
                    amount = float(data['amount']),
                    btc_value = float(lastPrice)
                    )
                    new_transaction.save()
                    balance.balance -= float(data['amount'])
                    balance.save()
                    return Response({'status':'Sucessfully','balance':balance.balance}, status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)  
            else:
                return Response({'error': 'Balance not enough'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Session invalid'}, status=status.HTTP_400_BAD_REQUEST)
        
    
    
class WfxTransactionAPIView(ListAPIView):
    queryset = WfxTransaction.objects.all()
    serializer_class = WfxTransactionSerializer
    permission_classes = (permissions.IsAuthenticated,IsOwner,)
    lookup_field = "user"
    pagination_class=Pagination

    def get_queryset(self):
        # self.serializer_class = ''
        return self.queryset.filter(user=self.request.user).order_by('-created_at')
