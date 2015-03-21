FROM debian:testing
MAINTAINER Albert Dixon <albert.dixon@schange.com>

RUN apt-get update
RUN apt-get install -y --no-install-recommends unzip wget &&\
    wget -O ngrok.zip --no-check-certificate \
    'https://api.equinox.io/1/Applications/ap_pJSFC5wQYkAyI0FIVwKYs9h1hW/Updates/Asset/ngrok.zip?os=linux&arch=amd64&channel=stable' &&\
    unzip -d /usr/local/bin ngrok.zip &&\
    rm -rf ngrok.zip /var/lib/apt/lists/* /tmp/* /var/tmp/*
ADD config /templates/
ADD scripts/* /usr/local/bin/
RUN chmod a+rx /usr/local/bin/*
ENTRYPOINT ["docker-entry"]
CMD ["docker-start"]

ENV COUCHPOTATO_PORT 5050
ENV SICKRAGE_PORT 8081
