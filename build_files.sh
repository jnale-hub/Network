pip install -r requirements.txt

# make migrations
python manage.py migrate 
python manage.py collectstatic