FROM rabbitmq:3-management

RUN apt-get update && apt-get install --no-install-recommends -y python3 python3-pip && rm -rf /var/lib/apt/lists/*
#RUN setcap cap_net_bind_service=+ep /usr/bin/python3.8

WORKDIR /home/

COPY requirements.txt /home/
COPY server.py /home/

CMD ["pip3","install","-r", "requirements.txt"]
CMD ["python3", "server.py"]
