from django.contrib.auth.models import Group
from rest_framework import permissions, exceptions

from capacity.models import BackendPermissions


def is_in_group(request, group_name):
    """
    Takes a user and a group name, and returns `True` if the user is in that group.
    """
    try:
        return Group.objects.get(name=group_name).user_set.filter(id=request.user.id).exists()
    except Group.DoesNotExist:
        return None


def is_allowed_ip(request, ip):
    return request.META['REMOTE_ADDR'] in ip.split(',')


class HasGroupAndIpPermission(permissions.BasePermission):

    def has_permission(self, request, view):

        try:
            url = request.get_full_path().split('?')[0]

            if "/delete/" in url:
                url = url.split('delete/')[0]

            required_groups_mapping = getattr(view, "required_groups", {})
            ip_addresses = getattr(view, "ip_addresses", {})

            permissions = ""

            # get permissions from db
            if ip_addresses == {} or required_groups_mapping == {}:
                class_name = view.__class__.__name__
                permissions = BackendPermissions.objects.filter(url=url, groups__in=request.user.groups.all())

            # check groups
            if required_groups_mapping == {}:
                required_groups_mapping = {'GET': [], 'POST': [], 'PUT': [], 'PATCH': [], 'DELETE': [], 'IP': []}

                if permissions == None:
                    return False

                for permission in permissions:

                    if permission.ip_addresses is None:
                        permission.ip_addresses = []

                    for group in permission.groups.all():
                        if permission.get:
                            required_groups_mapping['GET'].append(group.name)
                        if permission.post:
                            required_groups_mapping['POST'].append(group.name)
                        if permission.patch:
                            required_groups_mapping['PATCH'].append(group.name)
                        if permission.delete:
                            required_groups_mapping['DELETE'].append(group.name)
                        if len(permission.ip_addresses) > 0:
                            for ip in permission.ip_addresses:
                                if ip not in required_groups_mapping['IP']:
                                    required_groups_mapping['IP'].append(ip)

            # Determine the required groups for this particular request method.
            required_groups = required_groups_mapping.get(request.method, [])
            allowed_ips = required_groups_mapping.get('IP', "")

            ip_error = False

            # Return True if the user has one required group or is staff.
            ip_allowed = True
            for group_name in required_groups:

                if is_in_group(request, group_name):

                    # check ip too
                    if len(allowed_ips) > 0:
                        if request.META.get('REMOTE_ADDR') in allowed_ips:
                            return True
                        else:
                            ip_error = True
                    else:
                        return True

            if ip_error:
                raise exceptions.PermissionDenied(detail="Invalid IP: " + request.META.get('REMOTE_ADDR'))

            raise exceptions.PermissionDenied(detail="Invalid User")
        except Exception as e:
            # raise exceptions.APIException(code=403, detail=str(e))
            raise exceptions.PermissionDenied(detail=str(e))
