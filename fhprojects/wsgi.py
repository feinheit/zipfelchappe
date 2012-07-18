import os, sys

WEBAPP_DIR = os.path.dirname(os.path.abspath(__file__))
APP_BASEDIR = os.path.abspath(os.path.join(WEBAPP_DIR, os.path.pardir))

if APP_BASEDIR not in sys.path:
    sys.path.insert(0, APP_BASEDIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.settings")

activate_this = os.path.expanduser(os.path.join(APP_BASEDIR, "venv", "bin", "activate_this.py"))
execfile(activate_this, dict(__file__=activate_this))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fhprojects.settings")


from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
