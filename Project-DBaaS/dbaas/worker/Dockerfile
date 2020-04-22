FROM base:latest
WORKDIR /app
COPY . /app
EXPOSE 80
CMD ["/bin/sh","-c","cd /app && ([ ! -f data.db ] && python database.py) && python boss.py"]