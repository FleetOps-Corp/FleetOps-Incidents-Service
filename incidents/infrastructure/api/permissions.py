"""Custom permission classes for role-based access control."""

from rest_framework.permissions import BasePermission


class HasIncidentAccess(BasePermission):
    """
    Restricts access to endpoints according to the user's role.
    """

    message = "You do not have permission to perform this action."

    ALLOWED_ROLES = {
        "GET": {
            "EMPLEADO_VEHICULOS",
            "EMPLEADO_MANTENIMIENTO",
            "EMPLEADO_ASIGNACIONES",
            "EMPLEADO_REPORTES",
            "EMPLEADO_INCIDENTES",
            "ADMINISTRADOR",
        },
        "POST": {
            "EMPLEADO_VEHICULOS",
            "EMPLEADO_MANTENIMIENTO",
            "EMPLEADO_ASIGNACIONES",
            "EMPLEADO_REPORTES",
            "EMPLEADO_INCIDENTES",
            "ADMINISTRADOR",
        },
    }

    def has_permission(self, request, view):
        user = request.user

        if not getattr(user, "is_authenticated", False):
            return False

        role = getattr(user, "role", None)

        if role is None:
            return False

        return role in self.ALLOWED_ROLES.get(request.method, set())
