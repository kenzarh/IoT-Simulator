# IoT simulator using RabbitMQ

## This repository

This repository simulates IoT data exchanges using a RabbitMQ broker. 

It contains a Docker image for RabbitMQ that enables the MQTT protocol and gives some definitions by creating 4 queues: temperature, pressure, humidity and airdensity, each one with one binding with a routing key's name similar to the name of the queue.
This docker image enables rabbitmq-management that essentially offers an interface for managing and monitoring the exchanges (port 15672).

"random_airdensity_sensor_container", "random_humidity_sensor_container" and "random_pressure_sensor_container" are three docker images that generate random sensors measurements for air density, humidity and pressure and send the to the corresponding queue of the RabbitMQ Broker.

Then, the docker image "temperature_sensor_CNN_model_container" gets these measurements from the Broker, predicts the temperature using a CNN model and sends the value to the Broker.

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
Then run the docker images: "random_pressure_sensor_container", "random_humidity_sensor_container", "random_airdensity_sensor_container" and "temperature_sensor_CNN_model_container".
