from django.shortcuts import render
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView
)
from .serializers import (  WalletAddressSerializer,
                            UpdateWaddressSerializer,
                            DepositSerializer,
                            WithdrawSerializer,
                            InvoiceViewSerializer,
                            BalanceViewSerializer
)
from .models import WalletAddress, Invoice, Balances, BalancesHistory
from rest_framework import permissions
from .permissions import IsOwner
import os
from rest_framework.response import Response
from rest_framework import generics,status, views
from .coinpayments import CoinPayments
from rest_framework import pagination
# Create your views here.



class ExamplePagination(pagination.PageNumberPagination):       
       page_size = 1


class WalletAddressAPIView(ListCreateAPIView):
    serializer_class = WalletAddressSerializer
    queryset = WalletAddress.objects.all()
    permission_classes = (permissions.IsAuthenticated,IsOwner,)
    lookup_field = "user"

    def post(self, request):
        userAddress = self.queryset.filter(user=self.request.user
                        ,coin_syntax=self.request.data['coin_syntax'])
        if userAddress:
            return Response({'error': 'Coin Address exist'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = self.serializer_class(data = request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=self.request.user)
            
        return Response({'success': 'save wallet address successfully'}, status=status.HTTP_200_OK)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class UpdateWaddressAPI(generics.GenericAPIView):
    serializer_class = UpdateWaddressSerializer
    permission_classes = (permissions.IsAuthenticated,IsOwner,)
    
    def post(self, request):
        try:
            userAddress = WalletAddress.objects.get(user=self.request.user
                                                    ,coin_syntax=request.data['coin_syntax'])
            
            userAddress.address_text = request.data['address_text']
            userAddress.save()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'success': 'new address updated'}, status=status.HTTP_200_OK)
    
    
