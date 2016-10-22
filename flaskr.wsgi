#!/usr/bin/python3
import sys
import os

sys.path.insert(1,'/home/george/Dropbox/python_dev/flaskr')

from flaskr.flaskr import app as application
application.secret_key = 'development key'
