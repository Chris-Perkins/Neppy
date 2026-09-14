"""Config for Neppy based on env variables.

Note: The config is validated on import.
"""

import os

# Authentication
google_secret_file_path: str = os.environ.get("GOOGLE_SECRET_FILE_PATH") or f"{os.getcwd()}/__secrets__/google-secret.json"
# gemma4:12b is small enough to run on Nep's PC without completely fucking it
default_ollama_model = os.environ.get("DEFAULT_OLLAMA_MODEL") or "gemma4:12b"

# Storage
storage_dir_path = os.environ.get("STORAGE_PATH") or f"{os.getcwd()}/__neppystorage__"
cache_dir_path: str = os.environ.get("CACHE_DIR_PATH") or f"{storage_dir_path}/__cache__"
