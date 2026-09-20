"""Defines workflows."""

from neppy.exceptions import InternalException
from neppy.integrations.filestorage import NeppyFilestorageClient
from neppy.integrations.gmail import NeppyGmailClient
from neppy.integrations.llms import NeppyLLMClient
from neppy.integrations.putio import NeppyPutIOClient
from neppy.utils.dataclasses import neppy_dataclass


@neppy_dataclass
class ExecutionContext:
    gmail_client: NeppyGmailClient
    filestorage_client: NeppyFilestorageClient
    ollama_client: NeppyLLMClient
    putio_client: NeppyPutIOClient


def run_workflow(ctx: ExecutionContext, workflow_code: str) -> None:
    """Run the input workflow using the input context."""
    namespace = {}
    exec(workflow_code, namespace)

    if "main" not in namespace:
        raise InternalException("Workflow code must define a 'main(ctx)' function.")

    return namespace["main"](ctx)
