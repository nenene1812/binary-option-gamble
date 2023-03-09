from django.db import models
from user.models import User
from .coinpayments import CoinPayments
from django.db.models.signals import post_save
# Create your models here.


class WalletAddress(models.Model):
    """ Class customer wallet address"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address_text = models.CharField(max_length=255, null=False, blank=False)
    coin_syntax =  models.CharField(max_length=10, null=False, blank=False)
    coin_name = models.CharField(max_length=40)


class Invoice(models.Model):
    """Class customer invoice """
    
    ACTION_CHOICES = [
        (1, ("deposit")),
        (2, ("withdraw")),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    action_type = models.IntegerField(default=1)
    txn_id = models.CharField(max_length=255)
    timeout = models.DecimalField(max_digits=65, decimal_places=18)
    currency1_amount = models.FloatField()
    currency2_amount = models.FloatField()
    network_fee = models.FloatField()
    currency1 = models.CharField(max_length=255)
    currency2 = models.CharField(max_length=255)
    checkout_url = models.CharField(max_length=1000)
    status_url = models.CharField(max_length=1000)
    qrcode_url = models.CharField(max_length=1000)
    status = models.IntegerField()
    status_text = models.CharField(max_length=255)
    payment_address = models.CharField(max_length=255)


class Balances(models.Model):
    """Class cutomer balance"""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.FloatField()

def create_balance(sender,**kwargs):
    if kwargs['created']:
        balance = Balances.objects.create(user=kwargs['instance'],balance=0)
post_save.connect(create_balance,sender=User)

class BalancesHistory(models.Model):
    """Class log balance change history """

    ACTION_CHOICES = [
        (1, ("deposit")),
        (2, ("withdraw")),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.ForeignKey(Balances, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    balance_befor = models.FloatField()
    balance_after = models.FloatField()
    action_type = models.IntegerField(default=1)
    source_from = models.CharField(max_length=255)
    source_id = models.CharField(max_length=255)
    