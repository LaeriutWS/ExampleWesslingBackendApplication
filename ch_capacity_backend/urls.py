"""
URL configuration for ch_capacity_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from capacity.views import GoogleLoginApi, GroupsView, UsersView, BackendPermissionsView, FrontendPermissionsView, \
    MyPermissionsView

# JWT authentication
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/google-login/', GoogleLoginApi.as_view()),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/groups/', GroupsView.as_view()),
    path('api/users/', UsersView.as_view()),
    path('api/backend_permissions/', BackendPermissionsView.as_view()),
    path('api/backend_permissions/delete/<int:pk>/', BackendPermissionsView.as_view()),
    path('api/frontend_permissions/', FrontendPermissionsView.as_view()),
    path('api/frontend_permissions/delete/<int:pk>/', FrontendPermissionsView.as_view()),
    path('api/my_permissions/', MyPermissionsView.as_view()),
]
