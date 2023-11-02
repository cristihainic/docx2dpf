FROM python:3.11.6-slim-bullseye
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY . /app/
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice-writer \
    default-jre libreoffice-java-common

RUN pip install -r reqs.txt

CMD python convertor.py

EXPOSE 1488/tcp
EXPOSE 1488/udp
