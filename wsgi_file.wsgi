#! /usr/bin/python3.6

import logging
import sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/home/ray/philsite/')
sys.path.insert(0, "/home/ray/philsite/philsite")
print(sys.path)
from philsite import app as application
application.secret_key = 'anything you wish'
