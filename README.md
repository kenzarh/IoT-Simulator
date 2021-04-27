# IoT simulator with RabbitMQ

## This repository

This repository simulates IoT data exchanges using a RabbitMQ broker. 

It contains a Docker image for RabbitMQ that enables the MQTT protocol and gives some definitions by creating 4 queues: temperature, pressure, humidity and airdensity, each one with one binding with a routing key's name similar to the name of the queue, and a queue all_messages with a routing key # for capturing all the messages.
This Docker image enables rabbitmq-management that essentially offers an interface for managing and monitoring the exchanges (port 15672).

A Docker image for MongoDB is also enabled in this container for storing all the messages.

Mongo Express is used to visualise and manage MongoDB databases (port 8081)  

"random_airdensity_sensor", "random_humidity_sensor" and "random_pressure_sensor" are three docker containers that generate random sensors measurements for air density, humidity and pressure and send the to the corresponding queue of the RabbitMQ Broker.

Then, the docker container "temperature_sensor_CNN_model" gets these measurements from the Broker, predicts the temperature using a CNN model and sends the value to the Broker.

All the exchanged messages are in an XML format according to the the Open Data Format (O-DF). The used format is in the "messages_format.xml" file.

## Setup

This setup assumes you already have docker-compose and docker installed.

```
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