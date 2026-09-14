"""Entry point of Neppy."""

from pathlib import Path

from ollama import Message
from pydantic import BaseModel

from neppy.integrations import NeppyFilestorageClient, NeppyGmailClient, NeppyOllamaClient
from neppy.workflow import WorkflowContext
import neppy.config


def main():
    print("Starting Neppy")

    filestorage_client = NeppyFilestorageClient(Path(neppy.config.storage_dir_path))
    gmail_client = NeppyGmailClient(neppy.config.google_secret_file_path)
    ollama_client = NeppyOllamaClient(default_model=neppy.config.default_ollama_model)

    class TestClass(BaseModel):
        question_received: bool

    result = ollama_client.run([Message(role="user", content="Did you receive this question?")], response_type=TestClass)

    ctx = WorkflowContext(
        gmail_client=gmail_client,
        filestorage_client=filestorage_client,
    )


if __name__ == "__main__":
    main()
