import io
import json
from enum import Enum

from teapot.errors import InvalidTypeError
from teapot.errors.location import SourceLocation, location_from
from teapot.output import Output, OutputOptions


def make_output(**options):
    stream = io.StringIO()
    return Output(OutputOptions(**options), stdout=stream), stream


def test_output_writes_plain_messages_without_terminal_colour():
    output, stream = make_output(color="auto")

    output.write("ready")

    assert stream.getvalue() == "ready\n"
    assert "\033[" not in stream.getvalue()


def test_output_always_colourizes_messages_when_requested():
    output, stream = make_output(color="always")

    output.write("warning", level="warning")

    assert "\033[33mwarning\033[0m" in stream.getvalue()


def test_auto_colour_uses_terminal_capability():
    class Terminal(io.StringIO):
        def isatty(self):
            return True

    stream = Terminal()
    output = Output(OutputOptions(color="auto"), stdout=stream)

    output.write("info")

    assert "\033[36minfo\033[0m" in stream.getvalue()


def test_output_never_disables_colour_even_for_forced_diagnostics():
    output, stream = make_output(color="never")
    error = InvalidTypeError(
        "expected int, found str",
        location=SourceLocation(4, 2),
    )

    output.diagnostic(error)

    assert "\033[" not in stream.getvalue()
    assert "4:2" in stream.getvalue()
    assert "Hint:" in stream.getvalue()


def test_quiet_suppresses_info_but_not_diagnostics():
    output, stream = make_output(quiet=True)
    error = InvalidTypeError("bad type", location=SourceLocation(1, 1))

    output.write("trace", level="trace")
    output.diagnostic(error)

    assert "trace" not in stream.getvalue()
    assert "bad type" in stream.getvalue()


def test_trace_warning_and_verbose_helpers_route_through_output():
    output, stream = make_output(verbosity=1)

    output.trace("trace")
    output.warning("warning")
    output.verbose("verbose")

    assert stream.getvalue().splitlines() == ["trace", "warning", "verbose"]


def test_verbose_helper_is_silent_at_default_verbosity():
    output, stream = make_output()

    output.verbose("verbose")

    assert stream.getvalue() == ""


def test_json_diagnostics_are_machine_readable():
    output, stream = make_output(diagnostic_format="json")
    error = InvalidTypeError("expected int, found str", location=SourceLocation(7, 3))

    output.diagnostic(error)

    payload = json.loads(stream.getvalue())
    assert payload["code"] == "invalid-type"
    assert payload["location"] == "7:3"
    assert payload["hint"]


def test_full_json_details_do_not_expose_ast_representations():
    output, stream = make_output(
        diagnostic_format="json",
        diagnostic_detail="full",
    )
    error = InvalidTypeError(
        "bad type",
        location=SourceLocation(3, 1),
        node="internal AST node",
    )

    output.diagnostic(error)

    payload = json.loads(stream.getvalue())
    assert "details" in payload
    assert "node" not in payload["details"]
    assert "internal AST node" not in stream.getvalue()


def test_concise_diagnostics_omit_hints():
    output, stream = make_output(diagnostic_detail="concise")
    error = InvalidTypeError("bad type", location=SourceLocation(2, 1))

    output.diagnostic(error)

    assert "bad type" in stream.getvalue()
    assert "Hint:" not in stream.getvalue()


def test_output_can_write_a_custom_log_file(tmp_path):
    log_file = tmp_path / "logs" / "teapot.log"
    output, stream = make_output(log_file=log_file)

    output.write("trace event", level="trace")

    assert stream.getvalue() == "trace event\n"
    assert log_file.read_text() == "trace event\n"


def test_full_text_diagnostics_include_code():
    output, stream = make_output(diagnostic_detail="full")
    error = InvalidTypeError("bad type", location=SourceLocation(2, 1))

    output.diagnostic(error)

    assert "[invalid-type]" in stream.getvalue()


def test_output_ignores_unknown_configuration_keys():
    output, stream = make_output()

    output.configure(unknown_option=True)
    output.write("still works")

    assert stream.getvalue() == "still works\n"


def test_detail_values_avoid_internal_object_representations():
    class Named(Enum):
        VALUE = "value"

    class WithValue:
        value = "plain value"

    class Internal:
        pass

    assert Output._detail_value(None) is None
    assert Output._detail_value(Named.VALUE) == "VALUE"
    assert Output._detail_value(WithValue()) == "plain value"
    assert Output._detail_value(Internal()) == "Internal"


def test_source_location_fallbacks_are_stable():
    assert str(SourceLocation(position=9)) == "offset 9"
    assert str(SourceLocation()) == "unknown location"
    assert location_from(None, position=4).position == 4
    assert location_from(type("Token", (), {"line": 3, "col": 2})()) == SourceLocation(
        3, 2
    )
