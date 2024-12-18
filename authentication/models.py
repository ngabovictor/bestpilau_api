from django.conf import settings
from django.db import models

import uuid
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from auditlog.registry import auditlog

from utils.models import BaseModel
from utils.fields import JSONSchemaField, LOCATION_DEFINITION_SCHEMA


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_rider = models.BooleanField(default=False)
    rider_id = models.CharField(max_length=255, null=True, blank=True, unique=True)

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

auditlog.register(User, exclude_fields=['password', 'username'])


class OTPManager(models.Manager):
    def get_user_valid_otp(self, user):
        """
        Retrieves the last valid OTP for a user.

        Args:
            user: The user object to fetch the OTP for.

        Returns:
            The latest valid OTP object if it exists, otherwise None.
        """
        try:
            return self.filter(
                user=user, expires_at__gt=timezone.now(), is_used=False
            ).latest("created_at")
        except OTP.DoesNotExist:
            return None

    def check_valid_otp(self, user, raw_code):
        """
        Checks if a given OTP is valid for a user.

        Args:
            user: The user object to check the OTP against.
            raw_code: The raw (unhashed) OTP code.

        Returns:
            True if the OTP is valid and not yet used, False otherwise.
        """
        otp = self.get_user_valid_otp(user)  # Get the latest valid OTP
        if otp and otp.check_code(raw_code):
            otp.mark_as_used()  # Mark the OTP as used
            return True
        return False


class OTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    objects = OTPManager()

    def set_code(self, raw_code):
        self.code = make_password(raw_code)

    def check_code(self, raw_code):
        # Check expiration first
        if self.expires_at < timezone.now() or self.is_used:
            return False  # Expired OTP is always invalid

        def setter(raw_code):
            self.set_code(raw_code)
            # Update updated_at field as well (optional)
            self.save(update_fields=["code"])

        return check_password(raw_code, self.code, setter)

    def mark_as_used(self):
        self.is_used = True
        self.save(update_fields=["is_used"])

    def save(self, *args, **kwargs):
        # If the code is not already hashed, hash it before saving
        if not self.code.startswith("pbkdf2_sha256$"):
            self.set_code(self.code)
        super().save(*args, **kwargs)


class SavedAddress(BaseModel):
    name = models.CharField(max_length=255, null=True, blank=True)
    address = JSONSchemaField(schema=LOCATION_DEFINITION_SCHEMA)

auditlog.register(SavedAddress)