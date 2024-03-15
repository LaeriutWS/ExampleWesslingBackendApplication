import os

from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response

from capacity.models import BackendPermissions, FrontendPermissions
from capacity.permissions import HasGroupAndIpPermission
from capacity.serializers import GroupSerializer, UserSerializer, BackendPermissionsInputSerializer, \
    BackendPermissionsSerializer, FrontendPermissionsInputSerializer, FrontendPermissionsSerializer


class UsersView(APIView):
    """
    url: /api/users
    View to create, update and retrieve users
    """

    permission_classes = [HasGroupAndIpPermission]

    @staticmethod
    def get(request):
        users = User.objects.all()
        users = users.prefetch_related('groups')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    @staticmethod
    def post(request):
        data = request.data
        user = User.objects.create_user(username=data['email'], email=data['email'], first_name=data['first_name'],
            last_name=data['last_name'], is_active=data['is_active'], )
        user.save()

        for group in data['groups']:
            user.groups.add(group)

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def patch(request):

        user_id = request.data['id']
        user = User.objects.filter(id=user_id).first()

        # first delete all groups
        user.groups.clear()

        # remove group attribute from request data
        groups = request.data.pop('groups')
        for group in groups:
            user.groups.add(group)

        # update user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupsView(APIView):
    """
    url: /api/groups
    View to create, update and retrieve groups
    """

    permission_classes = [HasGroupAndIpPermission]

    @staticmethod
    def get(request):
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)

    @staticmethod
    def post(request):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def patch(request):
        group_id = request.data['id']
        group = Group.objects.get(id=group_id)
        group.name = request.data['name']
        group.save()
        serializer = GroupSerializer(group)
        return Response(serializer.data, status=status.HTTP_200_OK)

class BackendPermissionsView(generics.ListAPIView):
    """
    url: /api/backend_permissions
    View to create, update and retrieve users
    """

    permission_classes = [HasGroupAndIpPermission]

    # get class name
    queryset = BackendPermissions.objects.all()
    serializer_class = BackendPermissionsInputSerializer

    def get(self, request):
        permissions = BackendPermissions.objects.all()
        permissions = permissions.prefetch_related('groups')
        serializer = BackendPermissionsSerializer(permissions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BackendPermissionsInputSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            serializer = BackendPermissionsSerializer(serializer.instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        db_id = request.data['id']
        permission = BackendPermissions.objects.filter(id=db_id).first()
        serializer = BackendPermissionsInputSerializer(permission, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            serializer = BackendPermissionsSerializer(permission)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        permission_data = BackendPermissions.objects.get_queryset().filter(id=kwargs['pk'])
        permission_data.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FrontendPermissionsView(generics.ListAPIView):
    """
    url: /api/users
    View to create, update and retrieve users
    """

    permission_classes = [HasGroupAndIpPermission]

    # get class name
    queryset = FrontendPermissions.objects.all()
    serializer_class = FrontendPermissionsInputSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'url', 'groups__id']

    def get(self, request):
        permissions = FrontendPermissions.objects.all()
        permissions = self.filter_queryset(permissions)
        permissions = permissions.prefetch_related('groups')
        serializer = FrontendPermissionsSerializer(permissions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FrontendPermissionsInputSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            serializer = FrontendPermissionsSerializer(serializer.instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        db_id = request.data['id']
        permission = FrontendPermissions.objects.filter(id=db_id).first()
        serializer = FrontendPermissionsInputSerializer(permission, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            serializer = FrontendPermissionsSerializer(permission)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        permission_data = FrontendPermissions.objects.get_queryset().filter(id=kwargs['pk'])
        permission_data.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyPermissionsView(APIView):
    """
    url: /api/my_permissions
    View to retrieve permissions for the current user
    """

    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request):
        user = request.user
        groups = user.groups.all()
        backend_permissions = BackendPermissions.objects.filter(groups__in=groups).distinct()
        frontend_permissions = FrontendPermissions.objects.filter(groups__in=groups).distinct()

        backend_serializer = BackendPermissionsSerializer(backend_permissions, many=True)
        frontend_serializer = FrontendPermissionsSerializer(frontend_permissions, many=True)

        return JsonResponse(
            {"backend_permissions": backend_serializer.data, "frontend_permissions": frontend_serializer.data},
            headers={'Access-Allow-Origin': '*'}, status=200)


class GoogleLoginApi(APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def post(request):
        """
        POST API for google login
        """

        try:
            token = request.data.get('google_token')
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(),
                                                  os.environ['GOOGLE_OAUTH_CLIENT_ID_FRONTEND'])
            email = idinfo['email']
            user = User.objects.filter(email=email).first()
            if user is None:
                return JsonResponse({"errors": {"detail": "User does not exist"}}, status=400)

            else:
                refresh = RefreshToken.for_user(user)
                user.last_login = timezone.now()
                user.save()

                return JsonResponse(
                    {"username": user.username, "refresh": str(refresh), "access": str(refresh.access_token), },
                    headers={'Access-Allow-Origin': '*'}, status=200)

        except ValueError as e:
            print(e)
            return JsonResponse({"errors": {"detail": "Invalid token"}}, status=400)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def post(request):

        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(token=refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(exception=e, status=status.HTTP_400_BAD_REQUEST)
