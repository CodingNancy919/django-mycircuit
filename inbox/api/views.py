from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from utils.decorators import required_params
from notifications.models import Notification
from django.utils.decorators import method_decorator
from ratelimit.decorators import ratelimit

from inbox.api.serializers import (
    NotificationSerializer,
    NotificationSerializerForUpdate,
)


class NotificationViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin
):

    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ('unread',)

    def get_queryset(self):
        # return Notification.objects.filter(recipient=self.request.user)
        return self.request.user.notifications.all()

    @action(methods=['GET'], detail=False, url_path='unread-count')
    @method_decorator(ratelimit(key='user', rate='3/s', method='GET', block=True))
    def unread_count(self, request, *args, **kwargs):
        unread_count = self.get_queryset().filter(unread=True).count()
        # Notification.objects.filter(
        #     recipient=self.request.user,
        #     unread=True,
        # ).count()
        return Response({'unread_count': unread_count}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='mark-all-as-read')
    @method_decorator(ratelimit(key='user', rate='3/s', method='POST', block=True))
    def mark_all_as_read(self, request, *args, **kwargs):
        update_count = self.get_queryset().filter(unread=True).update(unread=False)
        return Response({'update_count': update_count}, status=status.HTTP_200_OK)

    @required_params(method='PUT', params=['unread'])
    @method_decorator(ratelimit(key='user', rate='3/s', method='POST', block=True))
    def update(self, request, *args, **kwargs):
        """
       用户可以标记一个 notification 为已读或者未读。标记已读和未读都是对 notification
       的一次更新操作，所以直接重载 update 的方法来实现。另外一种实现方法是用一个专属的 action：
           @action(methods=['POST'], detail=True, url_path='mark-as-read')
           def mark_as_read(self, request, *args, **kwargs):
               ...
           @action(methods=['POST'], detail=True, url_path='mark-as-unread')
           def mark_as_unread(self, request, *args, **kwargs):
               ...
       两种方法都可以，我更偏好重载 update，因为更通用更 rest 一些, 而且 mark as unread 和
       mark as read 可以公用一套逻辑。
       """
        notification = self.get_object()
        serializer = NotificationSerializerForUpdate(
            instance=notification,
            data=request.data,
        )

        if not serializer.is_valid():
            return Response({
                'Success': False,
                'message': 'Please check your input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        notification = serializer.save()
        return Response(
            NotificationSerializer(notification).data,
            status=status.HTTP_200_OK)


