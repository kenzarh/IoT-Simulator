import pika
# Connection to the RabbitMQ Broker
credentials = pika.PlainCredentials('admin', 'admin')
parameters = pika.ConnectionParameters("host.docker.internal",5672,'/',credentials)
#parameters = pika.ConnectionParameters("localhost",5672,'/',credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

from classes import Simulation
simulation = Simulation("simulation_config.json",channel,connection)
simulation.runSimulation()