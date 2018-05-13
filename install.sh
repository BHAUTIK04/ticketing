#!/bin/bash

apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2930ADAE8CAF5059EE73BB4B58712A2291FA4AD5
echo "deb [ arch=amd64 ] http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.6 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.6.list
apt-get update -y
apt-get install mongodb-org -y
mkdir -p /data/db
mongod &


export DEBIAN_FRONTEND="noninteractive"
debconf-set-selections <<< "mysql-server mysql-server/root_password password root"
debconf-set-selections <<< "mysql-server mysql-server/root_password_again password root"
#service mysql restart
sleep 5
apt-get install mysql-server --force-yes -y
apt-get install libmysqlclient-dev --force-yes -y
pip install -r requirements.txt

#apt-get install mongodb --force-yes -y
mongod

echo "########create database##########"
service mysql restart
service mysql status 
echo "create database ticketing" | mysql -uroot -proot
