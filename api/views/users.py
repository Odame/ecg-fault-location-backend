'''
Requests associated to Users
'''
from flask import jsonify, make_response, request
from flask.views import MethodView

from app import DB_SERVICE as DBService
from common.exceptions import DBError, EntryNotFoundError, InvalidColumnsError
from common.status_codes import (STATUS_CREATED, STATUS_INTERNAL_ERROR,
                                 STATUS_INVALID_INPUT, STATUS_NO_INPUT,
                                 STATUS_NOT_FOUND, STATUS_OK)


class UsersAPI(MethodView):
    '''
    Exposes the 'users' api endpoint
    '''
    db_table = 'user'

    def get(self, user_id=None):
        '''
        Get the data for the User with the specified user_id.
        Get the data for all Users.
        '''
        try:
            db_data = DBService.select_data(self.db_table, data_id=user_id)
        except EntryNotFoundError:
            return make_response(
                jsonify(
                    {'message': 'The user with id {} was not found'.format('user_id')}),
                STATUS_NOT_FOUND
            )
        except DBError as error:
            return make_response(
                jsonify({'message': error.message}), STATUS_INTERNAL_ERROR
            )
        return make_response(jsonify(db_data), STATUS_OK)

    def post(self):
        '''
        Create and add a new user
        '''
        data = request.form.to_dict()
        if len(data) == 0:
            return make_response(
                jsonify({'message': 'No data input provided'}), STATUS_NO_INPUT
            )
        try:
            user_id = DBService.insert_data(self.db_table, **data)
        except InvalidColumnsError as invalid_columns_error:
            invalid_columns_str = ', '.join(invalid_columns_error.columns)
            message = 'Unexpected data input(s): [' + invalid_columns_str + ']'
            return make_response(
                jsonify({'message': message}), STATUS_INVALID_INPUT
            )
        except DBError as error:
            return make_response(
                jsonify({'message': error.message}), STATUS_INTERNAL_ERROR
            )
        return make_response(
            jsonify({'message': 'The user has been added successfully', 'id': user_id}),
            STATUS_CREATED
        )

    def put(self, user_id):
        '''
        Update the data for a user
        '''
        data = request.form.to_dict()
        if len(data) == 0:
            return make_response(
                jsonify({'message': 'No data input provided'}), STATUS_NO_INPUT
            )
        try:
            DBService.update_data(table=self.db_table,
                                  data_id=user_id, new_data=data)
        except EntryNotFoundError:
            return make_response(
                jsonify({'message': 'The user with id {} was not found'.format(user_id)}),
                STATUS_NOT_FOUND
            )
        except InvalidColumnsError as invalid_columns_error:
            invalid_columns_str = ', '.join(invalid_columns_error.columns)
            message = 'Unexpected data input(s): [' + invalid_columns_str + ']'
            return make_response(
                jsonify({'message': message}), STATUS_INVALID_INPUT
            )
        except DBError as error:
            return make_response(
                jsonify({'message': error.message}), STATUS_INTERNAL_ERROR
            )
        return make_response(jsonify({'message': message}), STATUS_OK)

    def delete(self, user_id):
        '''
        Delete a user
        '''
        try:
            DBService.delete_data(table=self.db_table, data_id=user_id)
        except EntryNotFoundError:
            return make_response(
                jsonify({'message': 'The user with id {} was not found'.format(user_id)}),
                STATUS_NOT_FOUND
            )
        except DBError as error:
            return make_response(
                jsonify({'message': error.message}), STATUS_INTERNAL_ERROR
            )
