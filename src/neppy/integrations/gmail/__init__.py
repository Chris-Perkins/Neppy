"""Neppy's Google integration with Gmail support."""

from .client import NeppyGmailClient
from .types import ListThreadsOptions, ListThreadsResult, Message, Thread

__all__ = [
    "NeppyGmailClient",
    "ListThreadsOptions",
    "ListThreadsResult",
    "Message",
    "Thread",
]
