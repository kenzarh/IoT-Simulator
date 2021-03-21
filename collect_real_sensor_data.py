import pika # The RabbitMQ client library for Python

import time

credentials = pika.PlainCredentials('admin', 'admin')
parameters = pika.ConnectionParameters("localhost",5672,'/',credentials)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()

from urllib.request import urlopen
import json

url_sensors = "http://dafflon.fr:5000/api/listSensor"
sensors = json.loads(urlopen(url_sensors).read())['SensorList']

def metadata (data,time,name,type,url):
  metadata = {
  "sensor":{
  "name":name,
  "Category":[
  "located",
  "real",
  "..."
  ],
  "Type":type,
  "Hz":1,
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

def light():
  url = "http://dafflon.fr:5000/api/Sensor/light/data/LIGHT"
  endpoint = '/api/Sensor/light/data/LIGHT'
  response = json.loads(urlopen(url).read())
  data = response['data-light-intensity']

  import time
  import datetime
  date_string = response['time']
  date = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
  time = time.mktime(date.timetuple())

  name = [sensor['name'] for sensor in sensors if sensor['endpoint']==endpoint]

  type = 'brightness'

  return data,time,name,type,url



while True:
        
        data,time,name,type,url = light()
        metadata = metadata (data,time,name,type,url)
        channel.basic_publish(exchange='amq.topic', routing_key='light',body=json.dumps(data1))

        time.sleep(5)
