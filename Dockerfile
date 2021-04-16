FROM ubuntu:20.04
FROM python:3.8

WORKDIR /Netflix

EXPOSE 5000
ENV FLASK_ENV=development
ENV FLASK_APP=AppFile.py

ADD . /Netflix

RUN python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt
RUN ["apt-get", "update"]
RUN ["apt-get", "install", "-y", "libgl1-mesa-dev"]
RUN ["apt-get", "install", "-y", "vim"]
CMD ["flask", "run", "--host", "0.0.0.0"]