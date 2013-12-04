import os
import sys	
sys.path.append('/home/rapoadmin/public_html/devrapo/')
sys.path.append('/home/rapoadmin/public_html/devrapo/rapoapp')
os.environ['DJANGO_SETTINGS_MODULE'] = 'rapoapp.settings'
os.environ['LANG']='en_US.UTF-8'
os.environ['LC_ALL']='en_US.UTF-8'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
