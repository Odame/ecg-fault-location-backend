'''
Custom Errors
'''
from os import environ as os_environ

from psycopg2 import errorcodes


class InvalidColumnsError(Exception):
    '''
    Indicates that column(s) are not valid for a particular database table.
    The name of the table is as given by 'table' attribute.
    The column(s) are as given by the 'columns' attribute.
    '''

    def __init__(self, table, invalid_columns):
        super(InvalidColumnsError, self).__init__("")
        invalid_columns_str = ', '.join(invalid_columns)
        self.message = "The table '{}' has no column(s) {}".format(
            table, invalid_columns_str)
        self.columns = invalid_columns
        self.table = table


class DBError(Exception):
    '''
    A wrapper class for errors raised as a result of db operations.
    All db errors in PostgreSQL have unique error codes
    For more info on PostgreSQL error codes, check:
    http://initd.org/psycopg/docs/errorcodes.html
    https://www.postgresql.org/docs/current/static/errcodes-appendix.html#ERRCODES-TABLE
    The table for which the error occurred is stored in DBError.table
    The error code resulting from the exception is stored in DBError.error_code
    '''

    def __init__(self, table, psycopg2_error):
        super(DBError, self).__init__("")
        self.message = psycopg2_error.message.replace('\n', '') if os_environ.get(
            'FLASK_DEBUG') else 'Internal server db error. Actual message has been logged on server'
        self.error_code = errorcodes.lookup(psycopg2_error.pgcode[:2])
        self.table = table


class EntryNotFoundError(Exception):
    '''
    This is the error thrown when an entry was not found in the database.
    May be associated to single-item UPDATE or DELETE operations.
    The id of the entry/item is stored in EntryNotFoundError.entry_id
    '''

    def __init__(self, table, entry_id):
        super(EntryNotFoundError, self).__init__("")
        self.message = "The {} with id {} was not found".format(
            table, entry_id)
        self.table = table
        self.entry_id = entry_id


class InvalidTableError(Exception):
    '''
    This is the error thrown when a given table cannot be found in the database.
    May be associated to any of the CRUD operations.
    The name of the invalid table is stored in InvalidTableError.table
    '''

    def __init__(self, table):
        super(InvalidTableError, self).__init__(
            "The table {} was not found in the database".format(table))
        self.table = table
