"""Defines workflows."""

from sqlite3 import InternalError

from neppy.integrations.filestorage import NeppyFilestorageClient
from neppy.integrations.gmail import NeppyGmailClient
from neppy.utils.dataclasses import neppy_dataclass


@neppy_dataclass
class WorkflowContext:
    gmail_client: NeppyGmailClient
    filestorage_client: NeppyFilestorageClient


def run_workflow(ctx: WorkflowContext, workflow_code: str) -> None:
    """Run the input workflow using the input context."""
    namespace = {}
    exec(workflow_code, namespace)

    if "main" not in namespace:
        raise InternalError("Workflow code must define a 'main(ctx)' function.")

    return namespace["main"](ctx)
