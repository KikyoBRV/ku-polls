#!/bin/sh
python ./manage.py migrate

if [ -f "./data/polls-v4.json" ]; then
  python ./manage.py loaddata ./data/polls-v4.json
fi
if [ -f "./data/users.json" ]; then
  python ./manage.py loaddata ./data/users.json
fi
if [ -f "./data/votes-v4.json" ]; then
  python ./manage.py loaddata ./data/votes-v4.json
fi

python ./manage.py runserver 0.0.0.0:8000