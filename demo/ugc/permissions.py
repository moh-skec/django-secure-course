from rest_framework import permissions


class OnlyCreatorPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        del view 
        return request.method == 'POST' or request.method == 'GET'

    def has_object_permission(self, request, view, obj):
        del view  
        return request.user == obj.created_by
