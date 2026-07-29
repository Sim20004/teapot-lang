# Parser TODO List

## Parser architecture

* [x] Create `handle_statement()`

  * [x] Central statement dispatcher
  * [x] Replace large `if/elif` chain in `parse()`
  * [x] Return AST nodes instead of directly appending everywhere

* [x] Create `handle_block()`

  * [x] Parse `{ }`
  * [x] Store statements inside block AST node
  * [x] Support nested scopes

* [ ] Create `parse_type()`

  * [ ] Primitive types
  * [ ] Mutable types
  * [ ] Constant types
  * [ ] Reference types
  * [ ] Arrays
  * [ ] Lists
  * [ ] Maps
  * [ ] Struct types

* [ ] Create `parse_identifier()`

  * [ ] Validate identifier usage
  * [ ] Prevent reserved words being used

* [ ] Add parser state:

  * [ ] Current scope
  * [ ] Memory mode
  * [ ] Current function
  * [ ] Current loop depth
  * [ ] Current imports

---

# Program structure

* [ ] Parse program root

Support:

```teapot
$MEM-GC

statements...
```

* [ ] Require memory directive at file start
* [ ] Store memory mode in `Program` AST node
* [ ] Reject unknown directives

---

# Directives

* [x] `$MEM-GC`

Behaviour:

* [x] Enable garbage collection mode

* [x] `$MEM-MANUAL`

Behaviour:

* [x] Require manual freeing
* [ ] Validate `free` usage later

---

# Variables

## Declaration

Support:

```teapot
val mui8 x = 5.
```

Add:

* [x] Parse `val`
* [x] Parse datatype
* [x] Parse identifier
* [x] Parse assignment
* [x] Parse expression

---

## Uninitialised variables

Support:

```teapot
val mui8 x.
```

Add:

* [x] Default value = null
* [x] Type retained

---

## Mutable variables

Support:

```teapot
val mui8 x = 5.
```

Add:

* [x] Mutable type recognition

---

## Constant variables

Support:

```teapot
val cui8 x = 5.
```

Add:

* [x] Constant type recognition
* [x] Mark AST as immutable

---

## References

Support:

```teapot
val ref mui8 x = y.
```

Add:

* [ ] Parse `ref`
* [ ] Create reference AST node
* [ ] Validate reference target

---

# Types

Create type parser.

## Primitive types

Support:

* [ ] void
* [ ] str
* [ ] char
* [ ] bln
* [ ] aint
* [ ] dml
* [ ] f32
* [ ] f64

---

## Integer types

Support:

* [ ] si8
* [ ] si16
* [ ] si32
* [ ] si64
* [ ] ui8
* [ ] ui16
* [ ] ui32
* [ ] ui64

---

## Type modifiers

Support:

* [ ] m prefix

Example:

```teapot
mui8
```

* [ ] c prefix

Example:

```teapot
cui8
```

---

# Expressions

## Primary expressions

Support:

* [ ] Integer literals
* [ ] Float literals
* [ ] Boolean literals
* [ ] String literals
* [ ] Character literals
* [ ] Null literal
* [ ] Identifiers
* [ ] Parentheses

---

## Unary expressions

Support:

* [ ] `~`
* [ ] Future unary operators

---

## Binary expressions

Support:

### Arithmetic

* [ ] `+`
* [ ] `-`
* [ ] `*`
* [ ] `/`
* [ ] `%`
* [ ] `**`

### Comparison

* [ ] `==`
* [ ] `>`
* [ ] `<`
* [ ] `>=`
* [ ] `<=`
* [ ] `~=`

### Logical

* [ ] `&&`
* [ ] `||`

---

## Assignment expressions

Support:

* [ ] `=`
* [ ] `+=`
* [ ] `-=`
* [ ] `*=`
* [ ] `/=`

---

## Casting

Support:

```teapot
x >> mui8
```

Add:

* [ ] Cast AST node
* [ ] Parse target type

---

# Functions

## Function declaration

Support:

```teapot
fc main()!void {

}
```

Add:

* [ ] Parse `fc`
* [ ] Parse function name
* [ ] Parse arguments
* [ ] Parse return type
* [ ] Parse body

---

## Arguments

Support:

```teapot
fc add(mui8 x)!void
```

Add:

* [ ] Argument type
* [ ] Argument name
* [ ] Multiple arguments

---

## Default arguments

Support:

```teapot
fc hello(str name = "User")
```

Add:

* [ ] Default value parsing

---

## Function overloading

Add:

