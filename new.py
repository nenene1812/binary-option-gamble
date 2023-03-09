import time
import redis
from threading import Thread
import asgi_redis

redis_client = redis.StrictRedis(host='localhost', port=6379, db=3)

cl = asgi_redis.RedisChannelLayer()
while True:
    a = cl.send_group( 'time',{'message':'hihi'})
    print(a)
    time.sleep(1)