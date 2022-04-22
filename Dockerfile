FROM python:3.9.12-alpine3.15

MAINTAINER Klemens Schueppert "schueppi@envot.io"

WORKDIR /devisor/

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./devisor /devisor/devisor/
COPY ./start_devisor.py /devisor/start_devisor.py

ENV PYTHONUNBUFFERED TRUE
ENV HOST broker
ENV PORT 1883
ENV NAME eot

ENTRYPOINT python start_devisor.py -host ${HOST} -port ${PORT} -name ${NAME}
