#!/bin/bash
sleep 2
mongod &
sleep 5
service apache2 start
service mysql restart
sleep 2
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
sleep 3
tailf debug.log
