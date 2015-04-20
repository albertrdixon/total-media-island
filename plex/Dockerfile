FROM ubuntu:utopic
MAINTAINER Albert Dixon <albert.dixon@schange.com>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update -qq
RUN apt-get install --no-install-recommends -y --force-yes \
    gettext-base curl wget ca-certificates \
    avahi-daemon avahi-utils supervisor &&\
    apt-get autoclean -y &&\
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN curl -#kL https://github.com/albertrdixon/tmplnator/releases/download/v2.0.0/tnator-linux-amd64.tar.gz |\
    tar xvz -C /usr/local/bin

RUN curl -#kL https://github.com/albertrdixon/escarole/releases/download/v0.0.3/escarole-linux.tgz |\
    tar xvz -C /usr/local/bin

ADD bashrc /root/.bashrc
ADD configs /templates
ADD scripts/* /usr/local/bin/
RUN chown root:root /usr/local/bin/* &&\
    chmod a+rx /usr/local/bin/* &&\
    mkdir -p /plexupdate /plexmediaserver &&\
    touch /first_run

ENTRYPOINT ["docker-entry"]
CMD ["docker-start"]
VOLUME ["/plexmediaserver"]
EXPOSE 32400 1900 5353 32410 32412 32413 32414 32469

ENV OPEN_FILE_LIMIT     32768
ENV DOWNLOADDIR         /plexupdate
ENV FORCE               no
ENV PUBLIC              no
ENV AUTOINSTALL         yes
ENV RELEASE             64-bit
ENV URL_LOGIN           https://plex.tv/users/sign_in
ENV URL_DOWNLOAD        https://plex.tv/downloads?channel=plexpass
ENV URL_DOWNLOAD_PUBLIC https://plex.tv/downloads
ENV UPDATE_TIME         3:00

ENV PLEX_MEDIA_SERVER_HOME                    /usr/lib/plexmediaserver
ENV PLEX_MEDIA_SERVER_USER                    root
ENV PLEX_MEDIA_SERVER_APPLICATION_SUPPORT_DIR /plexmediaserver
ENV PLEX_MEDIA_SERVER_TMPDIR                  /tmp
ENV PLEX_MEDIA_SERVER_MAX_STACK_SIZE          4000
ENV PLEX_MEDIA_SERVER_MAX_PLUGIN_PROCS        6
