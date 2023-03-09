from django.db import models
from user.models import User
from .utils import create_new_ref_number
from datetime import datetime, timedelta
from django.contrib.postgres.fields import ArrayField
import uuid


class TradeSession(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    kline_open = models.CharField(default='1',max_length=255)
    kline_end = models.CharField(default='1',max_length=255)

class WfxTransaction(models.Model):
    """Class log trade transaction""" 

    ACTION_CHOICES = [
        (1, ("short")),
        (2, ("long")),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False,unique=True,db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    session = models.ForeignKey(TradeSession, on_delete=models.CASCADE)
    transaction_type = models.IntegerField(default=1)
    amount = models.FloatField()
    status = models.CharField(max_length=20)
    btc_value = models.FloatField()



