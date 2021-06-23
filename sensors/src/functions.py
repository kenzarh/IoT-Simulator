# Formating data into an xml file

def send_data (typeObject,idObject,idSensor,sensorCategory,sensorType,secondsBetweenTwoMessages,sensorLocation,time,unit,value):

        # Importing the generic XML file
        import xml.etree.ElementTree as ET
        tree = ET.parse("messages_format.xml")
        root = tree.getroot()

        # Changing the parameters

        element1 = root[0]
        element1.set('type', typeObject)

        element2 = root[0][0]
        element2.text=idObject

        element3 = root[0][1][0][0][0]
        element3.text=idSensor

        element4 = root[0][1][0][1][0]
        element4.text=sensorCategory

        element5 = root[0][1][0][2][0]
        element5.text=sensorType

        element6 = root[0][1][0][3][0]
        element6.text=str(secondsBetweenTwoMessages)

        element7 = root[0][1][0][4][0]
        element7.text=sensorLocation

        element8 = root[0][2][0][0][0]
        element8.text=str(time)

        element9 = root[0][2][0][2][0]
        element9.text=unit

        element10 = root[0][2][1]
        element10.text=str(value)

        message = ET.tostring(root).decode()

        return message


# Function that transforms time to seconds. It takes the value and the unit and returns the value in seconds
def time_in_seconds (value,unit):

        if unit == "s":
                seconds = value
        elif unit == "ms":
                seconds = value/1000
        elif unit == "min":
                seconds = value*60
        elif unit == "h":
                seconds = value*3600
        return seconds

# A class for retrieving data from queues
import xml.etree.ElementTree as ET
import pika
class SensorValue(object):
    def __init__(self,queue):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters("host.docker.internal",5672,'/',pika.PlainCredentials('admin', 'admin')))
        #self.connection = pika.BlockingConnection(pika.ConnectionParameters("localhost",5672,'/',pika.PlainCredentials('admin', 'admin')))
        self.channel = self.connection.channel()
        self.channel.basic_consume(queue=queue,on_message_callback=self.on_response,auto_ack=False)
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