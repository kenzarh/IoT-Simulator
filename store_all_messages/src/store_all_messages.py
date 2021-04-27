# Connection to the RabbitMQ Broker
import pika # The RabbitMQ client library for Python
credentials = pika.PlainCredentials('admin', 'admin')
parameters = pika.ConnectionParameters("host.docker.internal",5672,'/',credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

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
        data = str(self.response)
        return (data)

import pymongo # Importing the library for writing from Python to MongoDB database
# Connect to database
client = pymongo.MongoClient("host.docker.internal:27017")
database = client["rabbitmq_messages"]
collection = database["messages"]  


while True:

        # Get a message
        message = SensorValue('all_messages').call()
        #print(message)

        # Put the message in the database
        dict = { "message": message}
        collection.insert_one(dict)
        #print(list(collection.find())[:])