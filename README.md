# IoT simulator using RabbitMQ

## This repository

This repository simulates IoT data exchanges using a RabbitMQ broker. 

It contains a Docker image for RabbitMQ that enables the MQTT protocol and gives some definitions by creating a queue "queue.home" (for domotic sensors) and two bindings with the routing keys "light", "sound", "temperature", etc.
This docker image enables rabbitmq-management that essentially offers an interface for managing and monitoring the exchanges (port 15672).

The "sensor_model.py" programm gets real sensors data from the file "data.csv", predicts the temperature using a CNN algorithm and sends the predicted measure in an XML format- according to the the Open Data Format (O-DF)- to the RabbitMQ broker, precisely to the amq.topic exchange that sends it to the corresponding queue (here to the "temperature" queue) using the bindings.

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
Then run the "sensor_model.py" programm.
