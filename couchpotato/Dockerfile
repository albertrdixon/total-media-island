FROM python:2.7.9
MAINTAINER Albert Dixon <albert.dixon@schange.com>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get install -y --no-install-recommends --force-yes \
    git ca-certificates wget \
    unar unzip locales curl dnsmasq

RUN dpkg-reconfigure locales && \
    locale-gen C.UTF-8 && \
    /usr/sbin/update-locale LANG=C.UTF-8

RUN curl -#kL https://github.com/albertrdixon/tmplnator/releases/download/v2.0.0/tnator-linux-amd64.tar.gz |\
    tar xvz -C /usr/local/bin

RUN curl -#kL https://github.com/albertrdixon/escarole/releases/download/v0.1.0/escarole-linux.tgz |\
    tar xvz -C /usr/local/bin

RUN virtualenv venv
ADD requirements.txt requirements.txt
RUN venv/bin/pip install -r requirements.txt && rm requirements.txt

RUN git clone -v git://github.com/RuudBurger/CouchPotatoServer.git /couchpotato

RUN apt-get purge -y --auto-remove \
    gcc libc6-dev libsqlite3-dev libssl-dev \
    make xz-utils zlib1g-dev
RUN apt-get autoremove -y && apt-get autoclean -y &&\
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ADD bashrc /root/.bashrc
ADD configs /templates
ADD scripts/* /usr/local/bin/
RUN mkdir /data &&\
    chown root:root /usr/local/bin/* &&\
    chmod a+rx /usr/local/bin/*

WORKDIR /couchpotato
ENTRYPOINT ["docker-entry"]
CMD ["docker-start"]
EXPOSE 5050

ENV PATH                 /usr/local/bin:$PATH
ENV OPEN_FILE_LIMIT      32768
ENV SUPERVISOR_LOG_LEVEL INFO
ENV UPDATE_FREQUENCY     86400
ENV COUCHPOTATO_HOME     /couchpotato
ENV COUCHPOTATO_CHANNEL  master
ENV CP_DATA_DIR          /data
ENV CP_CONFIG            /data/settings.conf
ENV CP_PID_FILE          /data/couchpotato.pid
