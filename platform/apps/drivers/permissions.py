from rest_framework.permissions import BasePermission


class IsDriverAuthenticated(BasePermission):
    """
    Permiso personalizado que verifica si el usuario está autenticado como driver
    usando JWT tokens con información del driver.
    """

    def has_permission(self, request, view):
        # Verificar si el middleware agregó información del driver al request
        return hasattr(request, 'driver_id') and request.driver_id is not None


class IsDriverOwner(BasePermission):
    """
    Permiso que verifica si el driver autenticado es el propietario del recurso.
    Útil para vistas que requieren que el driver solo pueda acceder a sus propios datos.
    """

    def has_object_permission(self, request, view, obj):
        # Verificar que el driver esté autenticado
        if not hasattr(request, 'driver_id') or request.driver_id is None:
            return False

        # Verificar que el objeto tenga un atributo driver_id o steam_id
        if hasattr(obj, 'driver_id'):
            return obj.driver_id == request.driver_id
        elif hasattr(obj, 'steam_id'):
            return obj.steam_id == request.driver_steam_id

        return False