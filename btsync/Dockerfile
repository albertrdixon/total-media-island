FROM debian:testing
MAINTAINER Albert Dixon <albert.dixon@schange.com>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get install -y --no-install-recommends curl
RUN curl -#kL https://download-cdn.getsyncapp.com/stable/linux-x64/BitTorrent-Sync_x64.tar.gz |\
    tar xvz -C /usr/local/bin

RUN curl -#kL https://github.com/albertrdixon/tmplnator/releases/download/v2.0.0/tnator-linux-amd64.tar.gz |\
    tar xvz -C /usr/local/bin

ADD configs /templates
ADD scripts/* /usr/local/bin/
RUN chmod a+rx /usr/local/bin/* &&\
    mkdir -p /btsync/.sync

ENTRYPOINT ["docker-entry"]
CMD ["bash"]

EXPOSE 8888 55555
ENV UI_PORT     8888
ENV LISTEN_PORT 55555
