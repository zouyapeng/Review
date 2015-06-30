#!/bin/bash

/usr/bin/uwsgi --ini /var/www/review/uwsgi.ini
/usr/bin/service nginx restart

