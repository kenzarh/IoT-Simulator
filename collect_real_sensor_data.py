import pika # The RabbitMQ client library for Python

import time

credentials = pika.PlainCredentials('admin', 'admin')
parameters = pika.ConnectionParameters("localhost",5672,'/',credentials)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()

import json
from urllib.request import urlopen

url1 = "http://dafflon.fr:5000/api/Sensor/light/data/LIGHT"
url2 = "http://dafflon.fr:5000/api/Sensor/lm358/data/SOUND"

while True:
        response1 = urlopen(url1)
        data1 = json.loads(response1.read())
        channel.basic_publish(exchange='amq.topic', routing_key='light',body=json.dumps(data1))

        response2 = urlopen(url2)
        data2 = json.loads(response2.read())
        channel.basic_publish(exchange='amq.topic', routing_key='sound',body=json.dumps(data2))
       
        time.sleep(5)
