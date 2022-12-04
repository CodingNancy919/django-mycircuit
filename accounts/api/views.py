from rest_framework import views, permissions
from rest_framework import viewsets
from django.contrib.auth.models import User,Group
from accounts.api.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]