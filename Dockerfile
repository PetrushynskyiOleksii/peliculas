FROM python:3.9.0

ENV TZ=Europe/Kiev
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN mkdir /server

COPY requirements.txt /server

RUN pip install --upgrade pip && \
    pip install -r /server/requirements.txt

WORKDIR /server
