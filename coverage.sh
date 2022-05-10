#!/bin/bash
coverage run ./manage.py test

coverage xml
curl -Os https://uploader.codecov.io/latest/linux/codecov
chmod +x codecov
./codecov
exec $@
