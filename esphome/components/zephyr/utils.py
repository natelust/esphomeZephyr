from contextlib import contextmanager
from pathlib import Path
from typing import Union

import os

@contextmanager
def at_location(path: Union[os.PathLike, str]):
    cwd = Path().absolute()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(cwd)


@contextmanager
def swap_build_path(path: str):
    from esphome.core import CORE
    current_dir = CORE.build_path
    try:
        CORE.build_path = path
        yield
    finally:
        CORE.build_path = current_dir