import os, sys
from google.appengine.api import users

os.environ["DJANGO_SETTINGS_MODULE"] = "dvk.settings"

ROOT_PATH = os.path.dirname(__file__)
sys.path.append(ROOT_PATH)

#from google.appengine.dist import use_library
#use_library('django', '1.1')
sys.path.insert(0, "django.zip")
from appenginepatcher.patch import patch_all, setup_logging

patch_all()
# Google App Engine imports.
from google.appengine.ext.webapp import util

# Force Django to reload its settings.
from django.conf import settings

settings._target = None

import django.core.handlers.wsgi
import django.core.signals
import django.dispatch.dispatcher

# Unregister the rollback event handler.

def main():
	# Create a Django application for WSGI.
	application = django.core.handlers.wsgi.WSGIHandler()

	# Run the WSGI CGI handler with that application.
	util.run_wsgi_app(application)

if __name__ == "__main__":
	main()