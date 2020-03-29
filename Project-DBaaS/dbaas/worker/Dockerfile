FROM base:latest
WORKDIR /app
COPY . /app
EXPOSE 8100
CMD ["/bin/sh","-c","cd /app && ([ ! -f data.db ] && python database.py) && python boss.py"]
