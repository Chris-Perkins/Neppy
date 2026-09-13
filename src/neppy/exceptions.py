"""Exceptions raised by Neppy logic."""


class NeppyException(Exception):
    """Top-level exception raised when Neppy-specific erroring occurs."""


class BadRequestException(NeppyException):
    """Indicates something failed because of a user skill issue."""


class InternalException(NeppyException):
    """Indicates something failed because of a developer skill issue."""
