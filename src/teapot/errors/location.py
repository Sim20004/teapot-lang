from dataclasses import dataclass


@dataclass(frozen=True)
class SourceLocation:
    line: int | None = None
    column: int | None = None
    position: int | None = None

    def __str__(self):
        if self.line is not None and self.column is not None:
            return f"{self.line}:{self.column}"
        if self.position is not None:
            return f"offset {self.position}"
        return "unknown location"


def location_from(value, position=None):
    if value is None:
        return SourceLocation(position=position)
    return SourceLocation(
        getattr(value, "line", None),
        getattr(value, "col", getattr(value, "column", None)),
        position,
    )
