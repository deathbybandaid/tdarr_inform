FROM python:3-alpine

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt -r web-requirements.txt

EXPOSE 5004

VOLUME /config

USER 1000:1000

# Automatically create the basic config file if it doesn't exist - makes life from Docker easier
CMD ([ ! -e /config/config.ini ] && python tdarr_inform.py --config /config/config.ini --setup) && python tdarr_inform.py --config /config/config.ini --mode server
