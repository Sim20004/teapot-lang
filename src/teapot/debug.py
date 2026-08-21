import builtins
from pathlib import Path


# Shadows built-in print() function with one that prints and writes to build/build.log.
def print(*args, **kwargs):
    # Keep trace output visible while making it available for later inspection.
    text = " ".join(str(arg) for arg in args)

    Path("build").mkdir(parents=True, exist_ok=True)

    with open("build/build.log", "at") as file:
        file.write(text + "\n")

    builtins.print(*args, **kwargs)