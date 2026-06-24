# IN BUILDING

"""Application-specific exceptions."""


class ApplicationException(Exception):
    """Base exception for all application-level errors."""

    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code or self.__class__.__name__
        super().__init__(self.message)


class IncidentNotFoundApplicationError(ApplicationException):
    """Raised when an incident cannot be found in the application layer."""

    pass



class VehicleValidationError(ApplicationException):
    """Raised when vehicle validation fails in the application layer."""

    pass
