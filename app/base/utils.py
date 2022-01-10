from rest_framework.exceptions import ValidationError


def check(to_check, fields):
    for field in to_check:
        if field not in fields:
            raise ValidationError({'error_message': f'possible fields: {fields}'})
