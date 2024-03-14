from rest_framework import serializers

from django.contrib.auth.models import Group, User

from capacity.models import BackendPermissions, FrontendPermissions


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'groups', 'email', 'first_name', 'last_name', 'is_active', 'last_login')


class BackendPermissionsSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)

    class Meta:
        model = BackendPermissions
        fields = '__all__'


class BackendPermissionsInputSerializer(serializers.ModelSerializer):

    class Meta:
        model = BackendPermissions
        fields = '__all__'


class FrontendPermissionsSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)

    class Meta:
        model = FrontendPermissions
        fields = '__all__'


class FrontendPermissionsInputSerializer(serializers.ModelSerializer):

    class Meta:
        model = FrontendPermissions
        fields = '__all__'