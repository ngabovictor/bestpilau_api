from django.db import models, transaction
import uuid
from django.conf import settings


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    version = models.IntegerField(default=0)
    state = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Lock on the ID to prevent race condition
        with transaction.atomic():
            try:
                original = type(self).objects.select_for_update().get(pk=self.pk)
                self.version = original.version + 1
            except:
                pass
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
