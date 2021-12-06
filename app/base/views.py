from django.http import JsonResponse
from rest_framework import status


def health(request):
    return JsonResponse({'message': 'OK'}, status=status.HTTP_200_OK)
