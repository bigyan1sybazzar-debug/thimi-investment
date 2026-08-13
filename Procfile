release: python manage.py migrate && python manage.py sync_member_emails
web: gunicorn backend.wsgi --log-file -

