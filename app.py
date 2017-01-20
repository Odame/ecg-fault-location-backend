'''
The main entry point of the entire application
'''
from logging import error as log_error
# from logging import info as log_info
from os import environ as env
from sqlite3 import connect as connect_sqlite

from flask import Flask, abort, g
from psycopg2 import connect as connect_postgresql
from psycopg2 import OperationalError
from psycopg2.extras import RealDictCursor
# from werkzeug.local import LocalProxy

from common import config
from common.status_codes import STATUS_INTERNAL_ERROR
from common.db_service import DBService as _DBService


app = Flask(__name__)
app.config.from_object(config)


def get_db_connection():
    '''
    Create a new database connection if one doesn't exist already
    and return it.
    '''
    with app.app_context():
        _db_connection = getattr(g, '_db_connection', None)
        if _db_connection is None:
            try:
                if app.config['DEBUG'] is True:
                    # we are in debug mode, so we connect to the sqlite db file
                    _db_connection = connect_sqlite('sqlite.db', isolation_level=None)
                    log_error("CONNECTED TO SQLITE DATABASE")
                else:
                    # we are in production so use the db connection
                    # parameters defined in the DATABASE_URL environmen
                    # variable
                    _db_connection = connect_postgresql(
                        env.get('DATABASE_URL'), cursor_factory=RealDictCursor)
                    log_error(
                        "**********CONNECTED TO HEROKU POSTGRES DATABASE**********")
            except OperationalError as error:
                log_error('app.py >> get_db_connection(): ' + error.message)
                abort(STATUS_INTERNAL_ERROR)
            g._db_connection = _db_connection
        return _db_connection

# DB_CONNECTION = LocalProxy(get_db_connection)

# Create a DBService and make it a local proxy
# A local proxy can be accessed safely across multiple
# threads in a single process
DB_SERVICE = _DBService(
    get_db_connection(), 'SQLITE' if app.config['DEBUG'] else 'POSTGRESQL'
)


def register_api(view, endpoint, url, key='id', key_type='int'):
    '''
    Register the url(s) for an typical api endpoint.
    Use this function to register flask MethodViews only
    The urls that will be added by default are:
    url                   {GET POST}
    url/<pk_type:pk>      {GET PUT DELETE}
    '''
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, defaults={key: None},
                     view_func=view_func, methods=['GET', ])
    app.add_url_rule(url, view_func=view_func, methods=['POST', ])
    app.add_url_rule('%s/<%s:%s>' % (url, key_type, key), view_func=view_func,
                     methods=['GET', 'PUT', 'DELETE'])


# # we register the urls for the flask app
from api.views.poles import PolesAPI
from api.views.users import UsersAPI
register_api(UsersAPI, 'users_api', '/users', key='user_id')
register_api(PolesAPI, 'poles_api', '/poles', key='pole_id')


@app.teardown_appcontext
def teardown_db_connection(exception):
    _db_connection = getattr(g, '_db_connection', None)
    if _db_connection:
        log_error("DATABASE CONNECTION CLOSED >> application teardown")
        _db_connection.close()

@app.teardown_request
def teardown_db_connec(exception):
    _db_connection = getattr(g, '_db_connection', None)
    if _db_connection:
        log_error("DATABASE CONNECTION CLOSED >> request teardown")
        _db_connection.close()


# we now actually start the app
if __name__ == '__main__':
    app.run()
