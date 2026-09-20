"""Wrapper around ollama. Allows for basic prompting."""

from typing import overload

from ollama import Message, chat
from pydantic import BaseModel
from pydantic.types import T

from neppy.exceptions import InternalException


class NeppyLLMClient:
    """Enables usage of of local LLMs."""

    def __init__(self, default_model: str):
        self.default_model = default_model

    @overload
    def chat(
        self,
        prompt: list[Message],
        *,
        model_override: str | None = None,
    ) -> str: ...

    @overload
    def chat[T: BaseModel](
        self,
        prompt: list[Message],
        *,
        response_type: type[T],
        model_override: str | None = None,
    ) -> T: ...

    def chat[T: BaseModel](
        self,
        prompt: list[Message],
        *,
        response_type: type[T] | None = None,
        model_override: str | None = None,
    ) -> T | str:
        """Run the input prompt against the input model.

        Args:
            prompt (list[Message]): The prompt to run through the LLM.
            response_type (BaseModel type, optional): The type of class that should be returned. If not specified, a string is returned.
            model_override (str, optional): The LLM model to execute on. If not specified, the client's `default_model` will be used.

        Returns:
            the result of the LLM, casted to response_type (if set) or a string otherwise.

        Example:
            ```py
            result = ollama_client.chat([
                Message(role="system", content="Help the user with their request. Answer concisely and truthfully."),
                Message(role="user", content="Is Coca-Cola good for me?"),
            ])
            ```
        """
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
