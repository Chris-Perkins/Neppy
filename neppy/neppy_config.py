"""
Config for Neppy based on env variables
"""

import os

# Authentication
google_secret_path = os.environ["GOOGLE_SECRET_PATH"]

# Caching
cache_folder_path = os.environ.get("CACHE_PATH") or os.path.join(os.get_exec_path(), "/__neppycache__/")
