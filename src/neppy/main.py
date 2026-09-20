"""Entry point of Neppy."""

from pathlib import Path

from neppy.integrations.filestorage import NeppyFilestorageClient
from neppy.integrations.gmail import NeppyGmailClient
from neppy.integrations.ollama import NeppyOllamaClient
from neppy.integrations.putio import NeppyPutIOClient
from neppy.workflow import ExecutionContext
import neppy.config
import neppy.workflows.workflow_generator


def main():
    print("Starting Neppy")

    filestorage_client = NeppyFilestorageClient(Path(neppy.config.storage_dir_path))
    gmail_client = NeppyGmailClient(neppy.config.google_secret_file_path)
    ollama_client = NeppyOllamaClient(default_model=neppy.config.default_ollama_model)
    putio_client = NeppyPutIOClient(
        client_id=neppy.config.putio_client_id,
        client_secret=neppy.config.putio_client_secret,
        putio_username=neppy.config.putio_username,
        putio_password=neppy.config.putio_password,
    )

    ctx = ExecutionContext(
        gmail_client=gmail_client,
        filestorage_client=filestorage_client,
        ollama_client=ollama_client,
        putio_client=putio_client,
    )
    ...


if __name__ == "__main__":
    main()
