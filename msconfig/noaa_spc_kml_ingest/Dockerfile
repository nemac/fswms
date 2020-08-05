FROM ubuntu:18.04

MAINTAINER NEMAC Dev Team <nemac@unca.edu>

USER root

SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y \
      build-essential \
      software-properties-common \
      python3 \
      python3-pip

RUN add-apt-repository ppa:ubuntugis/ubuntugis-unstable

RUN apt-get install -y \
      libgdal-dev=3.0.4+dfsg-1~bionic0 \
      gdal-bin=3.0.4+dfsg-1~bionic0

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal

ENV C_INCLUDE_PATH=/usr/include/gdal

RUN pip3 install GDAL==3.0.4

CMD cd /run && python3 ./ingest_kml.py 3
