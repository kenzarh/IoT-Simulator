# Importing the CNN model
import tensorflow as tf 
model = tf.keras.models.load_model(".\CNN.model")

# Importing data (will be changed to collecting data from real sensors)
import pandas as pd
df = pd.read_csv('.\data.csv')
columns = ['T (degC)','p (mbar)','H2OC (mmol/mol)','rho (g/m**3)']
data = df[columns]
data = data.values
Y = data[:,0] # Temperatures
X = data [:,1:] # Features used to predict temperature 
X = X.reshape(X.shape[0], X.shape[1], 1)


# Sending the message to the RabbitMQ Broker
import pika # The RabbitMQ client library for Python
credentials = pika.PlainCredentials('admin', 'admin')
parameters = pika.ConnectionParameters("localhost",5672,'/',credentials)
#connection = pika.BlockingConnection(parameters)
#channel = connection.channel()

import time
import datetime
from message import send_data
import xml.etree.ElementTree as ET

i = 1000 # Starting whith the raw i

while True:

        f = 5 # Messages frequency

        # Predicting the temperature
        temperature = int(model.predict (X[i:i+1,:]))

        now = datetime.datetime.now().timestamp()
        
        message = send_data(typeObject="Temperature",idObject="VirtualTemperature1",idSensor="VirtualTemperature1",sensorCategory="virtual", sensorType="temperature",frequency=f,sensorLocation="virtual",time=now,unit="◦C",value=temperature)

        #channel.basic_publish(exchange='amq.topic', routing_key='temperature',body=message)
        print (message)

        i = i + 1

        time.sleep(f)