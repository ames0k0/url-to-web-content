FROM ubuntu:24.04

WORKDIR /u2wc

RUN apt update && apt install -y python3.12 python3-pip

COPY requirements.txt src/server.py ./

RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

EXPOSE 8888

CMD [ "python3", "server.py" ]
