# Connection to the RabbitMQ Broker
import pika # The RabbitMQ client library for Python
credentials = pika.PlainCredentials('admin', 'admin')
parameters = pika.ConnectionParameters("host.docker.internal",5672,'/',credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Send a random humidity value between 0.8 and 29 every f seconds to the RabbitMQ Broker
min = 0.8
max = 29
import random 
import time
import datetime
from message import send_data
while True:

        f = 5 # Messages frequency

        # Generating a random humidity value between 0.8 and 29
        humidity = random. uniform(min,max)
        #print (humidity)

        now = datetime.datetime.now().timestamp()
        
        message = send_data(typeObject="Humidity",idObject="RandomHumidity1",idSensor="RandomHumiditySensor1",sensorCategory="virtual", sensorType="humidity",frequency=f,sensorLocation="virtual",time=now,unit="mmol/mol",value=humidity)

        channel.basic_publish(exchange='amq.topic', routing_key='humidity',body=message)
        print (message)

        time.sleep(f)