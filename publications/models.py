from django.db import models

from auditlog.registry import auditlog
from utils.models import BaseModel


class Pub(BaseModel):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='publications_images',)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


auditlog.register(Pub)
