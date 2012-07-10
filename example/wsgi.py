import os
import sys

webapp_dir = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.abspath(os.path.join(webapp_dir, os.path.pardir))
VENV = os.path.join(PATH, 'venv')

if PATH not in sys.path:
    sys.path.insert(0, PATH)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.settings")

activate_this = os.path.expanduser(os.path.join(VENV, "bin", "activate_this.py"))
execfile(activate_this, dict(__file__=activate_this))

#from django.core.wsgi import get_wsgi_application
#application = get_wsgi_application()

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
