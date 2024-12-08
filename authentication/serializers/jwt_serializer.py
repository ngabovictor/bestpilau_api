import logging

from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from authentication.models import OTP, User
from authentication.serializers.user_serializer import UserSerializer
from rest_framework import serializers

logger = logging.getLogger(__name__)


class JwtTokenObtainPairSerializer(TokenObtainPairSerializer):
    username = serializers.CharField()  # Add a field for the username
    code = serializers.CharField()  # Add a field for the OTP code
    default_error_messages = {
        'no_active_account': 'No active account found with the given credentials'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.token = None
        self.fields.pop('password', None)

    def validate(self, attrs):
        username = attrs.get('username')
        code = attrs.get('code')

        try:
            user = User.objects.get(username=username)
            self.user = user
        except User.DoesNotExist:
            raise TokenError(self.error_messages['no_active_account'])

        if not user.is_active:
            raise TokenError(self.error_messages['no_active_account'])

        if not OTP.objects.check_valid_otp(user=user, raw_code=code):
            raise InvalidToken("Invalid OTP")

        refresh = self.get_token(user)
        self.token = refresh
        data = {"refresh": str(refresh), "access": str(refresh.access_token), "code": code, "username": username, "user": user}
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['account'] = UserSerializer(instance=user).data
        token['groups'] = [group.name for group in user.groups.all()]
        perms = []

        # Extract user permissions
        for perm in user.user_permissions.all():
            perms.append(perm.codename)

        # Extract permissions from groups

        for group in user.groups.all():
            for perm in group.permissions.all():
                perms.append(perm.codename)

        # Add permissions to token
        token['perms'] = perms

        return token
