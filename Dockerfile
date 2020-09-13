FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY . /code/
RUN apt-get update && apt-get upgrade -y
RUN pip install -r requirements/local.txt