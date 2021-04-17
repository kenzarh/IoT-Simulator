# Connection to the RabbitMQ Broker
import pika # The RabbitMQ client library for Python
credentials = pika.PlainCredentials('admin', 'admin')
parameters = pika.ConnectionParameters("host.docker.internal",5672,'/',credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Send a random air density value between 1059 and 1394 every f seconds to the RabbitMQ Broker
min = 1059
max = 1394
import random 
import time
import datetime
from message import send_data
while True:

        f = 5 # Messages frequency

        # Generating a random air density value between 1059 and 1394
        airdensity = random. uniform(min,max)
        #print (airdensity)

        now = datetime.datetime.now().timestamp()
        
        message = send_data(typeObject="AirDensity",idObject="RandomAirDensity1",idSensor="RandomAirDensitySensor1",sensorCategory="virtual", sensorType="airDensity",frequency=f,sensorLocation="virtual",time=now,unit="g/m**3",value=airdensity)

        channel.basic_publish(exchange='amq.topic', routing_key='airdensity',body=message)
        print (message)

        time.sleep(f)