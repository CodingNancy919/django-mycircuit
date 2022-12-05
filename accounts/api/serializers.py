from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework import exceptions

class UserSerializer(serializers.ModelSerializer):
    """
    把User实例中指定的fields字段取出来包装成json返回
    经常用在和DB交互后得到instance，需要传给前端转换后的数据
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    # def validate(self, data):
    #     if not User.objects.filter(username=data['username'].lower()).exists():
    #         raise exceptions.ValidationError({
    #             'message': 'This user does not exists'
    #         })
    #     return data

class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=20, min_length=6)
    password = serializers.CharField(max_length=20, min_length=6)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    # will be called when is_valid() is called
    def validate(self, data):
        if User.objects.filter(username=data['username'].lower()).exists():
            raise exceptions.ValidationError({
                'username': 'This username has been occupied'
            })
        if User.objects.filter(email=data['email'].lower()).exists():
            raise exceptions.ValidationError({
                'email': 'This email address has been occupied'
            })
        return data

    # will be called when save() is called
    def create(self, validated_data):
        username = validated_data['username'].lower()
        email = validated_data['email'].lower()
        password = validated_data['password'].lower()
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password)
        return user
