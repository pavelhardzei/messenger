from rest_framework import status
from rest_framework.exceptions import APIException


class LogicError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred.'

    def __init__(self, detail=None, status_code=None):
        self.status_code = status_code or self.status_code
        self.detail = {'error_message': detail or self.default_detail}
