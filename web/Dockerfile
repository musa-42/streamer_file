FROM ubuntu:latest

RUN apt-get update && apt-get install -y locales python3 python3-pip wget && rm -rf /var/lib/apt/lists/* \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8

ENV LANG en_US.utf8

COPY . /app

WORKDIR /app

RUN pip3 install -r requirements.txt

ENV PORT = 8080

EXPOSE 8080

#CMD gunicorn main:main --timeout 86400 -w 5 --bind 0.0.0.0:$PORT --worker-class aiohttp.GunicornWebWorker
