'''
All status codes used in the application.
The status codes defined as X5X are custom to the application
and not part of the standard HTTP status codes
'''

# success statius codes
STATUS_OK = 200
STATUS_CREATED = 201

# client error status codes
STATUS_INVALID_INPUT = 451
STATUS_NOT_FOUND = 404
STATUS_NO_INPUT = 450

# server-side errors status codes
STATUS_INTERNAL_ERROR = 500
