"""Config for Neppy based on env variables.

Note: The config is validated on import.
"""

import os

# Integrations
google_secret_file_path: str = os.environ.get("NEPPY_GOOGLE_SECRET_FILE_PATH") or f"{os.getcwd()}/__secrets__/google-secret.json"
# qwen2.5-coder:14b is small enough to run on Nep's PC without completely fucking it
default_ollama_model = os.environ.get("NEPPY_DEFAULT_OLLAMA_MODEL") or "qwen2.5-coder:14b"

putio_client_id = os.environ.get("NEPPY_PUTIO_CLIENT_ID", "")
putio_client_secret = os.environ.get("NEPPY_PUTIO_CLIENT_SECRET", "")
putio_username = os.environ.get("NEPPY_PUTIO_USERNAME", "")
putio_password = os.environ.get("NEPPY_PUTIO_PASSWORD", "")


# Storage
storage_dir_path = os.environ.get("NEPPY_STORAGE_PATH") or f"{os.getcwd()}/__neppystorage__"
generated_workflows_dir_path = os.environ.get("NEPPY_WORKFLOWS_PATH") or "storage_dir_path/workflows"
cache_dir_path: str = os.environ.get("NEPPY_CACHE_DIR_PATH") or f"{storage_dir_path}/__cache__"
