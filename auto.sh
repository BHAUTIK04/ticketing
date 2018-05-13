#!/bin/bash

docker build -t "ticketapi" .
docker run -d -p 8000:8000 -p 27017:27018 -p 3306:3307 --name "ticketapi" ticketapi

