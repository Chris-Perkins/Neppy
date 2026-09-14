"""Entry point of Neppy."""

from pathlib import Path

from neppy.integrations import NeppyFilestorageClient, NeppyGmailClient, NeppyOllamaClient
from neppy.workflow import WorkflowContext
import neppy.config


def main():
    print("Starting Neppy")

    filestorage_client = NeppyFilestorageClient(Path(neppy.config.storage_dir_path))
    gmail_client = NeppyGmailClient(neppy.config.google_secret_file_path)
    ollama_client = NeppyOllamaClient(default_model=neppy.config.default_ollama_model)

    ctx = WorkflowContext(gmail_client=gmail_client, filestorage_client=filestorage_client, ollama_client=ollama_client)


if __name__ == "__main__":
    main()
