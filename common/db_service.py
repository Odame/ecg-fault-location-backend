'''
CRUD operations on the underlying database
'''
from logging import error as log_error

from common.exceptions import (
    DBError, EntryNotFoundError, InvalidColumnsError, InvalidTableError)
from app import DB_CONNECTION as db_connection


class DBService(object):
    '''
    Contains functions for performing varios CRUD operations on the underlying database
    '''

    def __init__(self):
        self.db_connection = db_connection
        self.cursor = db_connection.cursor()
        self.table_column_mappings = {
            'user_account': [
                'user_account_id', 'email', 'full_name', 'uid', 'is_active'
            ],
            'pole': [
                'pole_id', 'pole_number',
                'lat', 'long',
            ]
        }

    # @staticmethod
    def is_valid_table(self, table):
        '''
        Returns True if 'table' is a valid table name in the database
        '''
        return table in self.table_column_mappings
    
    def get_invalid_columns(self, table, columns):
        '''
        Return the elements in 'columns' that are not part of the
        actual columns of 'table' in the database
        '''
        valid_columns = set(self.table_column_mappings.get(table, []))
        input_columns = set(columns)
        invalid_columns = list(input_columns.difference(valid_columns))
        return invalid_columns
    
    def get_valid_columns(self, table):
        '''
        Return list of the valid columns for table whose name is specified as 'table'
        If 'table' is not found in the database, an empty list is returned
        '''
        return self.table_column_mappings.get(table, [])
    
    def insert_data(self, table, **kwargs):
        '''
        INSERT data into 'table' in the database.
        The data for the entry is provided via 'kwargs'.
        '''
        insert_query = '''
            INSERT INTO {table} 
                ({columns_to_insert})
            VALUES 
                ({values_placeholders})
            RETURNING {table}_id
        '''
        if not self.is_valid_table(table):
            raise InvalidTableError(table)
        columns_to_insert = ', '.join(kwargs.keys())
        invalid_columns = self.get_invalid_columns(table, kwargs.keys())
        if len(invalid_columns) > 0:
            raise InvalidColumnsError(table, invalid_columns)
        values_to_insert = kwargs.values()
        values_placeholders = ', '.join(['%s'] * len(values_to_insert))
        insert_query = insert_query.format(
            table=table,
            columns_to_insert=columns_to_insert,
            values_placeholders=values_placeholders
        )
        insert_query = insert_query.replace('\n', '')
        try:
            with self.db_connection:  # required for auto commit/rollback
                self.cursor.execute(insert_query, values_to_insert)
                # get the id of the row we just inserted
                insert_id = self.cursor.fetchone()[0]
        except Exception as error:
            log_error('db_service.py >> insert_data() >> insert_query execution: ' + error.message)
            raise DBError(table, error)
        return insert_id

    # @staticmethod
    def update_data(self, table, data_id, new_data, exclude=None):
        '''
        UPDATE the data in 'table' with the specified 'data_id' the database.
        List of columns that should be exempted from the update are specified in 'exclude'.
        'new_data' represent the column:new_value pairs that must be updated.
        NB: This function is meant to update only a single row in the database
        '''
        update_query = '''
            UPDATE {table} 
            SET {columns_placeholders}
            WHERE {table}_id=%s
        '''
        if not self.is_valid_table(table):
            raise InvalidTableError(table)
        invalid_columns = self.get_invalid_columns(table, new_data.keys())
        if len(invalid_columns) > 0:
            raise InvalidColumnsError(table, invalid_columns)
        illegal_columns = None
        if exclude:
            illegal_columns = list(
                set(exclude).intersection(set(new_data.keys())))
        if illegal_columns:  # if illegal_columns is not null
            raise InvalidColumnsError(table, illegal_columns)
        # we generate the query that will be run against the database.
        # construct the column-value pairs
        # column_value_pairs_placeholders: 'column_1=%s, column_2=%s, ...'
        column_value_pairs_placeholders = ', '.join(
            ['{c}=%s'.format(c=c) for c in new_data.keys()])
        update_query = update_query.format(
            table=table,
            columns_placeholders=column_value_pairs_placeholders
        )
        # query_params: contains all the parameters that will be passed to the query during
        # execution
        query_params = new_data.values() + [data_id]
        # execute the query
        try:
            with self.db_connection:  # required for auto commit/rollback
                self.cursor.execute(update_query, query_params)
                affected_rows = self.cursor.rowcount
                if affected_rows != 1:
                    raise EntryNotFoundError(table, data_id)
        except EntryNotFoundError as entry_not_found_error:
            raise entry_not_found_error
        except Exception as error:
            log_error('db_service.py >> update_data() >> update_query execution: ' + error.message)
            raise DBError(table, error)

    # @staticmethod
    def delete_data(self, table, data_id):
        '''
        DELETE the data in 'table' with the specified 'data_id' from the database.
        '''
        if not self.is_valid_table(table):
            raise InvalidTableError(table)
        # query to be executed if the table has no 'is_active' column.
        # this means the data cannot just be flagged as inactive in the
        # database
        delete_query = '''
            DELETE FROM {table} 
            WHERE {table}_id=%(data_id)s
        '''
        # query to be executed if the table has an 'is_active' column.
        # this mean the data can be flagged as inactive in the database
        deactivate_query = '''
            UPDATE {table} 
            SET is_active=FALSE 
            WHERE {table}_id=%(data_id)s AND is_active=TRUE
        '''
        can_deactivate = 'is_active' in self.get_valid_columns(table)
        query_to_execute = deactivate_query if can_deactivate else delete_query
        query_to_execute = query_to_execute.format(table=table)
        query_to_execute = query_to_execute.replace('\n', '')
        try:
            with self.db_connection:  # required for auto commit/rollback
                self.cursor.execute(
                    query_to_execute, {'data_id': data_id})
                affected_rows = self.cursor.rowcount
                if affected_rows != 1:
                    raise EntryNotFoundError(table, data_id)
        except EntryNotFoundError as entry_not_found_error:
            raise entry_not_found_error
        except Exception as error:
            log_error('db_service.py >> delete_data() >> delete_query execution: ' + error.message)
            raise DBError(table, error)

    def select_data(self, table, data_id=None, exclude=None, **kwargs):
        '''
        SELECT data from a single 'table' in the database.
        The returned data can be filtered by passing column:value pairs
        as filters via kwargs. Filters will be ANDED.
        NB: This function does not cater for cases where data has to be fetched by
        joining multiple tables
        '''
        select_query = '''
        SELECT {columns_to_select} FROM {table} 
        '''
        # check if the table name is valid in the database
        if not self.is_valid_table(table):
            raise InvalidTableError(table)
        valid_columns = self.get_valid_columns(table)
        if exclude:
            columns_to_select = ', '.join(
                list(
                    set(valid_columns).difference(set(exclude))
                )
            )
        else:
            columns_to_select = ', '.join(valid_columns)

        select_query = select_query.format(
            table=table, columns_to_select=columns_to_select)
        db_data = None
        if data_id:
            kwargs.update({'{table}_id'.format(table=table): db_data})
        filter_columns = kwargs.keys()
        filter_params = kwargs.values()
        # check if we have to modify the select_query to handle filters
        # we know we have to do filtering if kwargs is not empty
        if len(filter_columns) > 0:
            invalid_filter_columns = self.get_invalid_columns(
                table, filter_columns)
            # if there are columns in the filter params that are invalid
            if len(invalid_filter_columns) > 0:
                raise InvalidColumnsError(table, invalid_filter_columns)
            placeholders = ' AND '.join(
                ['{c}=%s'.format(c=c) for c in filter_columns]
            )
            select_query += ' WHERE ' + placeholders
            # if 'table' has an 'is_active' column,
            # we make sure we select only the active data entries
            if 'is_active' in valid_columns:
                select_query += ' AND is_active=TRUE '
        else:
            # if 'table' has an 'is_active' column,
            # we make sure we select only the active data entries
            if 'is_active' in valid_columns:
                select_query += ' WHERE is_active=TRUE'
        # remove new line characters from the select_query string
        select_query = select_query.replace('\n', '')
        try:
            with self.db_connection:  # required for auto commit/rollback
                self.cursor.execute(select_query, filter_params)
                db_data = self.cursor.fetchall()
        except Exception as error:
            log_error('db_service.py >> select_data() >> select_query execution: ' + error.message)
            raise DBError(table, error)
        if data_id:
            try:
                return db_data[0]
            except IndexError:
                raise EntryNotFoundError(table, data_id)
        return db_data
