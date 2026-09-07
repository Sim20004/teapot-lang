from teapot.teapot_ast import Type
from teapot.tokens import TokenType
from teapot.web import _serialise, compile_source


def test_serialise_handles_enums_dataclasses_collections_and_dict_keys():
    value = {
        TokenType.TYPE: (Type("mui8", True), [True, None]),
    }

    assert _serialise(value) == {
        "TokenType.TYPE": [
            {"name": "mui8", "mutable": True, "reference": False, "subtype": None},
            [True, None],
        ]
    }


def test_compile_source_returns_serialised_pipeline_result():
    result = compile_source(
        "$MEM-GC\n"
        "val mui8 global_value = 1.\n"
        "fc add(mui8 amount)!mui8 {\n"
        "    val mui8 local_value = amount.\n"
        "}\n"
    )

    assert result["memory_mode"] == "$MEM-GC"
    assert result["tokens"][0] == {
        "type": "DIRECTIVE",
        "value": "$MEM-GC",
        "line": 1,
        "col": 1,
    }
    assert result["ast"]["memory_mode"] == "$MEM-GC"
    assert [symbol["name"] for symbol in result["symbols"]] == [
        "global_value",
        "add",
    ]

    function = result["symbols"][1]
    assert function["kind"] == "function"
    assert [(member["name"], member["kind"]) for member in function["members"]] == [
        ("amount", "function_parameter"),
        ("local_value", "variable"),
    ]
