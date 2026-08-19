import builtins
from pathlib import Path


def print(*args, **kwargs):
    text = " ".join(str(arg) for arg in args)

    Path("build").mkdir(parents=True, exist_ok=True)

    with open("build/build.log", "at") as file:
        file.write(text + "\n")

    builtins.print(*args, **kwargs)