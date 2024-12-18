import logging
from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from authentication.models import OTP
from authentication.models import User
from authentication.serializers.jwt_serializer import JwtTokenObtainPairSerializer
from authentication.serializers.user_serializer import UserSerializer
from utils.functions import generate_digits_code
from notifications.sms import send_sms_task
from rest_framework.authtoken.models import Token

logger = logging.getLogger(__name__)


class AuthViewSet(ViewSet):
    permission_classes = [AllowAny]

    @action(methods=['POST'], detail=False, name='request-otp', url_name='request-otp', url_path='request-otp')
    def request_otp_code(self, request, *args, **kwargs):
        username = request.data.get("username")
        if not username:
            return Response(data={"message": "Username was not provided"}, status=status.HTTP_400_BAD_REQUEST)

        logger.info("Finding user with provided username: {}".format(username))
        user, _ = User.objects.get_or_create(username=username, defaults={"is_active": True})

        # Generate OTP

        logger.info("Generate OTP")

        generated_code = generate_digits_code(length=4)

        otp = OTP(user=user)
        otp.set_code(generated_code)
        otp.expires_at = timezone.now() + timedelta(minutes=10)
        otp.save()

        logger.info("Sending to username OTP: {}".format(generated_code))
        print("Sending to username OTP: {}".format(generated_code))

        send_sms_task(message=f"Your Best Pilau OTP is {generated_code}. It will expire in 10 minutes.", phone_numbers=[username])
        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, name='verify-otp-jwt', url_name='verify-otp-jwt', url_path='verify-otp-jwt')
    def verify_otp_jwt(self, request, *args, **kwargs):
        username = request.data.get("username")
        code = request.data.get("code")

        if not username or not code:
            return Response(data={"message": "Username and/or OTP was not provided"},
                            status=status.HTTP_400_BAD_REQUEST)

        token_serializer = JwtTokenObtainPairSerializer(data={
            'username': str(username),
            'code': code
        })
        token_serializer.is_valid(raise_exception=True)
        request.user = token_serializer

        return Response({
            'tokens': {
                "access_token": str(token_serializer.token.access_token),
                "refresh_token": str(token_serializer.token),
                "token_type": "Bearer",
            },  # Use the custom serializer
            'user': UserSerializer(token_serializer.user, context={'request': request}).data
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, name='verify-otp', url_name='verify-otp', url_path='verify-otp')
    def verify_otp_token(self, request, *args, **kwargs):
        username = request.data.get("username")
        code = request.data.get("code")

        if not username or not code:
            return Response(data={"message": "Username and/or OTP was not provided"},
                            status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(username=username, is_active=True).first()

        if not user:
            return Response(data={"message": "User with provided username is not found"},
                            status=status.HTTP_400_BAD_REQUEST)

        token_serializer = JwtTokenObtainPairSerializer(data={
            'username': str(username),
            'code': code
        })

        token, _ = Token.objects.get_or_create(user=user)

        request.user = user

        return Response({
            'tokens': {
                "access_token": str(token.key),
                "refresh_token": None,
                "token_type": "Token",
            },  # Use the custom serializer
            'user': UserSerializer(user, context={'request': request}).data
        }, status=status.HTTP_200_OK)
        
    @action(methods=['POST'], detail=False, name='login', url_name='login', url_path='login')
    def password_login(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(data={"message": "Username and/or password was not provided"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(username=username, is_active=True).first()

        
        if not user or not user.check_password(password):
            return Response(data={"message": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)
        
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'tokens': {
                "access_token": str(token.key),
                "refresh_token": None,
                "token_type": "Token",
            },  # Use the custom serializer
            'user': UserSerializer(user, context={'request': request}).data
        }, status=status.HTTP_200_OK)