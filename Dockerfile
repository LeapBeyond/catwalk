FROM python:3.7-slim-buster

MAINTAINER Leap Beyond <info@leapbeyond.ai>

RUN apt update -y && apt install -y nginx

WORKDIR /usr/src/app

RUN mkdir catwalk

COPY . catwalk/

RUN cd catwalk && pip install --upgrade pip && pip install --no-cache-dir .

ENV MODEL_PATH catwalk/example_models/rng
ENV SERVER_CONFIG=conf/application.yml
ENV SERVER_PORT=9090

CMD ["catwalk", "serve"]
