from rest_framework.permissions import BasePermission
from rest_framework import permissions

class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'DOCTOR')

class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'PATIENT')


class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.patient == request.user
    
class IsPatientOrReadOnly(permissions.BasePermission):
    """
    - Read permissions allowed to any user (patients or doctors).
    - Write permissions only allowed to patients (and only for their own reviews).
    """

    def has_permission(self, request, view):
        # Allow safe methods (GET, HEAD, OPTIONS) for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only patients can create/update/delete
        return request.user.role == 'PATIENT'  # Adjust if your User model has a 'role' field

    def has_object_permission(self, request, view, obj):
        # Read permissions allowed for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for the review author
        return obj.patient == request.user