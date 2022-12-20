#!/bin/bash
docker-compose build
docker-compose run web python3 manage.py collectstatic --noinput
docker-compose run web python3 manage.py migrate
docker-compose run web python3 manage.py createsuperuser
