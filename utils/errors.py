"""Error classes for Organizer MCP Server."""


class OrganizerError(Exception):
    """Base exception for organizer errors."""
    pass


class FileAccessError(OrganizerError):
    """Raised when a file cannot be accessed."""
    pass


class FileReadError(OrganizerError):
    """Raised when a file cannot be read."""
    pass


class FolderAccessError(OrganizerError):
    """Raised when a folder cannot be accessed."""
    pass


class ValidationError(OrganizerError):
    """Raised when input validation fails."""
    pass


class OperationError(OrganizerError):
    """Raised when an operation fails."""
    pass
