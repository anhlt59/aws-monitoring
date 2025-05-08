import re
import subprocess  # nosec
import sys
from typing import Literal

from src.common.exceptions.system import CommandFailureError

PROC_OUTPUT = Literal["PIPE", "STDOUT", "DEVNULL"]


def execute_command(command: str, output: PROC_OUTPUT = "STDOUT", return_code: bool = False) -> str:
    """
    Run a command and return the output.
    :param command: (str) command to run
    :param output: STDOUT  - sys stdout
                   PIPE    - return output
                   DEVNULL - discard output
    :param return_code: (bool) if True, return the return code of the command
    :return: str
    """
    match output:
        case "STDOUT":
            stdout = sys.stdout
        case "PIPE":
            stdout = subprocess.PIPE
        case "DEVNULL":
            stdout = subprocess.DEVNULL
        case _:
            raise ValueError("Invalid output type, use 'PIPE', 'STDOUT' or 'DEVNULL'")

    with subprocess.Popen(
        re.split(r"\s|\n", command),
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdout=stdout,
        universal_newlines=True,
        bufsize=-1,
    ) as process:  # nosec
        if stdout == subprocess.DEVNULL:
            return ""
        stdout, stderr = process.communicate()
        if return_code:
            return process.returncode
        if process.returncode != 0:
            raise CommandFailureError(f"COMMAND ERROR: {stderr}")
        return stdout
