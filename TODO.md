# Teapot Compiler TODO

## Lexer

### Core lexer
- [x] Create TokenType enum
- [x] Create Token dataclass
- [x] Create Lexer class
- [x] Add source handling
- [x] Add CRLF to LF conversion
- [x] Add current_character()
- [x] Add advance()
- [x] Add tokenise()

### Token recognition
- [ ] Implement read_word()
  - [x] Keywords
  - [x] Types
  - [x] Boolean literals
  - [x] Identifiers

- [ ] Implement read_number()
  - [ ] Integers
  - [ ] Floats
  - [ ] Decimal literals

- [ ] Implement read_string()
  - [ ] Normal strings
  - [ ] Escape sequences (`\n`, `\"`, etc.)

- [ ] Implement read_character()
  - [ ] Single characters
  - [ ] Escape sequences

- [ ] Implement read_symbol()
  - [ ] Arithmetic operators
  - [ ] Comparison operators
  - [ ] Logical operators
  - [ ] Assignment operators
  - [ ] Punctuation

### Comments
- [ ] Single-line comments (`//`)
- [ ] Multi-line comments (`/* */`)
- [ ] Ignore comment markers inside strings

### Lexer validation
- [ ] Track correct line numbers
- [ ] Track correct column numbers
- [ ] Add lexer error messages
- [ ] Test invalid characters
- [ ] Test unfinished strings/comments


# Parser

## AST
- [ ] Design AST node system
- [ ] Create AST classes

## Parsing
- [ ] Parse variable declarations
- [ ] Parse expressions
- [ ] Parse operators
- [ ] Parse function declarations
- [ ] Parse function calls
- [ ] Parse return statements
- [ ] Parse if/elif/else
- [ ] Parse while loops
- [ ] Parse for loops
- [ ] Parse structs
- [ ] Parse enums
- [ ] Parse lists
- [ ] Parse maps
- [ ] Parse tuples
- [ ] Parse imports


# Semantic Analysis

- [ ] Variable scope checking
- [ ] Type checking
- [ ] Function signature checking
- [ ] Function overload resolution
- [ ] Constant mutation checking
- [ ] Return type checking
- [ ] Undefined variable detection


# Interpreter (first release)

## Runtime
- [ ] Create environment/scope system
- [ ] Store variables
- [ ] Execute expressions
- [ ] Execute statements
- [ ] Execute functions
- [ ] Implement built-in functions

## Memory
- [ ] Decide first release memory model
- [ ] Implement basic memory management


# Standard Library

- [ ] String functions
- [ ] Math functions
- [ ] File handling
- [ ] Input/output


# Testing

- [ ] Lexer tests
- [ ] Parser tests
- [ ] Runtime tests
- [ ] Error tests
- [ ] Example Teapot programs


# First Release Goal

Minimum working language:

- [ ] Variables
- [ ] Basic types
- [ ] Arithmetic
- [ ] Comparisons
- [ ] If statements
- [ ] While loops
- [ ] Functions
- [ ] Return values
- [ ] Printing output
- [ ] Error messages