"""Domain exception hierarchy."""


class DomainException(Exception):
    """Base exception for all domain-level errors."""

    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code or self.__class__.__name__
        super().__init__(self.message)


class InvalidIncidentTypeException(DomainException):
    """Raised when incident type is not valid (must be HUMANO or MECANICO)."""

    pass


class InvalidIncidentSeverityException(DomainException):
    """Raised when incident severity is not valid (must be LEVE or GRAVE)."""

    pass


class InvalidPlateNumberException(DomainException):
    """Raised when plate number format is invalid."""

    pass


class VehicleNotRegisteredException(DomainException):
    """Raised when vehicle plate is not registered in the system."""

    pass


class IncidentNotFoundError(DomainException):
    """Raised when an incident cannot be found by its ID."""

    pass
