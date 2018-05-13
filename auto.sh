#!/bin/bash

docker build -t "ticketapi" .
docker run -d -p 8001:8000 -p 27018:27017 -p 3307:3306 --name "ticketapi" ticketapi
