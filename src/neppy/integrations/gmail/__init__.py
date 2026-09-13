"""Neppy's Google integration with Gmail support."""

from .client import NeppyGmailClient
from .types import ListMessagesOptions, ListMessagesResult, Message

__all__ = [
    "NeppyGmailClient",
    "Message",
    "ListMessagesOptions",
    "ListMessagesResult",
]
