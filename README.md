# IoT simulator with RabbitMQ

## This repository

This repository simulates IoT data exchanges using a RabbitMQ broker. 

It contains a Docker image for RabbitMQ that enables the MQTT protocol and gives some definitions by creating 4 queues: temperature, pressure, humidity and airdensity, each one with one binding with a routing key's name similar to the name of the queue, and a queue all_messages with a routing key # for capturing all the messages.
This Docker image enables rabbitmq-management that essentially offers an interface for managing and monitoring the exchanges (port 15672).

Then, the docker container "sensors" runs the sensors specified in the configuration file.

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
