from pathlib import Path
from typing import Iterable


def list_files(directory: Path) -> Iterable[Path]:
    """
    List all files in a directory.
    :param directory: Path
    :return: list of files
    """
    for path in directory.glob("**/*"):
        if path.is_file():
            yield path


def make_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)
