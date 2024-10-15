FROM ubuntu:22.04


COPY ./docker/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

WORKDIR /src

COPY ./app/requirements /src/app/requirements
# Add samba-latest repository
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:linux-schools/samba4.17 && \
    apt-get update && \
    apt-get install python3-samba python3-pip  -y

RUN pip3 install -r app/requirements/requirements.txt

COPY ./app /src/app
ENTRYPOINT ["/entrypoint.sh"]