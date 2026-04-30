release: python manage.py migrate && python manage.py collectstatic --noinput && python manage.py create_superuser_auto
web: gunicorn evaluaciones__nombre__estudiantes.wsgi --log-file -
