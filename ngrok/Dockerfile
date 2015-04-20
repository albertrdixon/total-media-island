FROM debian:testing
MAINTAINER Albert Dixon <albert.dixon@schange.com>

ENV NGROK_VER 2.0.16

RUN apt-get update
RUN apt-get install -y --no-install-recommends unzip curl &&\
    curl -#kL -o ngrok.zip https://dl.ngrok.com/ngrok_${NGROK_VER}_linux_amd64.zip &&\
    unzip -d /usr/local/bin ngrok.zip &&\
    rm -rf ngrok.zip /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN curl -#kL https://github.com/albertrdixon/tmplnator/releases/download/v2.0.0/tnator-linux-amd64.tar.gz |\
    tar xvz -C /usr/local/bin

ADD configs /templates/
ADD scripts/* /usr/local/bin/
RUN chmod a+rx /usr/local/bin/*
ENTRYPOINT ["docker-entry"]
CMD ["docker-start"]
EXPOSE 4040

ENV COUCHPOTATO_PORT 5050
ENV SICKRAGE_PORT 8081
ENV PLEX_PORT 32400

ENV TLS           both
ENV LOG_LEVEL     info
ENV LOG_FMT       logfmt
ENV COMPRESS_CONN false
