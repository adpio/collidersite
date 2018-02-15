find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" - delete
echo "dropped migrations"
rm collidersitedb
echo "rm databse"
