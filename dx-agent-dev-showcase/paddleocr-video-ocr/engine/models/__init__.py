from typing import Dict, List


PREPROCESSING = Dict[str, Dict[str, str | int | float | List[int | float]]]


def make_indent_string(string: str, num_indent: int = 2) -> str:
    indent = " " * num_indent
    return f"{indent}{string}"
