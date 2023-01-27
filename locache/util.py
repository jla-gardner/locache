import ast
import inspect
import os
import textwrap
from pathlib import Path
from typing import Callable, Dict, Tuple

from astor import to_source

RUNNING_PATH = Path(".").absolute()


class Files:
    CODE = "code.py"


def get_file_containing(function: Callable):
    return Path(inspect.getsourcefile(function)).absolute()


def get_full_signature(func: Callable, args: Tuple, kwargs: Dict):
    signature = inspect.signature(func)
    bound = signature.bind(*args, **kwargs)
    bound.apply_defaults()
    return bound.arguments


def relative_path_to(path: Path):
    return os.path.relpath(path, RUNNING_PATH)


def remove_decorator(code: str, decorator_name: str):
    code = textwrap.dedent(code)

    def is_my_decorator(node):
        if isinstance(node, ast.Name):
            return node.id == decorator_name
        if isinstance(node, ast.Call):
            return is_my_decorator(node.func)
        return False

    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # we have hit the first function definition
            # find all decorators up to and including the one we want to remove
            # remove them

            to_keep = []
            # decorators are applied in reverse order
            for d in reversed(node.decorator_list):
                if is_my_decorator(d):
                    break
                to_keep.append(d)
            node.decorator_list = list(reversed(to_keep))

            break

    ast.fix_missing_locations(tree)
    return to_source(tree)


def get_source_code_for(func):
    code = inspect.getsource(func)
    return remove_decorator(code, "persist")
