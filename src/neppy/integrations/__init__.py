"""All external integrations available to Neppy.

This is similar to a naive MCP.
"""

from .filestorage import NeppyFilestorageClient
from .gmail import NeppyGmailClient

__all__ = [
    "NeppyFilestorageClient",
    "NeppyGmailClient",
]
