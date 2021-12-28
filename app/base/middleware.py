from django.http import JsonResponse
from rest_framework import status


class ErrorHandler:
    def __init__(self, get_response):
        self._get_response = get_response

    def __call__(self, request):
        return self._get_response(request)

    def process_exception(self, request, exception):
        return JsonResponse({'error_message': f'{exception}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
