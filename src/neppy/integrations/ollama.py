"""Wrapper around ollama. Allows for basic prompting."""

from typing import overload

from ollama import Message, chat
from pydantic import BaseModel
from pydantic.types import T

from neppy.exceptions import InternalException


class NeppyOllamaClient:
    def __init__(self, default_model: str):
        self.default_model = default_model

    @overload
    def run(
        self,
        prompt: list[Message],
        response_type: None,
        model_override: str | None = None,
    ) -> str: ...

    @overload
    def run[T: BaseModel](
        self,
        prompt: list[Message],
        response_type: type[T],
        model_override: str | None = None,
    ) -> T: ...

    def run[T: BaseModel](
        self,
        prompt: list[Message],
        response_type: type[T] | None = None,
        model_override: str | None = None,
    ) -> T | str:
        model_to_use = model_override or self.default_model
        format_schema = response_type.model_json_schema() if response_type is not None else None
        response = chat(
            model=model_to_use,
            messages=prompt,
            format=format_schema,
        )

        response_content = response.message.content
        if response_content is None:
            raise InternalException("Model unexpectedly returned empty content")

        if response_type is not None:
            return response_type.model_validate_json(response_content)
        return response_content
