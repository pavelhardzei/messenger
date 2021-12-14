from rest_framework import status
from rest_framework.exceptions import APIException


class LogicError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred.'

    def __init__(self, detail=None, status_code=None):
        if status_code:
            self.status_code = status_code
        if detail:
            self.detail = {'error_message': detail}
        else:
            self.detail = {'error_message': self.default_detail}
