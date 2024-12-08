import os
from authentication.models import User
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny


class AdminViewSet(ViewSet):
    permission_classes = [AllowAny]

    @action(methods=['POST'], detail=False, name='init-superuser', url_name='init-superuser', url_path='init-superuser')
    def create_superuser_account(self, request, *args, **kwargs):
        username = os.getenv('ADMIN_USERNAME')
        password = os.getenv('ADMIN_PASSWORD')
        user = User.objects.filter(username=username).first()
        if user:
            return Response(data={"message": "Unauthorized action"}, status=403)
        user = User(
            username=username,
            email=username,
            is_staff=True,
            is_superuser=True
        )

        user.set_password(password)

        user.save()

        return Response(data={"message": "Superuser account successfully initialized"}, status=status.HTTP_201_CREATED)
