# This file implements all the needed classes for running a simulation from a configuration file

from threading import Thread
import time
from time import time as tm
import pika

class ThreadWithReturnValue(Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return

class Simulation (object):

    def __init__(self,configurationFile,connection_parameters):
        self.connection_parameters=connection_parameters
        self.configurationFile = configurationFile

    def runSimulation(self):

        import math

        messages_number_list = []
        deleted_messages_list = []
        altered_messages_list = []
        stops_list = []
        stops_duration_list = []
        filtred_values_list = []

        import json
        file = open(self.configurationFile)
        configs = json.load(file)

        import threading

        global sentMessages 
        sentMessages = threading.Condition()
        sentMessages = 0

        simulationConditionsStop = configs["Simulation"]["Simulation stop"]
        global messagesNumberBeforeSimulationStop
        messagesNumberBeforeSimulationStop = math.inf
        elapsedTimeBeforeSimulationStop = math.inf
        elapsedTimeBeforeSimulationStopUnit = "s"
        from functions import time_in_seconds
        secondsElapsedBeforeSimulationStop = time_in_seconds(math.inf,"s")
        numberOfMessagesFinalStop = NumberOfMessagesFinalStop(name="None",value=math.inf)
        timeElapsedfinalStop = TimeElapsedfinalStop (name="None",value=math.inf)

        for simulationConditionStop in simulationConditionsStop:
            type = simulationConditionStop["Name"]
            if (type == "messages_number"):
                sentMessagesBeforeStop = SentMessagesBeforeStop(type,simulationConditionStop["Value"])
                messagesNumberBeforeSimulationStop = simulationConditionStop["Value"]
              
            elif (type == "time_elapsed"):
                timeElapsedBeforeStop = TimeElapsedBeforeStop(type,simulationConditionStop["Value"])
                elapsedTimeBeforeSimulationStop = simulationConditionStop["Value"]
                elapsedTimeBeforeSimulationStopUnit = simulationConditionStop["Value unit"]
                secondsElapsedBeforeSimulationStop = time_in_seconds(elapsedTimeBeforeSimulationStop,elapsedTimeBeforeSimulationStopUnit)
 
        sensors = configs ["Sensors"]

        threads = []

        # Calculate elapsed time - part 1
        from time import time as tm
        start_time = tm()

        # Loop over the sensors list
        for sensor in sensors:

            sensor_name = sensor["Sensor name"]
            sensorType = sensor["sensorType"]

            deleteDataPerturbation = DeleteDataPerturbation(name="perturbationName",secondsBetweenTwoPerturbationsType="value",secondsBetweenTwoPerturbationsInterval=[math.inf])
            alterDataPerturbation = AlterDataPerturbation(name="perturbationName",secondsBetweenTwoPerturbationsType="value",secondsBetweenTwoPerturbationsInterval=[math.inf])
            temporarySensorStop = TemporarySensorStop(name="perturbationName",secondsBetweenTwoPerturbationsType="value",secondsBetweenTwoPerturbationsInterval=[math.inf],stopDurationValue=0,stopDurationUnit="s")

            measurement = sensor["Measurement"]
            datatype = sensor["Data type"]
            unit = sensor["Unit"]
            dataInterval = sensor["Data interval"]
            secondsBetweenTwoMessages = sensor["Seconds between two messages"]
            sendingRoutingKey = sensor["sendingRoutingKey"]

            numberOfMessagesFinalStop = NumberOfMessagesFinalStop(name="None",value=math.inf)
            timeElapsedfinalStop = TimeElapsedfinalStop (name="None",value=math.inf)

            filters = []
            filtersInConfig = sensor["Filters"]
            for filter in filtersInConfig:
                    if (filter["Type"]=="Low-pass"):
                        name = filter["Name"]
                        filtredValue = filter["Settings"]["Max value"]
                        lowPassFilter = LowPassFilter(name=name,filtredValue=filtredValue)
                        filters.append(lowPassFilter)
                    elif (filter["Type"]=="High-pass"):
                        name = filter["Name"]
                        filtredValue = filter["Settings"]["Min value"]
                        highPassFilter = HighPassFilter(name=name,filtredValue=filtredValue)
                        filters.append(highPassFilter)

            perturbations = sensor["Perturbations"]
            for perturbation in perturbations:
                    type = perturbation ["Name"]
                    if (type == "delete_data"):
                        perturbationName = "Delete Data"
                        secondsBetweenTwoPerturbationsType = perturbation["Seconds between two deletions type"]
                        secondsBetweenTwoPerturbationsInterval = perturbation["Seconds between two deletions interval"]
                        deleteDataPerturbation = DeleteDataPerturbation(name=perturbationName,secondsBetweenTwoPerturbationsType=secondsBetweenTwoPerturbationsType,secondsBetweenTwoPerturbationsInterval=secondsBetweenTwoPerturbationsInterval)
                    elif (type == "alter_data"):
                        perturbationName = "Alter Data"
                        secondsBetweenTwoPerturbationsType = perturbation["Seconds between two alterations type"]
                        secondsBetweenTwoPerturbationsInterval = perturbation["Seconds between two alterations interval"]
                        alterDataPerturbation = AlterDataPerturbation(name=perturbationName,secondsBetweenTwoPerturbationsType=secondsBetweenTwoPerturbationsType,secondsBetweenTwoPerturbationsInterval=secondsBetweenTwoPerturbationsInterval)
                    elif (type == "stop"):
                        perturbationName = "Temporary Stop"
                        secondsBetweenTwoStopsType = perturbation["Seconds between two stops type"]
                        secondsBetweenTwoStopsInterval = perturbation["Seconds between two stops interval"]
                        stopDurationValue = perturbation["Stop duration value"]
                        stopDurationUnit = perturbation["Stop duration unit"]
                        temporarySensorStop = TemporarySensorStop(name=perturbationName,secondsBetweenTwoPerturbationsType=secondsBetweenTwoStopsType,secondsBetweenTwoPerturbationsInterval=secondsBetweenTwoStopsInterval,stopDurationValue=stopDurationValue,stopDurationUnit=stopDurationUnit)

            finalStopOptions = sensor["Final Stop"]
            for finalStop in finalStopOptions:
                        if(finalStop["Name"]) == "messages_number":
                            numberOfMessagesFinalStop = NumberOfMessagesFinalStop(name=finalStop["Name"],value=finalStop["Number of messages"])
                        elif(finalStop["Name"]) == "time_elapsed":
                            timeElapsedfinalStop = TimeElapsedfinalStop (name=finalStop["Name"],value=finalStop["Elaspsed Time In Seconds"])

            if (sensorType == "RandomEditor"):
                sensor = RandomNumericalSensor (name=sensor_name,measurement=measurement,datatype=datatype,unit=unit,location="virtual",dataInterval=dataInterval,secondsBetweenTwoMessages=secondsBetweenTwoMessages,sendingRoutingKey=sendingRoutingKey)

            elif (sensorType == "TemperaturePredictor"):
                sensor = TemperaturePredictor (name=sensor_name,measurement=measurement,datatype=datatype,unit=unit,location="virtual",dataInterval=dataInterval,secondsBetweenTwoMessages=secondsBetweenTwoMessages,sendingRoutingKey=sendingRoutingKey,receivingRoutingKey=sensor["receivingRoutingKey"],modelFile="CNNmodel")

            thread = ThreadWithReturnValue(target=sensor.runSensor, args=(self.connection_parameters,start_time,secondsElapsedBeforeSimulationStop,numberOfMessagesFinalStop,timeElapsedfinalStop,deleteDataPerturbation,alterDataPerturbation,temporarySensorStop,filters,))
            threads.append(thread)
            thread.start()

        # Waiting for all threads to finish
        for thread in threads:

            L = thread.join()
            print(L)
            [sensor_name,number_of_sent_messages , seconds_elapsed , number_of_filtred_values , number_of_deleted_messages , number_of_altered_messages , number_of_stops , total_stops_duration] = L
            messages_number_list.append(number_of_sent_messages)
            deleted_messages_list.append(number_of_deleted_messages)
            altered_messages_list.append(number_of_altered_messages)
            stops_list.append(number_of_stops)
            stops_duration_list.append(total_stops_duration)
            filtred_values_list.append(number_of_filtred_values)
                    
        # Initialize metrics list
        metrics = []

        # Add the simulation title
        simulation_title = configs ["Simulation"]["Name"]
        metrics.append(simulation_title)

        # Calculate elapsed time 2
        end_time = tm()
        seconds_elapsed = end_time - start_time
        timeElapsed = TimeElapsed (name="Elapsed Time" , formula = "Simulation duration" , value=seconds_elapsed)
        metrics.append(timeElapsed.value)

        # Total number of sent messages in the whole simulation
        sentMessages = SentMessages (name="Sent Messages",formula="Total messags sent",sentMessagesPerSensor=messages_number_list)
        metrics.append(sentMessages.calculateValue())

        # Debit of sent messages
        total_messages_number = sentMessages.calculateValue()
        debit_messages = total_messages_number / seconds_elapsed
        metrics.append(debit_messages)

        # Total number of deleted messages in the whole simulation
        deletedMessages = DeletedMessages (name="Deleted Messages",formula="Total of deleted messags",deletedMessagesPerSensor=deleted_messages_list)
        metrics.append(deletedMessages.calculateValue())

        total_deleted_messages = deletedMessages.calculateValue()

        # Debit of deleted messages
        debit_deleted_messages = total_deleted_messages / seconds_elapsed
        metrics.append(debit_deleted_messages)


        # Total number of altered messages in the whole simulation
        alteredMessages = AlteredMessages(name="Altered Messages",formula="Total altered messages",alteredMessagesPerSensor=altered_messages_list)
        metrics.append(alteredMessages.calculateValue())

        total_altered_messages = alteredMessages.calculateValue()

        # Debit of altered messages
        debit_altered_messages = total_altered_messages / seconds_elapsed
        metrics.append(debit_altered_messages)

        # Total number of stops in the whole simulation
        stopsNumber = StopsNumber(name="Stops Number",formula="Total numbr of stops",stopsNumberPerSensor=stops_list)
        metrics.append(stopsNumber.calculateValue())

        total_stops = stopsNumber.calculateValue()

        # Debit of stops
        debit_stops = total_stops / seconds_elapsed
        metrics.append(debit_stops)

        # Total duration of stops in the whole simulation
        stopsDuration = StopsDuration (name="Stops duration",formula="Total stops duration",stopsDurationPerSensor=stops_duration_list)
        metrics.append(stopsDuration.calculateValue())

        # Total uses of filters in the whole simulation
        filtredValues = FiltredValues (name="Filtred Values",formula="Total number of filtred values",filtredValuesPerSensor=filtred_values_list)
        metrics.append(filtredValues.calculateValue())

        print (metrics)

        # Writing metrics values in the csv file:
        from csv import writer  
        with open('output_metrics.csv', 'a') as f_object:
            writer_object = writer(f_object)
            writer_object.writerow(metrics)
            f_object.close()

class AbstractSensor(object):
    def __init__(self,name,measurement,datatype,unit,location,dataInterval,secondsBetweenTwoMessages,sendingRoutingKey):
        self.name = name
        self.measurement=measurement
        self.datatype = datatype
        self.unit = unit
        self.location = location
        self.dataInterval = dataInterval
        self.secondsBetweenTwoMessages = secondsBetweenTwoMessages
        self.sendingRoutingKey=sendingRoutingKey
    def runSensor(self,connection_parameters,start_time,secondsElapsedBeforeSimulationStop,numberOfMessagesFinalStop,timeElapsedfinalStop,DeleteDataPerturbation,AlterDataPerturbation,TemporarySensorStop,filters=[]):
        raise NotImplementedError('Subclasses must override the method!')

class RandomNumericalSensor(AbstractSensor):
    def runSensor(self,connection_parameters,start_time,secondsElapsedBeforeSimulationStop,numberOfMessagesFinalStop,timeElapsedfinalStop,DeleteDataPerturbation,AlterDataPerturbation,TemporarySensorStop,filters=[]):
        global sentMessages
        global messagesNumberBeforeSimulationStop
        simulation_start_time = start_time
        import random
        import pika
        import datetime
        import time
        from time import time as tm
        from functions import send_data
        min = self.dataInterval[0]
        max = self.dataInterval[1]
        number_of_sent_messages = 0 
        seconds_elapsed = 0
        number_of_filtred_values = 0
        number_of_deleted_messages = 0
        number_of_altered_messages = 0
        number_of_stops = 0
        total_stops_duration = 0
        start_time = tm()
        time_delete_data_1 = tm()
        time_alter_data_1 = tm()
        time_stop_1 = tm()
        elapsed_time_from_simulation_start = 0
        import threading
        lock = threading.Lock()
        while ((numberOfMessagesFinalStop.generateStop(number_of_sent_messages)==False) and (timeElapsedfinalStop.generateStop(seconds_elapsed)==False) and (elapsed_time_from_simulation_start<secondsElapsedBeforeSimulationStop) and (sentMessages<messagesNumberBeforeSimulationStop)):
                value = random.uniform(min,max)
                for filter in filters:
                    valueAfterFilter = filter.applyFilter(value)
                    if (value!=valueAfterFilter):
                        number_of_filtred_values = number_of_filtred_values + 1
                        value = valueAfterFilter
                now = datetime.datetime.now().timestamp()
                time_delete_data_2 = tm()
                elapsedTimeAfterDeleteData = time_delete_data_2 - time_delete_data_1
                if (DeleteDataPerturbation.generatePerturbation(elapsedTimeAfterDeleteData) == False):
                    time.sleep(self.secondsBetweenTwoMessages)
                    time_alter_data_2 = tm()
                    elapsedTimeAfterAlterData = time_alter_data_2 - time_alter_data_1
                    if (AlterDataPerturbation.generatePerturbation(elapsedTimeAfterAlterData,value) == False):
                        message = send_data(typeObject=self.measurement,idObject="Random"+self.measurement+str(number_of_sent_messages+1),idSensor=self.name,sensorCategory="virtual", sensorType="Random"+self.measurement,secondsBetweenTwoMessages=self.secondsBetweenTwoMessages,sensorLocation="virtual",time=now,unit=self.unit,value=value)
                        time_stop_2 = tm()
                        elapsedTimeAfterStop = time_stop_2 - time_stop_1
                        stop_duration = TemporarySensorStop.generatePerturbation(elapsedTimeAfterStop)
                        if (stop_duration != -1):
                            time.sleep(stop_duration)
                            time_stop_1 = tm()
                            number_of_stops = number_of_stops + 1
                            total_stops_duration = total_stops_duration + stop_duration
                        if ((elapsed_time_from_simulation_start<secondsElapsedBeforeSimulationStop) and (sentMessages<messagesNumberBeforeSimulationStop)):
                            connection = pika.BlockingConnection(connection_parameters)
                            channel = connection.channel()
                            channel.basic_publish(exchange='amq.topic', routing_key=self.sendingRoutingKey,body=message)
                            sentMessages = sentMessages + 1
                            number_of_sent_messages = number_of_sent_messages + 1
                    else:
                        alteredValue = AlterDataPerturbation.generatePerturbation(elapsedTimeAfterDeleteData,value)
                        time_alter_data_1 = tm()
                        message = send_data(typeObject=self.measurement,idObject="Random"+self.measurement+str(number_of_sent_messages+1),idSensor=self.name,sensorCategory="virtual", sensorType="Random"+self.measurement,secondsBetweenTwoMessages=self.secondsBetweenTwoMessages,sensorLocation="virtual",time=now,unit=self.unit,value=alteredValue)
                        number_of_altered_messages = number_of_altered_messages + 1
                elif (DeleteDataPerturbation.generatePerturbation(elapsedTimeAfterDeleteData) == True):
                    number_of_deleted_messages = number_of_deleted_messages + 1
                    time_delete_data_1 = tm()
                end_time = tm()
                seconds_elapsed = end_time - start_time
                elapsed_time_from_simulation_start = tm() - simulation_start_time
            
        return [self.name,number_of_sent_messages , seconds_elapsed , number_of_filtred_values , number_of_deleted_messages , number_of_altered_messages , number_of_stops , total_stops_duration]

class AbstractEditorConsumerSensor (AbstractSensor):
    def __init__(self,name,measurement,datatype,unit,location,dataInterval,secondsBetweenTwoMessages,sendingRoutingKey,receivingRoutingKey):
        super(AbstractSensor, self).__init__()
        self.receivingRoutingKey = receivingRoutingKey
    def runSensor(self,connection_parameters,start_time,secondsElapsedBeforeSimulationStop,numberOfMessagesFinalStop,timeElapsedfinalStop,DeleteDataPerturbation,AlterDataPerturbation,TemporarySensorStop,filters=[]):
        raise NotImplementedError('Subclasses must override the method!')

class TemperaturePredictor (AbstractEditorConsumerSensor):
    def __init__(self,name,measurement,datatype,unit,location,dataInterval,secondsBetweenTwoMessages,sendingRoutingKey,receivingRoutingKey,modelFile):
        super(AbstractEditorConsumerSensor, self).__init__(name,measurement,datatype,unit,location,dataInterval,secondsBetweenTwoMessages,sendingRoutingKey)
        self.receivingRoutingKey = receivingRoutingKey
        self.modelFile = modelFile
    def runSensor(self,connection_parameters,start_time,secondsElapsedBeforeSimulationStop,numberOfMessagesFinalStop,timeElapsedfinalStop,DeleteDataPerturbation,AlterDataPerturbation,TemporarySensorStop,filters=[]):
        global sentMessages
        global messagesNumberBeforeSimulationStop
        simulation_start_time = start_time
        import datetime
        import time
        from time import time as tm
        from functions import send_data
        min = self.dataInterval[0]
        max = self.dataInterval[1]
        number_of_sent_messages = 0 
        seconds_elapsed = 0
        number_of_filtred_values = 0
        number_of_deleted_messages = 0
        number_of_altered_messages = 0
        number_of_stops = 0
        total_stops_duration = 0
        start_time = tm()
        time_delete_data_1 = tm()
        time_alter_data_1 = tm()
        time_stop_1 = tm()
        elapsed_time_from_simulation_start = 0
        while ((numberOfMessagesFinalStop.generateStop(number_of_sent_messages)==False) and (timeElapsedfinalStop.generateStop(seconds_elapsed)==False) and (elapsed_time_from_simulation_start<secondsElapsedBeforeSimulationStop) and (sentMessages<messagesNumberBeforeSimulationStop)):
            connection = pika.BlockingConnection(connection_parameters)
            channel = connection.channel() 
            # Get air density value
            method_frame, header_frame, body = channel.basic_get(queue = self.receivingRoutingKey[0]) 
            while not method_frame:
                method_frame, header_frame, body = channel.basic_get(queue = self.receivingRoutingKey[0]) 
            channel.basic_ack(method_frame.delivery_tag)        
            import xml.etree.ElementTree as ET
            parser = ET.XMLParser()
            tree = ET.ElementTree(ET.fromstring(body.decode('utf-8'), parser=parser)) 
            root = tree.getroot()
            airdensity = float(root[0][2][1].text) 
            print("airdensity:",airdensity)

            # Get humidity value
            method_frame, header_frame, body = channel.basic_get(queue = self.receivingRoutingKey[1]) 
            while not method_frame:
                method_frame, header_frame, body = channel.basic_get(queue = self.receivingRoutingKey[1]) 
            channel.basic_ack(method_frame.delivery_tag)      
            import xml.etree.ElementTree as ET
            parser = ET.XMLParser()
            tree = ET.ElementTree(ET.fromstring(body.decode('utf-8'), parser=parser)) 
            root = tree.getroot()
            humidity = float(root[0][2][1].text) 

            # Get the pressure value
            method_frame, header_frame, body = channel.basic_get(queue = self.receivingRoutingKey[2])   
            while not method_frame:
                method_frame, header_frame, body = channel.basic_get(queue = self.receivingRoutingKey[2]) 
            channel.basic_ack(method_frame.delivery_tag)      
            import xml.etree.ElementTree as ET
            parser = ET.XMLParser()
            tree = ET.ElementTree(ET.fromstring(body.decode('utf-8'), parser=parser)) 
            root = tree.getroot()
            pressure = float(root[0][2][1].text)
            print("pressure:",pressure)
           
            # Predicting the temperature
            X = [[float(airdensity),float(humidity),float(pressure)]]
            import pickle
            loaded_model = pickle.load(open("temperature_model.sav", 'rb'))
            value = loaded_model.predict(X)
        
            for filter in filters:
                valueAfterFilter = filter.applyFilter(value)
                if (value!=valueAfterFilter):
                    number_of_filtred_values = number_of_filtred_values + 1
                    value = valueAfterFilter
            now = datetime.datetime.now().timestamp()
            time_delete_data_2 = tm()
            elapsedTimeAfterDeleteData = time_delete_data_2 - time_delete_data_1
            if (DeleteDataPerturbation.generatePerturbation(elapsedTimeAfterDeleteData) == False):
                time.sleep(self.secondsBetweenTwoMessages)
                time_alter_data_2 = tm()
                elapsedTimeAfterAlterData = time_alter_data_2 - time_alter_data_1
                if (AlterDataPerturbation.generatePerturbation(elapsedTimeAfterAlterData,value) == False):
                    message = send_data(typeObject=self.measurement,idObject="Predictor"+self.measurement+str(number_of_sent_messages+1),idSensor=self.name,sensorCategory="virtual", sensorType="Predictor"+self.measurement,secondsBetweenTwoMessages=self.secondsBetweenTwoMessages,sensorLocation="virtual",time=now,unit=self.unit,value=value)
                    time_stop_2 = tm()
                    elapsedTimeAfterStop = time_stop_2 - time_stop_1
                    stop_duration = TemporarySensorStop.generatePerturbation(elapsedTimeAfterStop)
                    if (stop_duration != -1):
                        time.sleep(stop_duration)
                        time_stop_1 = tm()
                        number_of_stops = number_of_stops + 1
                        total_stops_duration = total_stops_duration + stop_duration
                    channel.basic_publish(exchange='amq.topic', routing_key=self.sendingRoutingKey,body=message)
                    sentMessages = sentMessages + 1
                    number_of_sent_messages = number_of_sent_messages + 1
                else:
                    alteredValue = AlterDataPerturbation.generatePerturbation(elapsedTimeAfterDeleteData,value)
                    time_alter_data_1 = tm()
                    message = send_data(typeObject=self.measurement,idObject="Random"+self.measurement+str(number_of_sent_messages+1),idSensor=self.name,sensorCategory="virtual", sensorType="Random"+self.measurement,secondsBetweenTwoMessages=self.secondsBetweenTwoMessages,sensorLocation="virtual",time=now,unit=self.unit,value=alteredValue)
                    number_of_altered_messages = number_of_altered_messages + 1
            elif (DeleteDataPerturbation.generatePerturbation(elapsedTimeAfterDeleteData) == True):
                number_of_deleted_messages = number_of_deleted_messages + 1
                time_delete_data_1 = tm()
            end_time = tm()
            seconds_elapsed = end_time - start_time
            elapsed_time_from_simulation_start = tm() - simulation_start_time
        return [self.name,number_of_sent_messages , seconds_elapsed , number_of_filtred_values , number_of_deleted_messages , number_of_altered_messages , number_of_stops , total_stops_duration]

class AbstractFilter(object):
    def __init__(self,name,filtredValue):
        self.name=name
        self.type=type
        self.filtredValue=filtredValue
    def applyFilter(self,value):
        raise NotImplementedError('Subclasses must override the method!')

class LowPassFilter (AbstractFilter):
    def applyFilter(self,value):
        if value > self.filtredValue:
            return(self.filtredValue)
        else: 
            return(value)

class HighPassFilter (AbstractFilter):
    def applyFilter(self,value):
        if value < self.filtredValue:
            return(self.filtredValue)
        else: 
            return(value)

class AbstractPerturbation(object):
    def __init__(self,name,secondsBetweenTwoPerturbationsType,secondsBetweenTwoPerturbationsInterval):
        self.name = name
        self.secondsBetweenTwoPerturbationsType = secondsBetweenTwoPerturbationsType
        self.secondsBetweenTwoPerturbationsInterval = secondsBetweenTwoPerturbationsInterval
    def generatePerturbation(self,elapsedTimeAfterPerturbation):
        raise NotImplementedError('Subclasses must override the method!')

class DeleteDataPerturbation(AbstractPerturbation):
    def generatePerturbation(self,elapsedTimeAfterPerturbation):
        if (self.secondsBetweenTwoPerturbationsType == "value"):
            secondsBetweenTwoPerturbations = self.secondsBetweenTwoPerturbationsInterval[0]
        elif (self.secondsBetweenTwoPerturbationsType == "random"):
            import random
            secondsBetweenTwoPerturbations = random.uniform(self.secondsBetweenTwoPerturbationsInterval[0],self.secondsBetweenTwoPerturbationsInterval[1])
        if (elapsedTimeAfterPerturbation >= secondsBetweenTwoPerturbations):
            return True
        else:
            return False

class AlterDataPerturbation(AbstractPerturbation):
    def generatePerturbation(self,elapsedTimeAfterPerturbation,initialMeasure):
        if (self.secondsBetweenTwoPerturbationsType == "value"):
            secondsBetweenTwoPerturbations = self.secondsBetweenTwoPerturbationsInterval[0]
        elif (self.secondsBetweenTwoPerturbationsType == "random"):
            import random
            secondsBetweenTwoPerturbations = random.uniform(self.secondsBetweenTwoPerturbationsInterval[0],self.secondsBetweenTwoPerturbationsInterval[1])
        if (elapsedTimeAfterPerturbation >= secondsBetweenTwoPerturbations):
            return (initialMeasure + initialMeasure * 0.1)
        else:
            return False

class TemporarySensorStop(AbstractPerturbation):
    def __init__(self,name,secondsBetweenTwoPerturbationsType,secondsBetweenTwoPerturbationsInterval,stopDurationValue,stopDurationUnit):
        AbstractPerturbation.__init__(self,name,secondsBetweenTwoPerturbationsType,secondsBetweenTwoPerturbationsInterval)
        self.stopDurationValue = stopDurationValue
        self.stopDurationUnit = stopDurationUnit
    def generatePerturbation(self,elapsedTimeAfterPerturbation):
        if (self.secondsBetweenTwoPerturbationsType == "value"):
            secondsBetweenTwoStops = self.secondsBetweenTwoPerturbationsInterval[0]
        elif (self.secondsBetweenTwoPerturbationsType == "random"):
            import random
            secondsBetweenTwoStops = random.uniform(self.secondsBetweenTwoPerturbationsInterval[0],self.secondsBetweenTwoPerturbationsInterval[1])
        if (elapsedTimeAfterPerturbation >= secondsBetweenTwoStops):
            from functions import time_in_seconds
            return time_in_seconds(value=self.stopDurationValue,unit=self.stopDurationUnit)
        else:
            return (-1)        

class AbstractSensorFinalStop(object):
    def __init__(self,name,value):
        self.name = name
        self.value = value
    def generateStop(self,valueFromSensor):
        raise NotImplementedError('Subclasses must override the method!')

class NumberOfMessagesFinalStop (AbstractSensorFinalStop):
    def generateStop(self,valueFromSensor):
        # valueFromSensor in this class is the number of messages the sensor has sent
        if (self.value>valueFromSensor):
            return False
        else:
            return True

class TimeElapsedfinalStop (AbstractSensorFinalStop):
    def generateStop(self,valueFromSensor):
        # valueFromSensor in this class is the sensor operating time
        if (self.value>valueFromSensor):
            return False
        else:
            return True

class AbstractSimulationFinalStop(object):
    def __init__(self,name,value):
        self.name = name
        self.value = value

class TimeElapsedBeforeStop(AbstractSimulationFinalStop):
    def __init__(self,name,value):
        super(AbstractSimulationFinalStop, self).__init__()

class SentMessagesBeforeStop(AbstractSimulationFinalStop):
    def __init__(self,name,value):
        super(AbstractSimulationFinalStop, self).__init__()
        

class AbstractMetric (object):
    def __init__(self,name,formula):
        self.name = name
        self.formula = formula
    def calculateValue(self):
        raise NotImplementedError('Subclasses must override the method!')
 

class TimeElapsed (AbstractMetric):
    def __init__(self,name,formula,value):
        super(AbstractMetric, self).__init__()
        self.value = value
    def calculateValue(self):
        return (self.value)


class SentMessages (AbstractMetric):
    def __init__(self,name,formula,sentMessagesPerSensor):
        super(AbstractMetric, self).__init__()
        self.sentMessagesPerSensor = sentMessagesPerSensor
    def calculateValue(self):
        total_messages_number = 0
        messages_number_list = self.sentMessagesPerSensor
        for n in messages_number_list:
            total_messages_number = total_messages_number + n
        return (total_messages_number)

class DeletedMessages (AbstractMetric):
    def __init__(self,name,formula,deletedMessagesPerSensor):
        super(AbstractMetric, self).__init__()
        self.deletedMessagesPerSensor = deletedMessagesPerSensor
    def calculateValue(self):
        total_deleted_messages = 0
        deleted_messages_list = self.deletedMessagesPerSensor
        for n in deleted_messages_list:
            total_deleted_messages = total_deleted_messages + n
        return (total_deleted_messages)

class StopsNumber (AbstractMetric):
    def __init__(self,name,formula,stopsNumberPerSensor):
        super(AbstractMetric, self).__init__()
        self.stopsNumberPerSensor = stopsNumberPerSensor
    def calculateValue(self):
        total_stops = 0
        stops_list = self.stopsNumberPerSensor
        for n in stops_list:
            total_stops = total_stops + n
        return (total_stops)
        
class StopsDuration (AbstractMetric):
    def __init__(self,name,formula,stopsDurationPerSensor):
        super(AbstractMetric, self).__init__()
        self.stopsDurationPerSensor = stopsDurationPerSensor
    def calculateValue(self):
        total_stops_duration = 0
        stops_duration_list = self.stopsDurationPerSensor
        for n in stops_duration_list:
            total_stops_duration = total_stops_duration + n
        return(total_stops_duration)

class AlteredMessages (AbstractMetric):
    def __init__(self,name,formula,alteredMessagesPerSensor):
        super(AbstractMetric, self).__init__()
        self.alteredMessagesPerSensor = alteredMessagesPerSensor
    def calculateValue(self):
        total_altered_messages = 0
        altered_messages_list = self.alteredMessagesPerSensor
        for n in altered_messages_list:
            total_altered_messages = total_altered_messages + n
        return(total_altered_messages)

class FiltredValues (AbstractMetric):
    def __init__(self,name,formula,filtredValuesPerSensor):
        super(AbstractMetric, self).__init__()
        self.filtredValuesPerSensor = filtredValuesPerSensor
    def calculateValue(self):
        total_filtred_values = 0
        filtred_values_list = self.filtredValuesPerSensor
        for n in filtred_values_list:
            total_filtred_values = total_filtred_values + n
        return(total_filtred_values)