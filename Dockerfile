FROM openknowledge/ckan-dev:2.8

MAINTAINER Andres Vazquez <andres@data99.com.ar>

# Set timezone
ARG TZ=UTC
RUN cp /usr/share/zoneinfo/$TZ /etc/localtime
RUN echo $TZ > /etc/timezone

RUN apk add py-cryptography
RUN chown -R ckan:ckan $CKAN_STORAGE_PATH
COPY ckan/docker-entrypoint.d/* /docker-entrypoint.d/
ADD requirements.txt /requirements.txt

RUN pip install --upgrade pip && \
    pip install -e git+https://github.com/ckan/ckanext-harvest.git#egg=ckanext-harvest && \
    pip install -e git+https://github.com/ckan/ckanext-pages.git#egg=ckanext-pages && \
    pip install -e git+https://github.com/ckan/ckanext-xloader.git#egg=ckanext-xloader && \
    pip install -e git+https://github.com/avdata99/ckanext-siu-harvester.git#egg=ckanext-siu-harvester && \
    pip install -r /requirements.txt
