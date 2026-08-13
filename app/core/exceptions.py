"""Domain errors translated to HTTP responses at the API boundary."""


class DomainError(Exception):
    """Base class for expected business-rule failures."""


class ConflictError(DomainError):
    """A requested resource conflicts with existing state."""


class NotFoundError(DomainError):
    """A resource does not exist or is not accessible to the caller."""


class AuthenticationError(DomainError):
    """Authentication failed without revealing the exact reason."""


class AuthorizationError(DomainError):
    """The caller is authenticated but lacks the required permission."""


class ValidationDomainError(DomainError):
    """A request is structurally valid but violates a business rule."""


class RateLimitError(DomainError):
    """Client request limit has been exceeded."""
