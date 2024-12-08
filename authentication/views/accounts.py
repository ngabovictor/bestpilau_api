import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from authentication.serializers.user_serializer import UserSerializer

logger = logging.getLogger(__name__)


class AccountViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @action(methods=['PATCH'], detail=False, name='update-profile', url_name='update-profile',
            url_path='update-profile')
    def update_account_profile(self, request, *args, **kwargs):
        logger.info('Updating profile')
        context = {
            "request": request
        }

        serializer = UserSerializer(instance=request.user, data=request.data, partial=True, context=context)

        logger.info('Validating user input: {}'.format(request.data))
        serializer.is_valid(raise_exception=True)

        logger.info('Saving user input')
        serializer.save()
        logger.info('Saved user input: {}'.format(serializer.data))

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, name='get-profile', url_name='get-profile',
            url_path='get-profile')
    def get_account_profile(self, request, *args, **kwargs):
        logger.info('Getting profile')
        context = {
            "request": request
        }

        serializer = UserSerializer(instance=request.user, context=context)

        return Response(serializer.data, status=status.HTTP_200_OK)

