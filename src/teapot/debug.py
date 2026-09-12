from teapot.output import get_output


def print(*args, **kwargs):
    """Compatibility wrapper used by existing compiler trace calls."""

    sep = kwargs.pop("sep", " ")
    end = kwargs.pop("end", "\n")
    stream = kwargs.pop("file", None)
    if kwargs:
        raise TypeError(f"unsupported output options: {', '.join(kwargs)}")
    text = sep.join(str(arg) for arg in args) + end.rstrip("\n")
    get_output().write(text, level="info", stream=stream)
