#!/bin/bash
if [ $? -eq 0 ]
then
    docker --version | grep "Docker version"
    if [ $? -eq 0 ]
    then
        echo "docker existing"
    else
        echo "install docker"
	apt-get install docker.io -y
    fi
else
    echo "install docker" >&2
    apt-get install docker.io -y
fi
sleep 5
echo "Ticketapi image creation started"
docker build -t "ticketapi" .
echo "Image creation done"
docker run -d -p 8001:8000 -p 27018:27017 -p 3307:3306 --name "ticketapi" ticketapi
echo "App container is up and running on port 8001"
echo "You can access all apis using BASE-URL localhost:8001"
