from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status

from .exceptions import LogicError


def get_object_or_404_with_message(klass, message, *args, **kwargs):
    try:
        return get_object_or_404(klass, *args, **kwargs)
    except Http404:
        raise LogicError(message, status.HTTP_404_NOT_FOUND)
