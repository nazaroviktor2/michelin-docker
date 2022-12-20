from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsEditorOrStaffAndAuth(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated and (request.user.is_editor or request.user.is_staff))

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated and request.user.is_editor and
            obj.user == request.user or request.user.is_staff)


class IsOwnerOrStaff(BasePermission):
    # def has_permission(self, request, view):
    #     return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated and obj.user == request.user or request.user.is_staff)
