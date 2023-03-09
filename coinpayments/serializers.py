from rest_framework import serializers
from .models import WalletAddress, Invoice ,Balances


class WalletAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = WalletAddress
        fields = ['address_text','coin_syntax','coin_name']


class UpdateWaddressSerializer(serializers.ModelSerializer):
    
    address_text = serializers.DecimalField(
        max_digits=65, decimal_places=18,write_only=True)
    coin_syntax = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        model = WalletAddress
        fields = ['address_text','coin_syntax']

class InvoiceViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Invoice
        fields = ['action_type','status_text','txn_id','created_at','currency1_amount','currency1']

class BalanceViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Balances
        fields = ['user','balance']


class DepositSerializer(serializers.ModelSerializer):

    class Meta:
        model = Invoice
        fields = ['currency1_amount','currency1','currency2']



class WithdrawSerializer(serializers.ModelSerializer):
    address = serializers.DecimalField(
        max_digits=65, decimal_places=18,write_only=True)

    class Meta:
        model = Invoice
        fields = ['currency1_amount','currency1','currency2','address']

