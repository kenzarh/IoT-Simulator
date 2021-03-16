# IoT simulator using RabbitMQ

## This repository

This repository simulates IoT data exchanges using a RabbitMQ broker. 

It contains a Docker image for RabbitMQ that enables the MQTT protocol and gives some definitions by creating a queue "queue.home" (for domotic sensors) and two bindings with the routing keys "light" and "sound".
This docker image enables rabbitmq-management that essentially offers an interface for managing and monitoring the exchanges (port 15672).

The "collect_real_sensor_data.py" programm sends real sensor data to the RabbitMQ broker, precisely to the amq.topic exchange that sends it to the corresponding queue using the bindings in a JSON format.

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
Then run the "collect_real_sensor_data.py" programm."# IoT-Simulator" 
"# IoT-Simulator" 
"# IoT-Simulator" 
