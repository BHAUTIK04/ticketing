FROM ubuntu:14.04
RUN apt-get update -y
RUN apt-get install python-minimal --force-yes -y
RUN apt-get install python-dev --force-yes -y
RUN apt-get install python-pip --force-yes -y
RUN pip install django==1.11
RUN apt-get install apache2 --force-yes -y
EXPOSE 8000 27017 3306
COPY ticketing/ start.sh install.sh requirements.txt /
RUN chmod +x /start.sh /install.sh
RUN /install.sh
CMD ["/start.sh"]

