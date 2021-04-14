# Connection to the RabbitMQ Broker
import pika # The RabbitMQ client library for Python
credentials = pika.PlainCredentials('admin', 'admin')
parameters = pika.ConnectionParameters("localhost",5672,'/',credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Send a random air pressure value between 913 and 1016 every f seconds to the RabbitMQ Broker
min = 913
max = 1016
import random 
import time
import datetime
from message import send_data
while True:

        f = 5 # Messages frequency

        # Generating a random air pressure value between 913 and 1016
        pressure = random. uniform(min,max)
        #print (pressure)

        now = datetime.datetime.now().timestamp()
        
        message = send_data(typeObject="Pressure",idObject="RandomPressure1",idSensor="RandomPressureSensor1",sensorCategory="virtual", sensorType="pressure",frequency=f,sensorLocation="virtual",time=now,unit="mbar",value=pressure)

        channel.basic_publish(exchange='amq.topic', routing_key='pressure',body=message)
        print (message)

        time.sleep(f)