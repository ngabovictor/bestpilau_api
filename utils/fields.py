from django.db import models
from django.core.exceptions import ValidationError
import jsonschema

SERVICE_DEFINITION_SCHEMA = {
    "type": "object",
    "properties": {
        "defaultOrigin": {
            "oneOf": [
                {"type": "null"},  # Allow null value
                {
                    "type": "object",
                    "properties": {
                        "address": {"type": "string"},
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"},
                        "editable": {"type": "boolean"}
                    },
                    "required": ["address", "latitude", "longitude", "editable"]
                }
            ]
        },
        "defaultDestination": {  # Same structure as defaultOrigin
            "oneOf": [
                {"type": "null"},
                {
                    "type": "object",
                    "properties": {
                        "address": {"type": "string"},
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"},
                        "editable": {"type": "boolean"}
                    },
                    "required": ["address", "latitude", "longitude", "editable"]
                }
            ]
        },
        "options": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "optionLabel": {"type": "string"},
                    "requests_count_controller": {"type": "boolean"},
                    "defaultOption": {
                        "type": "object",
                        "properties": {
                            "label": {},
                            "value": {}
                        }
                    },
                    "optionPlaceholder": {"type": "string"},
                    "choices": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "label": {},
                                "value": {}
                            }
                        }
                    }
                },
                "required": ["optionLabel", "optionPlaceholder", "choices", "requests_count_controller"]
            }
        }
    },
    "required": []
}

LOCATION_DEFINITION_SCHEMA = {
    "type": "object",
    "properties": {
        "address": {"type": "string"},
        "name": {"type": "string"},
        "latitude": {"type": "number"},
        "longitude": {"type": "number"}
    },
    "required": ["address", "latitude", "longitude"],
}


class JSONSchemaField(models.JSONField):
    """A JSONField that validates against a given JSON schema."""

    def __init__(self, *args, schema=None, **kwargs):
        self.schema = schema
        super().__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        """Perform validation against the schema."""
        super().validate(value, model_instance)
        if value is not None:  # Allow null values
            try:
                jsonschema.validate(value, self.schema)
            except jsonschema.exceptions.ValidationError as e:
                raise ValidationError(str(e))
