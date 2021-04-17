# Importing the CNN model
import tensorflow as tf 
model = tf.keras.models.load_model("CNN.model")

# Connection to the RabbitMQ Broker
import pika # The RabbitMQ client library for Python
credentials = pika.PlainCredentials('admin', 'admin')
parameters = pika.ConnectionParameters("host.docker.internal",5672,'/',credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

import time
import datetime
from message import send_data
import xml.etree.ElementTree as ET

# A class for retrieving data from queues
class SensorValue(object):
    def __init__(self,queue):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters("host.docker.internal",5672,'/',pika.PlainCredentials('admin', 'admin')))
        self.channel = self.connection.channel()
        self.channel.basic_consume(queue=queue,on_message_callback=self.on_response,auto_ack=True)
    def on_response(self, ch, method, props, body):
            self.response = body
    def call(self):
        self.response = None
        while self.response is None:
            self.connection.process_data_events()
        parser = ET.XMLParser()
        tree = ET.ElementTree(ET.fromstring(self.response, parser=parser)) 
        root = tree.getroot()
        value = root[0][2][1].text
        return (value)

# Each f seconds, retrieve data (air density, humidity and air pressure) from the broker, predict the temperature and send it to the broker

f = 5 # Messages frequency

while True:

        # Get the air density value
        airdensity = SensorValue('airdensity').call()
        print(airdensity)

        # Get the humidity value
        humidity = SensorValue('humidity').call()
        print(humidity)

        # Get the pressure value
        pressure = SensorValue('pressure').call()
        print(pressure)

        # Predicting the temperature
        X = [[[float(airdensity)],[float(humidity)],[float(pressure)]]]
        temperature = int(model.predict (X))
        print(temperature)

        now = datetime.datetime.now().timestamp()
        
        message = send_data(typeObject="Temperature",idObject="VirtualTemperature1",idSensor="VirtualSensorTemperature1",sensorCategory="virtual", sensorType="temperature",frequency=f,sensorLocation="virtual",time=now,unit="◦C",value=temperature)

        channel.basic_publish(exchange='amq.topic', routing_key='temperature',body=message)
        #print (message)

        time.sleep(f)