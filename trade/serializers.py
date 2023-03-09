from rest_framework import serializers
from .models import TradeSession, WfxTransaction
from django.core.exceptions import ValidationError
from coinpayments.models import Balances



class WfxTransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = WfxTransaction
        fields = ['transaction_type','amount','status','created_at']


class CreateWfxTransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = WfxTransaction
        fields = ['transaction_type','amount']
    
    def  validate(self,attrs):
        transaction_type = attrs.get('transaction_type','')
        amount = attrs.get('amount','')
        if transaction_type not in [1,2]:
            raise ValidationError('Invalid transaction_type, try again')
        if float(amount) <= 0.0:
            raise ValidationError('amount must more than zero, try again')
        return {
            'transaction_type': transaction_type,
            'amount': amount
        }

        return super().validate(attrs)