class InvoiceViewAPI(ListAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceViewSerializer
    permission_classes = (permissions.IsAuthenticated,IsOwner,)
    lookup_field = "user"
    pagination_class=ExamplePagination

    def get_queryset(self):
        # self.serializer_class = ''
        return self.queryset.filter(user=self.request.user)

class BalancesViewAPI(ListAPIView):
    queryset = Balances.objects.all()
    serializer_class = BalanceViewSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "user"

    def get_queryset(self):
        # self.serializer_class = ''
        return self.queryset.filter(user=self.request.user)


class DepositAPI(generics.GenericAPIView):
    # queryset = Invoice.objects.all()
    serializer_class = DepositSerializer
    permission_classes = (permissions.IsAuthenticated,)
    # lookup_field = "user"

    def post(self, request):
        data = request.data
        create_transaction_params = {
            'amount' : float(data['currency1_amount']),
            'currency1' : data['currency1'],
            'currency2' : data['currency2']
        }
        obj = CoinPayments.get_instance()
        transaction = obj.create_transaction(create_transaction_params)
        
        post_params1 = {
            'txid' : transaction['result']['txn_id'],
            }
        transactioninfo = obj.getTransactionInfo(post_params1)
        invoice ={}
        invoice['action_type'] = 1 #auto 
        invoice['txn_id'] = transaction['result']['txn_id'] #auto 
        invoice['timeout'] = float(transaction['result']['timeout']) #auto 
        invoice['currency1_amount'] = float(data['currency1_amount']) # FE send 
        invoice['currency2_amount'] = float(transaction['result']['amount'])
        invoice['network_fee'] = float(transaction['result']['confirms_needed'])
        invoice['currency1'] = data['currency1'] # FE send 
        invoice['currency2'] = data['currency2'] # FE send 
        invoice['checkout_url'] = transaction['result']['checkout_url']
        invoice['status_url'] = transaction['result']['status_url']
        invoice['qrcode_url'] = transaction['result']['qrcode_url']
        invoice['status'] = transactioninfo['result']['status']
        invoice['status_text'] = transactioninfo['result']['status_text']
        invoice['payment_address'] = transactioninfo['result']['payment_address']

        # serializer = self.serializer_class(data = invoice)
        # serializer.is_valid(raise_exception=True)
        # serializer.save(user=self.request.user)
        try:
            # serializer = self.serializer_class(data = invoice)
            # print(serializer)
            # serializer.is_valid(raise_exception=True)
            # serializer.save(user=self.request.user)

            new_invoice = Invoice(
                user=self.request.user,
                action_type = invoice['action_type'],
                txn_id = invoice['txn_id'],
                timeout = invoice['timeout'],
                currency1_amount = invoice['currency1_amount'],
                currency2_amount = invoice['currency2_amount'],
                network_fee = invoice['network_fee'],
                currency1 = invoice['currency1'],
                currency2 = invoice['currency2'],
                checkout_url = invoice['checkout_url'],
                status_url = invoice['status_url'],
                qrcode_url = invoice['qrcode_url'],
                status = invoice['status'],
                status_text = invoice['status_text'],
                payment_address = invoice['payment_address']
            )
            new_invoice.save()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(invoice, status=status.HTTP_201_CREATED)

class WithdrawAPI(generics.GenericAPIView):
    serializer_class = WithdrawSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Invoice.objects.all()
    # lookup_field = "user"

    # def get_queryset(self):
    #     data = self.queryset.filter(user=self.request.user)
    #     print(data)
    #     return data

    def post(self, request):
        data = request.data
        balance = Balances.objects.get(user=self.request.user)
        if float(balance.balance) >= float(data['currency1_amount']):
            try:  
                create_transaction_params = {
                    'amount' : float(data['currency1_amount']),
                    'currency1' : data['currency1'],
                    'currency2' : data['currency2'],
                    'address':data['address'],
                }
                obj = CoinPayments.get_instance()
                transaction = obj.create_transaction(create_transaction_params)
                
                post_params1 = {
                    'txid' : transaction['result']['txn_id'],
                    }
                transactioninfo = obj.getTransactionInfo(post_params1)
                invoice ={}
                invoice['action_type'] = 2 #auto 
                invoice['txn_id'] = transaction['result']['txn_id'] #auto 
                invoice['timeout'] = float(transaction['result']['timeout']) #auto 
                invoice['currency1_amount'] = float(data['currency1_amount']) # FE send 
                invoice['currency2_amount'] = float(transaction['result']['amount'])
                invoice['network_fee'] = float(transaction['result']['confirms_needed'])
                invoice['currency1'] = data['currency1'] # FE send 
                invoice['currency2'] = data['currency2'] # FE send 
                invoice['checkout_url'] = transaction['result']['checkout_url']
                invoice['status_url'] = transaction['result']['status_url']
                invoice['qrcode_url'] = transaction['result']['qrcode_url']
                invoice['status'] = transactioninfo['result']['status']
                invoice['status_text'] = transactioninfo['result']['status_text']
                invoice['payment_address'] = transactioninfo['result']['payment_address']
                try:
                    new_invoice = Invoice(
                        user=self.request.user,
                        action_type = invoice['action_type'],
                        txn_id = invoice['txn_id'],
                        timeout = invoice['timeout'],
                        currency1_amount = invoice['currency1_amount'],
                        currency2_amount = invoice['currency2_amount'],
                        network_fee = invoice['network_fee'],
                        currency1 = invoice['currency1'],
                        currency2 = invoice['currency2'],
                        checkout_url = invoice['checkout_url'],
                        status_url = invoice['status_url'],
                        qrcode_url = invoice['qrcode_url'],
                        status = invoice['status'],
                        status_text = invoice['status_text'],
                        payment_address = invoice['payment_address']
                    )
                    new_invoice.save()
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
                
            # else:
            #     return Response({'error': 'Coin wallet doesnot exist'}, status=status.HTTP_400_BAD_REQUEST)
            return Response(invoice, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'balance not enough'}, status=status.HTTP_400_BAD_REQUEST)
    

class IPNView(generics.GenericAPIView):
    serializer_class = WithdrawSerializer
    
    def post(self, request):
        data = request.data
        data = data.dict()
        print(data)
        invoice = Invoice.objects.get(txn_id=data['txn_id'])

        invoice.status = data['status']
        invoice.status_text = data['status_text']
        print(invoice.user)
        invoice.save()
        if data['status_text'] =='Complete' and invoice.action_type == 1: 
            balance = Balances.objects.get(user=invoice.user)
            
            new_balancehis = BalancesHistory(
                user = invoice.user,
                balance = balance,
                balance_befor = balance.balance,
                balance_after = balance.balance + float(data['amount1']),
                action_type = invoice.action_type,
                source_from = 'invoice',
                source_id = data['txn_id']
            )
            new_balancehis.save()
            balance.balance += float(data['amount1'])
            balance.save()

        if data['status_text'] =='Complete' and invoice.action_type == 2:
            balance = Balances.objects.get(user=invoice.user)
            new_balancehis = BalancesHistory(
                user = invoice.user,
                balance = balance,
                balance_befor = balance.balance,
                balance_after = balance.balance - float(data['amount1']),
                action_type = invoice.action_type,
                source_from = 'invoice',
                source_id = data['txn_id']
            )
            new_balancehis.save()
            balance.balance -= float(data['amount1'])
            balance.save()

        return Response(request.data, status=status.HTTP_200_OK)