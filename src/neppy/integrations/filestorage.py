"""Key-based filestorage implementation.."""

from pathlib import Path


class NeppyFilestorageClient:
    """Key-based local filestorage client - used as a naive persistence layer."""

    def __init__(self, base_storage_path: Path):
        if base_storage_path.exists() and not base_storage_path.is_dir():
            raise Exception("base_storage_path must be a directory")
        self.base_storage_path = base_storage_path
        self.base_storage_path.mkdir(parents=True, exist_ok=True)

    def list_keys(self, *, with_prefix: str | None = None) -> list[str]:
        output = _get_all_files_in_directory(self.base_storage_path)
        if with_prefix is not None:
            output = [key for key in output if key.startswith(with_prefix)]
        return output

    def set(self, key: str, value: str) -> None:
        target_path = self.base_storage_path.joinpath(key)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(value)

    def get(self, key: str) -> str:
        target_path = self.base_storage_path.joinpath(key)
        return target_path.read_text()

    def get_or_none(self, key: str) -> str | None:
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
