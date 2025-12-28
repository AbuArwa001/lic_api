from rest_framework.permissions import BasePermission

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            print("GET")
            return True
        print("POST")
        return request.user and request.user.is_staff

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        print("user", request.user)
        print("is_staff", request.user.is_staff)
        return request.user and request.user.is_staff
    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_staff

class AllowAll(BasePermission):
    def has_permission(self, request, view):
        return True

class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated