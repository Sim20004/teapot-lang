# Teapot Language Specification

## Table of Contents
1. [Overview](#overview)
2. [Naming Rules](#naming-rules)
3. [Reserved Words](#reserved-words)
4. [Data Types](#data-types)
5. [Variables & Constants](#variables--constants)
6. [Operators](#operators)
7. [Comments](#comments)
8. [Control Flow](#control-flow)
9. [Loop Control](#loop-control)
10. [Functions](#functions)
11. [Public / Private Visibility](#public--private-visibility)
12. [Data Structures](#data-structures)
13. [References & Pointers](#references--pointers)
14. [Memory Management](#memory-management)
15. [Error Handling](#error-handling)
16. [Type Conversion & Casting](#type-conversion--casting)
17. [Operator Precedence](#operator-precedence)
18. [Modules & Imports](#modules--imports)

---

## Overview

- **Encoding:** Teapot uses UTF-8 encoding.
- **Entry point:** The program starts at `fc main()!void {}`.
- **End of line:** A statement is terminated with a period (`.`). This is required after every statement, but is *not* needed after a closing brace, since braces already terminate blocks.
- **Whitespace:** Keywords must be separated by whitespace. Operators do not require whitespace around them. Any whitespace outside of these cases is ignored.
- **Scope:** Variables can only be accessed inside the scope in which they are defined.
- **Shadowing:** Shadowing is allowed — a variable in an inner scope may reuse the name of one in an outer scope:
  ```
  val mui8 x = 5.

  {
      val mui8 x = 10.
  }
  ```

---

## Naming Rules

An identifier is **invalid** if it:
- Starts with a number
- Contains a non-alphanumeric character other than `_` or `-`
- Starts with any non-alphabetic character
- Exactly matches a reserved word

Names are **case-sensitive**.

---

## Reserved Words

The following is the exhaustive list of keywords. They cannot be used as identifiers outside of strings.

**Modules and visibility**
- `attach` — imports a module
- `as` — creates an alias for an imported module
- `pub` — makes an object public

**Functions**
- `fc` — declares a function
- `exit` — returns a value from a function
- `operator` — declares a custom operator overload

**Variables and memory**
- `val` — declares a variable
- `ref` — declares a reference
- `free` — frees memory when using manual memory management
- `null` — represents no value

**Control flow**
- `if` — conditional statement
- `elif` — else-if conditional branch
- `else` — else conditional branch
- `while` — while loop
- `for` — for loop
- `break` — exits the current loop
- `continue` — skips to the next loop iteration

**Error handling**
- `do` — starts the error-handling block
- `fail` — defines the error-handling branch
- `err` — declares an error type

**Data structures**
- `sct` — declares a struct
- `enm` — declares an enum
- `list` — declares a dynamic list
- `map` — declares a map/dictionary

**Primitive data types**
- `void`, `str`, `char`, `bln`, `aint`, `dml`, `f32`, `f64`

**Signed integer types**
- `si8`, `si16`, `si32`, `si64`

**Unsigned integer types**
- `ui8`, `ui16`, `ui32`, `ui64`

**Mutable / constant prefixes**
- `m` — mutable type prefix
- `c` — constant type prefix

**Boolean literals**
- `true`, `false`

---

## Data Types

| Type | Description |
|---|---|
| `str` | String (UTF-8 char array; `text[0]` is valid) |
| `char` | Character |
| `si8`/`si16`/`si32`/`si64` | Signed 8/16/32/64-bit integer |
| `ui8`/`ui16`/`ui32`/`ui64` | Unsigned 8/16/32/64-bit integer |
| `aint` | Arbitrary precision integer |
| `f32` | 32-bit float |
| `f64` | 64-bit float |
| `dml` | Decimal |
| `bln` | Boolean (`true`, `false`) |
| `void` | Function returns nothing |

> **Note:** `void` has no mutable/constant variants — `cvoid`/`mvoid` are invalid.

### Mutable & Constant Prefixes

Every data type (except `void`) can be prefixed to indicate mutability:

- **Mutable types:** `mstr`, `mbln`, `msi8`, `msi16`, `msi32`, `msi64`, `mui8`, `mui16`, `mui32`, `mui64`, `maint`, `mf32`, `mf64`, `mdml`
- **Constant types:** `cstr`, `cbln`, `csi8`, `csi16`, `csi32`, `csi64`, `cui8`, `cui16`, `cui32`, `cui64`, `caint`, `cf32`, `cf64`, `cdml`

Constants are runtime values that do **not** change.

---

## Variables & Constants

Declare a variable with `val`, giving it a mutable (`m...`) or constant (`c...`) type:

```
val cstr name = "Teapot".
```

### Initialisation
A variable can be declared without a value:
```
val mui8 x.
```
This gives the variable the value `null`. `null` is converted to `0` when the value is subsequently changed.

### Type Conversion
Values are automatically converted to a compatible target type:
```
val f32 x = 5
```
This is valid — the `ui8` literal `5` is converted to `f32`.

---

## Operators

### Arithmetic
| Operator | Meaning |
|---|---|
| `+` | Addition |
| `-` | Subtraction |
| `*` | Multiplication |
| `/` | Division |
| `%` | Modulus |
| `**` | Exponentiation |

### Comparison
| Operator | Meaning |
|---|---|
| `==` | Equal to |
| `>` | Greater than |
| `<` | Less than |
| `>=` | Greater than or equal to |
| `<=` | Less than or equal to |
| `~=` | Not equal to |

### Logical
| Operator | Meaning |
|---|---|
| `&&` | And |
| `\|\|` | Or |
| `~` | Not |

### Assignment
| Operator | Meaning |
|---|---|
| `=` | Set variable to value |
| `+=` | Add value to variable |
| `-=` | Subtract value from variable |
| `*=` | Multiply variable by value |
| `/=` | Divide variable by value |

### Custom Operators
Structs can define their own operator overloads:
```
operator + (Vector a, Vector b)!Vector {
    exit Vector(a.x+b.x, a.y+b.y).
}
```

---

## Comments

```
// Inline comment

/*
Multi-line comment
*/
```
Comment syntax appearing inside a comment or a string is ignored.

---

## Control Flow

### If / Else If / Else
```
if (condition) {

}
elif (condition) {

}
else {

}
```

### While
```
while (condition) {

}
```

### For
```
for (item : list) {

}
```

---

## Loop Control

```
break.
continue.
```

---

## Functions

### Declaration
```
fc name(type name, type name, etc...)!returnvalue {}
```

### Returning a Value
```
exit returnvalue.
```

### Entry Point
```
fc main()!void {}
```

### Function Overloading
Functions may share a name if their parameter lists differ:
```
fc add(mui8 a)!mui8 {}
fc add(mstr a)!str {}
```
Overloading is **not** permitted where the only difference between two functions is the presence of a default argument.

### Default Arguments
```
fc hello(str name = "User") {}
```
This makes `name` optional.

### Recursion
Recursion is allowed. If the recursion limit is exceeded, the compiler will exit the program.

---

## Public / Private Visibility

All objects are **private** by default. Use `pub` to expose an object:
```
pub fc tcp()!void {

}
```

---

## Data Structures

### Arrays
Fixed-size, contiguous, single-type:
```
val mui8[] ages = [1, 2, 3].
```

### Lists
Dynamic and resizable:
```
list<datatype>
```

### Maps / Dictionaries
```
val map[str]ui8 ages = (
    ["John", 15]
).
```

### Tuples
```
(10, hello)
```

### Structs

**Declaration:**
```
sct Person {
    str name.
    ui8 age.
}
```

**Creation:**
```
val Person p = Person("Bob", 15).
```

**Field access:**
```
p::name.
```

### Enums

**Declaration:**
```
enm Colour {
    Red.
    Green.
    Blue.
}
```

**Usage:**
```
Colour::Red.
```

### Calling a Function
```
function(arg, arg2, arg3).
```

---

## References & Pointers

```
val mui8 x = 5.
val ref mui8 y = x.
```
References can be mutable. Null references are **not** allowed. Pointer arithmetic works the same as with ordinary variables.

---

## Memory Management

Teapot supports two memory management models, chosen per file. **One of the two directives below must appear at the very top of the file, or the program will not compile.**

### Garbage Collection
```
$MEM-GC
```
The compiler automatically frees memory.

### Manual Memory Freeing
```
$MEM-MANUAL
```
You must free memory yourself using `free()`:
```
object::free()
```

---

## Error Handling

```
do {

}

fail(FileError e) {

}
```
The `do` branch runs the main code; the `fail` branch runs if an error occurs in the `do` branch.

Error types are declared with `err`:
```
err FileError {
    str message.
}
```

---

## Type Conversion & Casting

**Automatic conversion** (see also [Variables & Constants](#variables--constants)):
```
val f32 x = 5
```

**Explicit casting** uses `>>`:
```
x >> mui8
y >> str
```

---

## Operator Precedence

Arithmetic operations are evaluated strictly in the order written (left to right), **not** by standard mathematical precedence:
```
5 + 2 * 3
```
is calculated as
```
(5 + 2) * 3
```
Use brackets to force a different order:
```
5 + (2 * 3)
```

---

## Modules & Imports

**Basic import** (file extension `.tp` may be omitted):
```
attach filename.
```

**Import specific function:**
```
attach filename::function.
```

**Import with alias:**
```
attach filename as foo.
```

All functions from an imported file are accessible after import.