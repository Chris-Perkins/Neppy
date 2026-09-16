from dataclasses import fields
from pathlib import Path
import inspect

from ollama import Message
from pydantic import BaseModel

from neppy.exceptions import InternalException
from neppy.utils.dataclasses import neppy_dataclass
from neppy.workflow import ExecutionContext
import neppy.config


@neppy_dataclass
class _PseudoHTMLElement:
    label: str
    content: str | None = None
    children: list[_PseudoHTMLElement] | None = None

    def __str__(self) -> str:
        output_lines: list[str] = []
        output_lines.append(f"<{self.label}>")
        if self.content is not None:
            indented_content = "\n".join(f"  {line}" for line in self.content.splitlines())
            output_lines.append(indented_content)
        for child in self.children or []:
            child_lines = str(child).splitlines()
            output_lines.extend(f"  {child_line}" for child_line in child_lines)
        output_lines.append(f"</{self.label}>")
        return "\n".join(output_lines)


def main(ctx: ExecutionContext, **kwargs) -> None:
    user_request: str = kwargs["user_request"]
    workflow_storage_path = Path(neppy.config.generated_workflows_dir_path)
    prompt = _generate_workflow_generation_prompt(user_request)

    class CodeGenerationResponseType(BaseModel):
        file_name: str
        python_code: str

    code_generation_result = ctx.ollama_client.chat(prompt=prompt, response_type=CodeGenerationResponseType)
    suggested_storage_location = workflow_storage_path.joinpath(code_generation_result.file_name)
    if suggested_storage_location.exists():
        raise InternalException(f"Agent wants to save workflow in a file that already exists: {suggested_storage_location}")
    suggested_storage_location.parent.mkdir(parents=True, exist_ok=True)
    suggested_storage_location.write_text(code_generation_result.python_code)


def _generate_workflow_generation_prompt(user_request: str) -> list[Message]:
    return [
        Message(
            role="system",
            content=f"""
# Context

You are an expert Python coder capable of building functional scripts.

# Task

A user is going to ask you to build a script. The script you generate must have a function with the following format:

```py
from neppy.workflow import ExecutionContext

def main(ctx: ExecutionContext) -> None:
    # TODO: Fill in this function. This function should meet the requirements of the script the user requested.
    # If parameters are needed, add them as keyword-only arguments 
    # Example: `def main(ctx: ExecutionContext, *, arg1: str)`
```

Do not include the leading or trailing '`' characters that define the codeblock. The code output will be placed
directly into a Python file.

Give the script a name - the name should be descriptive of its intended usage.

## ExecutionContext

{_generate_execution_context_instructions()}

# Rules

- You may import any standard python library in the script
- You may also import from any package in neppy.integrations
- Code quality is not of concern; functionality is the most important.
- Aim for simple code. The code should not be overengineered
""",
        ),
        Message(
            role="user",
            content=f"""
# Task

Generate a Python script that does the following: {user_request}
""",
        ),
    ]


def _generate_execution_context_instructions() -> str:
    execution_context_instructional_elements = [
        _PseudoHTMLElement(
            "property",
            children=[
                _PseudoHTMLElement("name", content=field.name),
                _PseudoHTMLElement("members", children=_generate_html_elements_for_class(field.type)),  # pyright: ignore[reportArgumentType] - this is always a Type, but Python be tweaking.
            ],
        )
        for field in fields(ExecutionContext)
    ]

    return f"""ctx: ExecutionContext is a custom datatype, with the following properties:

{"\n".join(str(element) for element in execution_context_instructional_elements)}"""


def _generate_html_elements_for_class(class_type: type) -> list[_PseudoHTMLElement]:
    output: list[_PseudoHTMLElement] = []
    field_functions = inspect.getmembers(class_type, inspect.isfunction)
    for name, fn in field_functions:
        is_private_fn = name.startswith("_")
        if is_private_fn:
            continue
        output.append(_PseudoHTMLElement(label="function", children=[_PseudoHTMLElement("name", content=name), _PseudoHTMLElement(label="documentation", content=inspect.getdoc(fn))]))
    return output
