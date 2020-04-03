FROM python:3.7-slim-buster

ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

MAINTAINER Leap Beyond <info@leapbeyond.ai>
LABEL maintainer="info@leapbeyond.ai"

LABEL org.label-schema.schema-version="1.0"
LABEL org.label-schema.build-date=$BUILD_DATE
LABEL org.label-schema.name="catwalk"
LABEL org.label-schema.description="`catwalk` is a model wrapping and serving platform."
LABEL org.label-schema.vcs-url="https://github.com/LeapBeyond/catwalk/"
LABEL org.label-schema.vcs-ref=$VCS_REF
LABEL org.label-schema.vendor="Leap Beyond"
LABEL org.label-schema.version=$VERSION
LABEL org.label-schema.docker.cmd="docker run -d -p 9090:9090"
LABEL org.label-schema.docker.cmd.test="docker run --rm -it leapbeyondgroup/catwalk:latest catwalk test"
LABEL org.label-schema.docker.cmd.help="docker run --rm -it leapbeyondgroup/catwalk:latest catwalk --help"
LABEL org.label-schema.docker.params="MODEL_PATH=string path to the model to serve,RUN_TESTS=boolean flag to enable/disable tests on server startup,SERVER_CONFIG=string path to the server config YML file,SERVER_PORT=integer port to listen on"


RUN apt update -y && apt install -y nginx

WORKDIR /usr/src/app

RUN mkdir catwalk

COPY . catwalk/

RUN cd catwalk && pip install --upgrade pip && pip install --no-cache-dir .

ENV MODEL_PATH=catwalk/example_models/rng
ENV RUN_TESTS=true
ENV SERVER_CONFIG=false
ENV SERVER_PORT=9090

CMD ["catwalk", "serve"]
