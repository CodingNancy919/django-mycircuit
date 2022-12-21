from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from inbox.api.serializers import NotificationSerializer


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
    def unread_count(self, request, *args, **kwargs):
        unread_count = self.get_queryset().filter(unread=True).count()
        # Notification.objects.filter(
        #     recipient=self.request.user,
        #     unread=True,
        # ).count()
        return Response({'unread_count': unread_count}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='mark-all-as-read')
    def mark_all_as_read(self, request, *args, **kwargs):
        update_count = self.get_queryset().filter(unread=True).update(unread=False)
        return Response({'update_count': update_count}, status=status.HTTP_200_OK)
