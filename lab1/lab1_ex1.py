import adafruit_dht
import uuid
import time
from datetime import datetime
from board import D4

mac_adress = hex(uuid.getnode())
print(mac_adress)

dht_device = adafruit_dht.DHT11(D4)

while True:
    timestamp = time.time()
    print(timestamp)
    formatted_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')
    try:
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        print(f'{formatted_date}-{mac_adress}:{temperature}')
        print(f'{formatted_date}-{mac_adress}:{humidity}')
        print()
    except:
        print()
        dht_device.exit()
        dht_device = adafruit_dht.DHT11(D4)

    print(formatted_date)
    time.sleep(2)
