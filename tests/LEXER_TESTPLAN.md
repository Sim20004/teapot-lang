| Test                                       | What it verifies                                   | Written? 
| ------------------------------------------ | -------------------------------------------------- | ---------
| `test_empty_source`                        | Empty source produces only `EOF`                   | X
| `test_eof_position`                        | EOF has the correct line/column                    | X
| `test_whitespace_is_ignored`               | Spaces, tabs and newlines don't create tokens      | X
| `test_crlf_is_normalised`                  | `\r\n` is converted to `\n`                        | X
| `test_single_line_comment`                 | `//` comments are ignored                          | X
| `test_comment_at_eof`                      | Comment without a trailing newline works           | X
| `test_identifier`                          | Normal identifiers are recognised                  | X
| `test_identifier_with_underscore`          | Underscores work                                   | X
| `test_identifier_starting_with_underscore` | `_foo` works                                       | X
| `test_identifier_with_numbers`             | Numbers are allowed after the first character      | X
| `test_keyword`                             | Every keyword becomes the correct token type       | X
| `test_datatype_keyword`                    | Every datatype becomes `TYPE`                      | X
| `test_boolean_true`                        | `true` becomes a boolean `True`                    | X
| `test_boolean_false`                       | `false` becomes a boolean `False`                  | X
| `test_integer`                             | Integers are parsed correctly                      | X
| `test_float`                               | Decimal numbers are parsed correctly               | X
| `test_multiple_numbers`                    | Multiple numeric tokens are separated correctly    | X
| `test_float_followed_by_symbol`            | `1.5.` doesn't incorrectly consume the final `.`   | X
| `test_duplicate_decimal_point`             | Invalid numbers such as `1.2.3` raise `LexerError` |
| `test_string`                              | Basic strings work                                 |
| `test_empty_string`                        | `""` works                                         |
| `test_string_with_spaces`                  | Spaces inside strings are preserved                |
| `test_string_with_symbols`                 | Symbols inside strings aren't tokenised separately |
| `test_unterminated_string`                 | Missing closing `"` raises `LexerError`            |
| `test_single_character_symbols`            | Every single-character symbol works                |
| `test_two_character_symbols`               | Every two-character symbol works                   |
| `test_two_character_symbol_precedence`     | `==`, `<=`, etc. aren't split into two tokens      |
| `test_invalid_symbol`                      | Unknown symbols raise `LexerError`                 |
| `test_directive`                           | Valid directives are recognised                    |
| `test_invalid_directive`                   | Unknown `$...` directives raise `LexerError`       |
| `test_duplicate_directive`                 | Two directives raise `LexerError`                  |
| `test_directive_value`                     | Directive token contains the correct value         |
| `test_line_tracking`                       | Tokens on later lines get correct line numbers     |
| `test_column_tracking`                     | Tokens get correct starting columns                |
| `test_multiline_source`                    | Line/column tracking survives multiple lines       |
| `test_error_position`                      | Lexer errors report the correct position           |
| `test_mixed_source`                        | A realistic Teapot program tokenises correctly     |
| `test_all_keywords`                        | Every entry in `KEYWORDS` is tested                |
| `test_all_types`                           | Every entry in `TYPE_KEYWORDS` is tested           |
| `test_all_symbols`                         | Every entry in `SYMBOLS` is tested                 |
