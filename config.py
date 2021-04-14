 # default config
import os

class BaseConfig(object):
    DEBUG = False
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
