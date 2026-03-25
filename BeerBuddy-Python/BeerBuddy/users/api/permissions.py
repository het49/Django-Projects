from rest_framework.permissions import BasePermission

class IsAllowed(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.values_list('name',flat =True).first()==request.META.get("HTTP_USER_TYPE")