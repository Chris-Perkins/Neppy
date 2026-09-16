"""Key-based filestorage implementation.."""

from pathlib import Path

from neppy.exceptions import NotFoundException


class NeppyFilestorageClient:
    """Key-based local filestorage client - intended to be used as a simple persistence layer."""

    def __init__(self, base_storage_path: Path):
        if base_storage_path.exists() and not base_storage_path.is_dir():
            raise Exception("base_storage_path must be a directory")
        self.base_storage_path = base_storage_path
        self.base_storage_path.mkdir(parents=True, exist_ok=True)

    def list_keys(self, *, with_prefix: str | None = None) -> list[str]:
        """List keys available in filestorage.

        Args:
            with_prefix (str, optional): If specified, only keys that start with this value are returned.

        Returns:
            All keys available that match the input filters.
        """
        output = _get_all_files_in_directory(self.base_storage_path)
        if with_prefix is not None:
            output = [key for key in output if key.startswith(with_prefix)]
        return output

    def set_value(self, key: str, value: str) -> None:
        """Set ``value`` at ``key``.

        Args:
            key (str): Where the value is store
            value (str): The value to store

        Returns:
            None
        """
        target_path = self.base_storage_path.joinpath(key)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(value)

    def get_value(self, key: str) -> str:
        """Gets the value stored at the input key.

        Args:
            key (str): The key to get the value of

        Returns:
            The value stored at `key`.

        Raises:
            NotFoundException: if nothing is stored at `key`.
        """
        value = self.get_value_or_none(key)
        if value is None:
            raise NotFoundException("No item is stored at `key`.")
        return value

    def get_value_or_none(self, key: str) -> str | None:
        """Gets the value stored at the input key, or none if no value is stored.

        Args:
            key (str): The key to get the value of

        Returns:
            The value stored at "key", or None if it does not exist.
        """
        target_path = self.base_storage_path.joinpath(key)
        if not target_path.exists():
            return None
        return target_path.read_text()


def _get_all_files_in_directory(directory: Path, *, recursive: bool = True) -> list[str]:
    """Lists files in the input directory."""
    if not directory.exists():
        return []
    paths = directory.rglob("*") if recursive else directory.glob("*")
    return [str(path.relative_to(directory)) for path in paths if path.is_file()]
