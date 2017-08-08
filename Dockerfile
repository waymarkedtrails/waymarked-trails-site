FROM ubuntu:17.04

RUN apt-get update && apt-get install --no-install-recommends -y \
    python3 python3-setuptools python3-psycopg2 python3-shapely python3-pip \
    python3-cairo python3-gi python3-gi-cairo gir1.2-pango-1.0 gir1.2-rsvg-2.0 \
    python3-gdal python3-scipy python3-yaml python3-wheel python3-pyosmium \
    curl gzip postgresql-client git nginx locales \
&& rm -rf /var/lib/apt/lists/*

RUN pip3 install SQLAlchemy==1.0.8 GeoAlchemy2==0.2.5 SQLAlchemy-Utils \
    CherryPy==3.8.0 Babel==2.2.0 Jinja2==2.8 Markdown==2.5.1 \
    webassets==0.11.1 cssutils==1.0.1

WORKDIR /opt
RUN git clone --depth=1 https://github.com/lonvia/osgende.git \
&& pip3 install osgende/

RUN mkdir -p /waymarkedtrails && \
    export DEBIAN_FRONTEND=noninteractive && \
    locale-gen en_US.UTF-8 && dpkg-reconfigure locales

ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'
WORKDIR /waymarkedtrails
CMD bash docker-startup.sh $STARTUP
