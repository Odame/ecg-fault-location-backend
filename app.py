'''
The main entry point of the entire application
'''
from logging import error as log_error
from os import environ as env
from sqlite3 import connect as connect_sqlite

from flask import Flask, abort, g
from psycopg2 import connect as connect_postgresql
from psycopg2 import OperationalError
from psycopg2.extras import RealDictCursor
from werkzeug.local import LocalProxy

from api.views.poles import PolesAPI
from api.views.users import UsersAPI
from common import config
from common.status_codes import STATUS_INTERNAL_ERROR

APP = Flask(__name__)
APP.config.from_object(config)


def connect_to_database():
    '''
    Create a connection to the underlying database and return it
    '''
    try:
        if APP.config['DEBUG'] is True:
            # we are in debug mode, so we connect to the sqlite db file

            conn = connect_sqlite('sqlite.db')
        else:
            # we are in production so use the db connection
            # parameters defined in the DATABASE_URL environmen variable
            conn = connect_postgresql(env.get('DATABASE_URL'), cursor_factory=RealDictCursor)
    except OperationalError as error:
        log_error('app.py >> get_db_connection(): ' + error.message)
        abort(STATUS_INTERNAL_ERROR)
    return conn

def get_db_connection():
    '''
    Create a new database connection if one doesn't exist already
    and return it.
    '''
    _db_connection = getattr(g, '_database', None)
    if _db_connection is None:
        _db_connection = g._database = connect_to_database()
    return _db_connection

DB_CONNECTION = LocalProxy(get_db_connection)

def register_api(view, endpoint, url, pk='id', pk_type='int'):
    '''
    Register the url(s) for an typical api endpoint.
    Use this function to register flask MethodViews only
    The urls that will be added by default are:
    url                   {GET POST}
    url/<pk_type:pk>      {GET PUT DELETE}
    '''
    view_func = view.as_view(endpoint)
    APP.add_url_rule(url, defaults={pk: None},
                     view_func=view_func, methods=['GET',])
    APP.add_url_rule(url, view_func=view_func, methods=['POST',])
    APP.add_url_rule('%s/<%s:%s>' % (url, pk_type, pk), view_func=view_func,
                     methods=['GET', 'PUT', 'DELETE'])

# we register the urls for the flask app
register_api(UsersAPI, 'users_api', '/users', pk='user_id')
register_api(PolesAPI, 'poles_api', '/poles', pk='pole_id')

# we now actually start the app
if __name__ == '__main__':
    APP.run()
