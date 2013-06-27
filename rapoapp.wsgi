import os
import sys	
sys.path.append('/home/rapoadmin/public_html/rapoproject/')
sys.path.append('/home/rapoadmin/public_html/rapoproject/rapoapp')
os.environ['DJANGO_SETTINGS_MODULE'] = 'rapoapp.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
