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


def test_compile_source_preserves_struct_field_declaration_order():
    """Declaration order is preserved because SymbolTable.symbols is a plain dict (insertion order guaranteed in Python 3.7+)."""
    source = "$MEM-GC\nsct Point { mui8 zeta. mui8 alpha. mui8 mu. }\n"
    result = compile_source(source)
    point = result["symbols"][0]
    assert point["kind"] == "struct"
    assert [m["name"] for m in point["members"]] == ["zeta", "alpha", "mu"]
    assert [m["kind"] for m in point["members"]] == [
        "struct_field",
        "struct_field",
        "struct_field",
    ]


def test_compile_source_preserves_enum_member_declaration_order():
    """Declaration order is preserved because SymbolTable.symbols is a plain dict (insertion order guaranteed in Python 3.7+)."""
    source = "$MEM-GC\nenm Status { Zeta. Alpha. Mu. }\n"
    result = compile_source(source)
    status = result["symbols"][0]
    assert status["kind"] == "enum"
    assert [m["name"] for m in status["members"]] == ["Zeta", "Alpha", "Mu"]
    assert [m["kind"] for m in status["members"]] == [
        "enum_member",
        "enum_member",
        "enum_member",
    ]


def test_compile_source_preserves_top_level_declaration_order():
    """Declaration order is preserved because SymbolTable.symbols is a plain dict (insertion order guaranteed in Python 3.7+)."""
    source = "$MEM-GC\nval mui8 zeta_val = 1.\nsct Alpha {}\nval mui8 mu_val = 2.\n"
    result = compile_source(source)
    assert [s["name"] for s in result["symbols"]] == ["zeta_val", "Alpha", "mu_val"]
    assert [s["kind"] for s in result["symbols"]] == ["variable", "struct", "variable"]
