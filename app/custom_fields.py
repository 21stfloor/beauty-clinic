from django.db import models
from django.core.exceptions import ValidationError

class PhoneNumberField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 15  # E.164 format (e.g., +123456789012)
        super(PhoneNumberField, self).__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def to_python(self, value):
        if value is None or value == "":
            return value
        # Remove non-digit characters from the input
        return ''.join(filter(str.isdigit, value))

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        if not value.startswith('+'):
            raise ValidationError("Phone number must start with '+' and include country code.")
        if not value[1:].isdigit():
            raise ValidationError("Phone number must contain only digits after the '+'.")

    def get_prep_value(self, value):
        if value:
            return '+' + value

    def formfield(self, **kwargs):
        return super().formfield(**{
            'max_length': 15,
            **kwargs,
        })
