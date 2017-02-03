'''
Requests associated to Poles
'''
from flask import jsonify, make_response, request
from flask.views import MethodView

from app import DB_SERVICE as DBService
# from common.db_service import DBService
from common.exceptions import DBError, EntryNotFoundError, InvalidColumnsError
from common.status_codes import (STATUS_CREATED, STATUS_INTERNAL_ERROR,
                                 STATUS_INVALID_INPUT, STATUS_NO_INPUT,
                                 STATUS_NOT_FOUND, STATUS_OK)


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
            filter_params = request.args.to_dict()
            # if pole_number was passed in as a request argument,
            # we perform a search instead
            if 'pole_number' in filter_params:
                db_data = DBService.search_data(
                    self.db_table, 'pole_number', filter_params['pole_number']
                )
            else:
                db_data = DBService.select_data(
                    self.db_table, data_id=pole_id, **filter_params)
        except EntryNotFoundError:
            return make_response(
                jsonify(
                    {'message': 'The pole with id {} was not found'.format(pole_id)}),
                STATUS_NOT_FOUND
            )
        except DBError as error:
            return make_response(
                jsonify({'message': error.message}), STATUS_INVALID_INPUT
            )
        return make_response(jsonify(db_data), STATUS_OK)

    def post(self):
        '''
        Create and add a new Pole
        '''
        data = request.args
        long_ = float(data['long'])
        lat_ = float(data['lat'])
        pole_number_ = str(data['pole_number'])
        new_pole_data = {
            'pole_number': pole_number_, 'long':long_, 'lat': lat_
        }
        if len(data) == 0:
            return make_response(
                jsonify({'message': 'No data input provided'}), STATUS_NO_INPUT
            )
        try:
            pole_id = DBService.insert_data(self.db_table, **new_pole_data)
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
            jsonify(
                {'message': 'The pole has been added successfully', 'id': pole_id}),
            STATUS_CREATED
        )

    def put(self, pole_id):
        '''
        Update the data for a Pole
        '''
        data = request.form.to_dict()
        if len(data) == 0:
            return make_response(
                jsonify({'message': 'No data input provided'}), STATUS_NO_INPUT
            )
        try:
            DBService.update_data(table=self.db_table,
                                  data_id=pole_id, new_data=data)
        except EntryNotFoundError:
            return make_response(
                jsonify(
                    {'message': 'The pole with id {} was not found'.format(pole_id)}),
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
        return make_response(
            jsonify(
                {'message': 'The pole with id {} has been updated successfully'.format(
                    pole_id)}
            ),
            STATUS_OK
        )

    def delete(self, pole_id):
        '''
        Delete a Pole
        '''
        try:
            DBService.delete_data(table=self.db_table, data_id=pole_id)
        except EntryNotFoundError:
            return make_response(
                jsonify(
                    {'message': 'The pole with id {} was not found'.format(pole_id)}),
                STATUS_NOT_FOUND
            )
        except DBError as error:
            return make_response(
                jsonify({'message': error.message}), STATUS_INTERNAL_ERROR
            )
        return make_response(
            jsonify(
                {'message': 'The pole with id {} has been deleted successfully'.format(
                    pole_id)}
            ),
            STATUS_OK
        )