* [ ] Store parameter signature
* [ ] Detect duplicate signatures
* [ ] Allow same name with different parameters

---

## Function calls

Support:

```teapot
hello().
```

Add:

* [ ] FunctionCall AST
* [ ] Parse arguments
* [ ] Nested calls

---

## Return

Support:

```teapot
exit value.
```

Add:

* [ ] Exit AST node
* [ ] Validate inside function

---

# Visibility

Support:

```teapot
pub fc main()!void {

}
```

Add:

* [ ] Parse `pub`
* [ ] Public flag on AST nodes
* [ ] Default private

---

# Control flow

## If

Support:

```teapot
if(condition){

}
```

Add:

* [ ] Condition expression
* [ ] Body block

---

## Else if

Support:

```teapot
elif(condition){

}
```

Add:

* [ ] Multiple branches

---

## Else

Support:

```teapot
else {

}
```

Add:

* [ ] Else body

---

# Loops

## While

Support:

```teapot
while(condition){

}
```

Add:

* [ ] Condition
* [ ] Body

---

## For

Support:

```teapot
for(item : list){

}
```

Add:

* [ ] Iterator variable
* [ ] Iterable expression
* [ ] Body

---

# Loop control

Add:

* [ ] `break`
* [ ] `continue`

Add validation:

* [ ] Only allowed inside loops

---

# Structs

## Declaration

Support:

```teapot
sct Person {

}
```

Add:

* [ ] Struct AST
* [ ] Field list
* [ ] Field types

---

## Struct creation

Support:

```teapot
Person("Bob",15)
```

Add:

* [ ] Constructor expression

---

## Field access

Support:

```teapot
person::name
```

Add:

* [ ] FieldAccess AST

---

# Enums

## Declaration

Support:

```teapot
enm Colour {

}
```

Add:

* [ ] Enum AST
* [ ] Enum values

---

## Usage

Support:

```teapot
Colour::Red
```

Add:

* [ ] Enum access AST

---

# Arrays

Support:

```teapot
val mui8[] ages = [1,2,3].
```

Add:

* [ ] Array type parser
* [ ] Array literal parser

---

# Lists

Support:

```teapot
list<ui8>
```

Add:

* [ ] Generic type parser
* [ ] List AST

---

# Maps

Support:

```teapot
map[str]ui8
```

Add:

* [ ] Key type parsing
* [ ] Value type parsing
* [ ] Map literal parsing

---

# Tuples

Support:

```teapot
(10, hello)
```

Add:

* [ ] Tuple AST
* [ ] Multiple expressions

---

# Imports

Support:

```teapot
attach file.
```

Add:

* [ ] Import AST

Support:

```teapot
attach file::function.
```

Add:

* [ ] Specific import

Support:

```teapot
attach file as foo.
```

Add:

* [ ] Alias

---

# Memory management

## Manual mode

Add:

```teapot
object::free()
```

Support:

* [ ] Free expression
* [ ] Free AST node
* [ ] Validate ownership

---

## GC mode

Support:

* [ ] Mark program as GC
* [ ] Generate GC metadata later

---

# Error handling

## Error declaration

Support:

```teapot
err FileError {

}
```

Add:

* [ ] Error type AST

---

## Error blocks

Support:

```teapot
do {

}

fail(FileError e){

}
```

Add:

* [ ] Do block
* [ ] Fail block
* [ ] Error variable

---

# Custom operators

Support:

```teapot
operator +(Vector a, Vector b)!Vector {

}
```

Add:

* [ ] Operator function AST
* [ ] Parse operator symbol
* [ ] Parse arguments
* [ ] Parse return type

---

# Comments

Lexer probably handles this, but parser should ensure:

* [ ] Comments cannot affect grammar
* [ ] Comments inside strings are ignored

---

# AST improvements

Add nodes:

```
Program
Block

VariableDeclaration
Assignment

Literal
Identifier

BinaryExpression
UnaryExpression
CastExpression

Function
FunctionArgument
FunctionCall
Return

If
While
For

Break
Continue

Struct
StructField
Enum
EnumValue

Array
List
Map
Tuple

Import

Reference

Free

ErrorType
ErrorHandler

OperatorFunction
```

---

# Testing

Create parser tests for:

* [ ] Empty program
* [ ] Variable declaration
* [ ] Expression parsing
* [ ] Function parsing
* [ ] Nested blocks
* [ ] Invalid syntax
* [ ] Missing periods
* [ ] Missing braces
* [ ] Invalid types
* [ ] Invalid directives
* [ ] AST output comparison