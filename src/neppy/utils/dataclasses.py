"""Utility functions/types."""

from dataclasses import dataclass

from typing_extensions import dataclass_transform


@dataclass_transform(frozen_default=True)
def neppy_dataclass[T](cls: type[T]) -> type[T]:
    """Makes a class an immutable dataclass with optimized memory management."""
    return dataclass(frozen=True, slots=True)(cls)
