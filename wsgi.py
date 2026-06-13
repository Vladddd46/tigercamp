# PythonAnywhere: paste into /var/www/vladddd46_pythonanywhere_com_wsgi.py

import os
import sys

path = '/home/vladddd46/habitatoo'
if path not in sys.path:
    sys.path.insert(0, path)

os.chdir(path)

from flask_app import app as application  # noqa: E402
