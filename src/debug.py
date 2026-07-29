import builtins

def print(*args, **kwargs):
    text = " ".join(str(arg) for arg in args)

    with open("build/build.log", "at") as file:
        file.write(text + "\n")

    builtins.print(*args, **kwargs)