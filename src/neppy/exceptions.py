"""Exceptions raised by Neppy logic."""


class NeppyException(Exception):
    """Top-level exception raised when Neppy-specific erroring occurs."""


class NotFoundException(NeppyException):
    """Indicates an item does not exist."""


class BadRequestException(NeppyException):
    """Indicates something failed because of a user skill issue."""


class InternalException(NeppyException):
    """Indicates something failed because of a developer skill issue."""
