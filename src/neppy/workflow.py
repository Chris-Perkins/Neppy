"""Defines workflows."""

from neppy.exceptions import InternalException
from neppy.integrations import NeppyFilestorageClient, NeppyGmailClient, NeppyOllamaClient
from neppy.utils.dataclasses import neppy_dataclass


@neppy_dataclass
class ExecutionContext:
    gmail_client: NeppyGmailClient
    filestorage_client: NeppyFilestorageClient
    ollama_client: NeppyOllamaClient


def run_workflow(ctx: ExecutionContext, workflow_code: str) -> None:
    """Run the input workflow using the input context."""
    namespace = {}
    exec(workflow_code, namespace)

    if "main" not in namespace:
        raise InternalException("Workflow code must define a 'main(ctx)' function.")

    return namespace["main"](ctx)
