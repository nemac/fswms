FROM ubuntu:18.04

MAINTAINER NEMAC Dev Team <nemac@unca.edu>

USER root

EXPOSE 80

ADD ./build.sh /tmp/build/build.sh

RUN /tmp/build/build.sh

ADD . /tmp/build/

# Start the fcgi and web servers.
CMD ["/usr/local/bin/run.sh"]
