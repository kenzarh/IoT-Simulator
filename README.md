# IoT simulator using RabbitMQ

## This repository

This repository simulates IoT data exchanges using a RabbitMQ broker. 

It contains a Docker image for RabbitMQ that enables the MQTT protocol and gives some definitions by creating 4 queues: temperature, pressure, humidity and airdensity, each one with one binding with arouting key similar to the name of the queue.
This docker image enables rabbitmq-management that essentially offers an interface for managing and monitoring the exchanges (port 15672).

The three python codes: "random_pressure_sensor.py", "random_humidity_sensor.py" and "random_airdensity_sensor.py" generate random sensors measurements and send the to the RabbitMQ Broker.

Then, the program "temperature_sensor_CNN_model.py" gets these measurements from the Broker, predicts the temperature using a CNN model and sends the value to the Broker.

All the exchanged messages are in an XML format according to the the Open Data Format (O-DF). The used format is in the "messages_format.xml" file.

## Setup

This setup assumes you already have docker-compose and docker installed.

```
cd rabbitmq_container
docker-compose up
```

## Execution

```
open http://$(docker-machine ip default):15672/
```
and use the login

```
username: admin
password: admin
```
Then run the python programs: "random_pressure_sensor.py", "random_humidity_sensor.py", "random_airdensity_sensor.py" and "temperature_sensor_CNN_model.py".
