#!/usr/bin/env bash

apt-get update && \
apt-get install -y \
  fcgiwrap \
  nginx \
  software-properties-common

add-apt-repository -y ppa:ubuntugis/ppa

apt-get update && \
apt-get install -y \
  gdal-bin=2.4.2+dfsg-1~bionic0 \
  mapserver-bin=7.4.1-1~bionic0

pip3 install mapscript

# Set up the Nginx Mapserver configuration.
cd /tmp/build 
cp ./mapserver.conf /etc/nginx/sites-available/mapserver.conf
ln -s /etc/nginx/sites-available/mapserver.conf /etc/nginx/sites-enabled/mapserver.conf
rm /etc/nginx/sites-enabled/default

# Set up the run script for starting services.
cp ./run.sh /usr/local/bin/run.sh
chmod +x /usr/local/bin/run.sh

# Clean up APT when done.
apt-get autoremove -y
apt-get clean -y
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
