#! /bin/sh
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
echo "dropped migrations"
rm collidersitedb
echo "rm databse"
python manage.py migrate
python manage.py createsuperuser
admin
a.piotrowski@g.pl
dupa1204
dupa1204
python manage.py runserver