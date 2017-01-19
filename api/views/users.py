'''
Requests associated to Users
'''
from flask.views import MethodView
from flask import jsonify, request

from common.db_service import DBService
from common.exceptions import DBError, EntryNotFoundError, InvalidColumnsError
from common.status_codes import (STATUS_CREATED, STATUS_INTERNAL_ERROR,
                                 STATUS_NOT_FOUND, STATUS_OK, STATUS_INVALID_INPUT, STATUS_NO_INPUT)


class UsersAPI(MethodView):
    '''
    Exposes the 'users' api endpoint
    '''
    db_table = 'user'

    def get(self, user_id=None):
        '''
        Get the data for the user with the specified user_id.
        Get the data for all users.
        '''
        try:
            db_data = DBService().select_data(self.db_table, data_id=user_id)
        except EntryNotFoundError:
            return {
                'message': 'The user with id {} was not found'.format('user_id')
            }, STATUS_NOT_FOUND
        except DBError as error:
            return {
                'message': error.message
            }, STATUS_INTERNAL_ERROR
        response = jsonify(db_data)
        response.status_code = STATUS_OK
        return response

    def post(self):
        '''
        Create and add a new user
        '''
        data = request.form.to_dict()
        if len(data) == 0:
            return{'message': 'No data input provided'}, STATUS_NO_INPUT
        try:
            user_id = DBService().insert_data(self.db_table, **data)
        except InvalidColumnsError as invalid_columns_error:
            invalid_columns_str = ', '.join(invalid_columns_error.columns)
            message = 'Unexpected data input(s): [' + invalid_columns_str + ']'
            return {
                'message': message
            }, STATUS_INVALID_INPUT
        except DBError as error:
            return {
                'message': error.message
            }, STATUS_INTERNAL_ERROR
        return {
            'message': 'The user has been added successfully',
            'id': user_id
        }, STATUS_CREATED

    def put(self, user_id):
        '''
        Update the data for a user
        '''
        data = request.form.to_dict()
        if len(data) == 0:
            return {'message': 'No data input provided'}, STATUS_NO_INPUT
        try:
            DBService().update_data(table=self.db_table, data_id=user_id, new_data=data)
        except EntryNotFoundError:
            return {
                'message': 'The user with id {} was not found'.format(user_id)
            }, STATUS_NOT_FOUND
        except InvalidColumnsError as invalid_columns_error:
            invalid_columns_str = ', '.join(invalid_columns_error.columns)
            message = 'Unexpected data input(s): [' + invalid_columns_str + ']'
            return {'message': message}, STATUS_INVALID_INPUT
        except DBError as error:
            return {'message': error.message}, STATUS_INTERNAL_ERROR

    def delete(self, user_id):
        '''
        Delete a user
        '''
        try:
            DBService().delete_data(table=self.db_table, data_id=user_id)
        except EntryNotFoundError:
            return {
                'message': 'The user with id {} was not found'.format(user_id)
            }, STATUS_NOT_FOUND
        except DBError as error:
            return {'message': error.message}, STATUS_INTERNAL_ERROR