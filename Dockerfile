FROM ubuntu:14.04

RUN apt-get update -qq \
    && apt-get install -y --no-install-recommends build-essential python-dev mlocate git libxml2-dev libxslt1-dev zlib1g-dev links2 python-pip

RUN updatedb

ADD esprit /esprit
ADD magnificent-octopus /magnificent-octopus
ADD python-client-sword2 /python-client-sword2

RUN pip install -e /esprit
RUN pip install -e /magnificent-octopus
RUN pip install -e /python-client-sword2

COPY dependencies.txt /dependencies/lodestone.txt
RUN pip install -r /dependencies/lodestone.txt

ADD . /lodestone
COPY docker.cfg /lodestone/local.cfg

# ENTRYPOINT ["/lodestone/docker-entrypoint.sh"]
ENTRYPOINT ["top", "-b"]
CMD ["-c"]