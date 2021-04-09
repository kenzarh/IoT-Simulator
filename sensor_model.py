# Importing the model
import tensorflow as tf 
model = tf.keras.models.load_model("C:\\Users\\dell\\Desktop\\IoT Simulator\\sensor_model\\CNN.model")

# Importing data (will be changed to collecting data from real sensors)
import pandas as pd
df = pd.read_csv("C:\\Users\\dell\\Desktop\\IoT Simulator\\sensor_model\\data.csv")
columns = ['T (degC)','p (mbar)','H2OC (mmol/mol)','rho (g/m**3)']
data = df[columns]
data = data.values
Y = data[:,0] # Temperatures
X = data [:,1:] # Features used to predict temperature 
X = X.reshape(X.shape[0], X.shape[1], 1)

# Function that creates the JSON message
def metadata (name,category,type,frequency,url,time,data):
  metadata = {
  "sensor":{
  "name":name,
  "Category":category,
  "Type":type,
  "Hz":frequency,
  "DataType":"Integer",
  "Location":{
    },
    "url":url,
    "port":5000
  },
  "data":{
  "Timestamp":time,
  "Data":data,
  "Trust Factor":1,
  "Scale Factor":1
  }
  }

  return metadata


# Sending the message to the RabbitMQ Broker

import pika # The RabbitMQ client library for Python
import time
from datetime import datetime
import json

credentials = pika.PlainCredentials('admin', 'admin')
parameters = pika.ConnectionParameters("localhost",5672,'/',credentials)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()

i = 1000 # Starting whith the raw i

while True:

        f = 5 # Messages frequency

        # Predicting the temperature
        temperature = int(model.predict (X[i:i+1,:]))
        

        now = datetime.now()
        now = now.strftime("%d/%m/%Y %H:%M:%S")


        message = metadata (name="Virtual temperature",category="virtual",type="temperature",frequency=f,url="XX",time=now,data=temperature)

        print(message)
        print(temperature)
        print(Y [i])

        channel.basic_publish(exchange='amq.topic', routing_key='temperature',body=json.dumps(message))

        i = i + 1

        time.sleep(f)
