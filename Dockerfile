FROM ubuntu:bionic

MAINTAINER Helena Schmidt

ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8

RUN apt-get -y update -qq && \
    apt-get -y install locales && \
    locale-gen en_US.UTF-8 && \
    update-locale LANG=en_US.UTF-8 && \
    apt-get install -y python3-pip python3-pandas
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /tmp/* /var/tmp/*

WORKDIR /app

RUN pip3 install flask_bootstrap
RUN pip3 install flask_wtf
RUN pip3 install tzwhere
RUN pip3 install geopy
RUN pip3 install aiohttp
RUN pip3 install async_timeout

ADD webapp /app
ADD data /app/data
ADD pictogram /app/pictogram
COPY downloadJsonData.py /app/app/
COPY plotMeteogram.py /app/app/

EXPOSE 5003

ENTRYPOINT ["/bin/bash", "/app/webapp/startup.sh"]
