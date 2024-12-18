from django.db import models
from auditlog.registry import auditlog
from utils.fields import JSONSchemaField
from utils.models import BaseModel

LOCATION_DEFINITION_SCHEMA = {
    "type": "object",
    "properties": {
        "address": {"type": "string"},
        "latitude": {"type": "number"},
        "longitude": {"type": "number"}
    },
    "required": ["address", "latitude", "longitude"],
}

WORKING_HOURS_DEFINITION_SCHEMA = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "day": {"type": "string"},
                "open_hours": {"type": "string"},    
            },
            "required": ["day", "open_hours"]
        },
        "required": []
    }

class Outlet(BaseModel):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='outlets_images', null=True,)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    is_open = models.BooleanField(default=True)
    working_hours = JSONSchemaField(schema=WORKING_HOURS_DEFINITION_SCHEMA)
    address = JSONSchemaField(schema=LOCATION_DEFINITION_SCHEMA)
    workers = models.ManyToManyField('authentication.User', related_name='outlets', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


auditlog.register(Outlet)