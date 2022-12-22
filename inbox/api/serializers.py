from rest_framework.serializers import ModelSerializer
from notifications.models import Notification


class NotificationSerializer(ModelSerializer):

    # Notification具体的设计在AbstractNotification
    class Meta:
        model = Notification
        fields = (
            'id',
            'actor_content_type',
            'actor_object_id',
            'verb',
            'action_object_content_type',
            'action_object_object_id',
            'target_content_type',
            'target_object_id',
            'timestamp',
            'unread',
        )