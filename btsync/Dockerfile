FROM debian:testing
MAINTAINER Albert Dixon <albert.dixon@schange.com>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get install -y --no-install-recommends curl
RUN curl -#kL http://download-new.utorrent.com/endpoint/btsync/os/linux-x64/track/stable |\
    tar xvz -C /usr/local/bin
RUN curl -#kL https://github.com/albertrdixon/tmplnator/releases/download/v1.0.0/tnator-linux-amd64.tar.gz |\
    tar xvz -C /usr/local/bin

ADD configs /templates
ADD scripts/* /usr/local/bin/
RUN chmod a+rx /usr/local/bin/* &&\
    mkdir /btsync

ENTRYPOINT ["docker-entry"]
CMD ["bash"]

EXPOSE 8888 55555
