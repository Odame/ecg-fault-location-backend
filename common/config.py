'''
All custom configurations for the flask app
'''
from os import environ as env

DEBUG = True if str(env.get('FLASK_DEBUG', '0')) == '1' else False

INDEX = 'https://odame.github.io/ecg-fault-location-backend/'
