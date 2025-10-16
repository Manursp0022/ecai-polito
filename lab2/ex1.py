"""

starting from your
solution to LAB1 – Exercise 1. 
You will modify it to send data to Redis instead of printing it locally.

"""
print("dajeee")
import redis
import time
from datetime import datetime
import adafruit_dht
import uuid
from board import D4

REDIS_HOST = 'redis-14100.c293.eu-central-1-1.ec2.redns.redis-cloud.com'
REDIS_PORT = 14100
REDIS_USERNAME = 'default'
REDIS_PASSWORD = 'fMVnUawdIIZcSAHcDpJKaZykdIAynJFN'

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    username=REDIS_USERNAME,
    password=REDIS_PASSWORD
)

is_connected = redis_client.ping()
print('Redis Connected:', is_connected)

try:
    redis_client.ts().create('temp_timeseries')
    redis_client.ts().create('hum_timeseries')
except redis.ResponseError:
    pass

mac_address = hex(uuid.getnode())
dht_device = adafruit_dht.DHT11(D4)

while True:
    timestamp = time.time()
    formatted_datetime = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')
    try:
        temperature = dht_device.temperature
        humidity = dht_device.humidity

        print(f'{formatted_datetime} - {mac_address}:temperature = {temperature}')
        print(f'{formatted_datetime} - {mac_address}:humidity = {humidity}')

        timestamp_ms = int(timestamp * 1000)
        redis_client.ts().add('temp_timeseries', timestamp_ms, temperature)
        redis_client.ts().add('hum_timeseries', timestamp_ms, humidity)
    except:
        print(f'{formatted_datetime} - sensor failure')
        dht_device.exit()
        dht_device = adafruit_dht.DHT11(D4)

    
    time.sleep(2)


