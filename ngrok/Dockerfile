FROM debian:testing
MAINTAINER Albert Dixon <albert.dixon@schange.com>

RUN apt-get update
RUN apt-get install -y --no-install-recommends unzip curl &&\
    curl -#kL \
    https://api.equinox.io/1/Applications/ap_pJSFC5wQYkAyI0FIVwKYs9h1hW/Updates/Asset/ngrok.zip?os=linux&arch=amd64&channel=stable &&\
    unzip -d /usr/local/bin ngrok.zip &&\
    rm -rf ngrok.zip /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN curl -#kL https://github.com/albertrdixon/tmplnator/releases/download/v1.0.0/tnator-linux-amd64.tar.gz |\
    tar xvz -C /usr/local/bin
ADD configs /templates/
ADD scripts/* /usr/local/bin/
RUN chmod a+rx /usr/local/bin/*
ENTRYPOINT ["docker-entry"]
CMD ["docker-start"]

ENV COUCHPOTATO_PORT 5050
ENV SICKRAGE_PORT 8081
