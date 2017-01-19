'''
Requests associated to Poles
'''
from flask import jsonify, request
from flask.views import MethodView

from common.db_service import DBService
from common.exceptions import DBError, EntryNotFoundError, InvalidColumnsError
from common.status_codes import (STATUS_CREATED, STATUS_INTERNAL_ERROR,
                                 STATUS_NOT_FOUND, STATUS_OK, STATUS_INVALID_INPUT, STATUS_NO_INPUT)


class PolesAPI(MethodView):
    '''
    Exposes the 'Poles' api endpoint
    '''
    db_table = 'pole'

    def get(self, pole_id=None):
        '''
        Get the data for the Pole with the specified pole_id.
        Get the data for all Poles.
        '''
        try:
            db_data = DBService().select_data(self.db_table, data_id=pole_id)
        except EntryNotFoundError:
            return {
                'message': 'The pole with id {} was not found'.format('pole_id')
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
        Create and add a new Pole
        '''
        data = request.form.to_dict()
        if len(data) == 0:
            return{'message': 'No data input provided'}, STATUS_NO_INPUT
        try:
            pole_id = DBService().insert_data(self.db_table, **data)
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
            'message': 'The pole has been added successfully',
            'id': pole_id
        }, STATUS_CREATED

    def put(self, pole_id):
        '''
        Update the data for a Pole
        '''
        data = request.form.to_dict()
        if len(data) == 0:
            return {'message': 'No data input provided'}, STATUS_NO_INPUT
        try:
            DBService().update_data(table=self.db_table, data_id=pole_id, new_data=data)
        except EntryNotFoundError:
            return {
                'message': 'The pole with id {} was not found'.format(pole_id)
            }, STATUS_NOT_FOUND
        except InvalidColumnsError as invalid_columns_error:
            invalid_columns_str = ', '.join(invalid_columns_error.columns)
            message = 'Unexpected data input(s): [' + invalid_columns_str + ']'
            return {'message': message}, STATUS_INVALID_INPUT
        except DBError as error:
            return {'message': error.message}, STATUS_INTERNAL_ERROR

    def delete(self, pole_id):
        '''
        Delete a Pole
        '''
        try:
            DBService().delete_data(table=self.db_table, data_id=pole_id)
        except EntryNotFoundError:
            return {
                'message': 'The pole with id {} was not found'.format(pole_id)
            }, STATUS_NOT_FOUND
        except DBError as error:
            return {'message': error.message}, STATUS_INTERNAL_ERROR
