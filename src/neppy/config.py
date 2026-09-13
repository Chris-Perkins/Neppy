"""Config for Neppy based on env variables.

Note: The config is validated on import.
"""

import os

# Authentication
google_secret_file_path: str = os.environ.get("GOOGLE_SECRET_FILE_PATH") or f"{os.getcwd()}/__secrets__/google-secret.json"

# Caching
cache_dir_path: str = os.environ.get("CACHE_DIR_PATH") or f"{os.getcwd()}/__neppycache__"


def _validate():
    if not os.path.exists(google_secret_file_path):
        raise ValueError(f'Expected to find Google Secret credentials in "{google_secret_file_path}"')


_validate()
