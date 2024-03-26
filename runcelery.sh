#!/bin/sh

python3 -m celery -A saris worker -l info

