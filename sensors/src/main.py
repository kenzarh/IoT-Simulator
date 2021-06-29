import pika
# Connection to the RabbitMQ Broker
credentials = pika.PlainCredentials('admin', 'admin')
connection_parameters = pika.ConnectionParameters("host.docker.internal",5672,'/',credentials)

from classes import Simulation
simulation = Simulation("simulation_config.json",connection_parameters)
simulation.runSimulation()