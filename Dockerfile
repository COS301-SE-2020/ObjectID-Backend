FROM python:3
ENV PYTHONUNBUFFERED 1


COPY ./compose/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./compose/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

RUN apt-get update && apt-get upgrade -y
RUN mkdir /code
WORKDIR /code
COPY . /code/
RUN pip install -r requirements/local.txt
ENTRYPOINT ["/entrypoint"]

# RUN python manage.py migrate
# RUN python manage.py collectstatic --noinput