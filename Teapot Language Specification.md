# Teapot Language Specification     

## End of line
End of line is declared using a period (`.`).
This must be used after every statement, but does not need to be used after closing braces as they already terminate blocks.

## Functions 
#### Declaration
`fc name(type name | type name | etc...)!returnvalue {}`
#### Return a value    
`exit returnvalue.`
Full stop marks end of line.  
#### Function overloading
Function overloading is allowed. This means that this code:
```
fc add(mui8 a)!mui8 {}
fc add(mstr a)!str {}
```
is valid.

Note that the functions must have different parameters to the function of the same name.

You cannot overload when the difference between the two functions is the presence of a default argument.
#### Default arguments
You can set default arguments when declaring a function as so:
```
fc hello(str name = "User") {}
```
This makes the argument optional.
#### Recursion
Recursion is allowed, but the compiler will exit the program if the recursion limit is exceeded.

## Public/private
All objects are private by default - you must make an object public using the `pub` keyword.
For example:
```
pub fc tcp()!void {

}
```

## Datatypes  
  
str -> String (UTF-8 char arrays, text[0] is valid)
char -> Character 
si8/si16/si32/si64 -> Signed 8-bit/16-bit/32-bit/64-bit integer   
ui8/ui16/ui32/ui64 -> Unsigned 8-bit/16-bit/32-bit/64-bit integer   
aint -> Arbitrary precision-based integer   
f32 -> 32-bit float   
f64 -> 64-bit float   
dml -> Decimal   
bln -> Boolean (Values: true, false)   
void -> Function returns nothing  
  
Note: void does not have mutable/constant types. cvoid/mvoid are invalid.  
  
## Arrays

Arrays can only be of the same type, and are of fixed size using contiguous memory. They are created like this:

`val mui8[] ages = [1|2|3].`

## Lists

Lists are dynamic, and are created as below:

`list<datatype>`

## Maps/dictionaries

Example:
```
val map[str]ui8 ages = (
    ["John"|15]
).
```

## Imports
#### Syntax
Example syntax:
`attach filename.`
You can exclude the file extension (.tp) when importing.
All functions from the imported file will be accessible.

You can import specific functions as so:
`attach filename::function.`

And you can import a module with an alias like this:
`attach filename as foo.`

## Memory management
To ensure that you have as much control as possible, Teapot allows you to choose whether you would like to use one of the two memory management models:
- Garbage collection
- Manual memory freeing
#### Garbage collection
To specify that you will be using garbage collection, place this at the very top of the file:
`$MEM-GC`
This means that the compiler will automatically free memory.

#### Manual memory freeing
To specify that you will be using manual memory freeing, place this at the very top of the file:
`$MEM-MANUAL`
This means you will need to free memory using free().
##### free() usage
You can free memory by calling free() on an object as so:
`object::free()`

> [!WARNING]
> You must specify one of the above or the program will not compile.

## References and Pointers
References are declared like this:
```
val mui8 x = 5.
val ref mui8 y = x.
```
References can be mutable. Null references are not allowed, and you can perform arithmetic operations with pointers as you would with variables.

## Tuples

`(10|hello)`

## Call a function  
  
`function(arg|arg2|arg3).`  

## Structs
#### Declaration
```
sct Person {
    str name.
    ui8 age.
}
```
#### Creation
```
val Person p = Person("Bob"|15).
```
#### Access
```
p::name.
```

#### Operators
Structs can define operators like this:
```
operator + (Vector a | Vector b)!Vector {
    exit Vector(a.x+b.x|a.y+b.y).
}
```

## Enums
#### Declaration
```
enm Colour {
    Red.
    Green.
    Blue.
}
```
#### Usage
```
Colour::Red.
```

## Scope

Variables can only be accessed inside of the scope where it is defined.

## Shadowing

Shadowing is allowed. This means that this:
```
val mui8 x = 5.

{
    val mui8 x = 10.
}
```
is valid.

## Initialisation

Variables can be initialised without a value as so:
`val mui8 x.`
This variable will have the value `null`.
`null` will be converted to 0 when the value is changed.

## Constants

Constants are runtime values that do **not** change.

## Error handling
Errors are handled as below:
```
do {
    
} 

fail(FileError e) {

}
```
The `do` branch contains the code to run, and the `fail` branch contains the code to run if there is an error in the `do` branch.

The FileError type is structured like this:
```
err FileError {
    str message.
}
```
## Precedence

Arithmetic operations are calculated in the order they are written. This means:
`5 + 2 * 3`
is calculated as
`(5 + 2) * 3`
If you would like to calculate in a different order, use brackets:
`5 + (2 * 3)`

## Type conversion

`val f32 x = 5`
is valid. `ui8` 5 will be converted to a `f32`.

## Casting

To cast, you use the format:
`variable >> datatype`
For example:
`x >> mui8`
`y >> str`

## Control flow
#### If
Syntax:
```
if (condition) {
    
}
```
#### Else
```
else {

}
```
#### Else if:
```
elif {

}
```
#### While
```
while (condition) {

}
```
#### For
```
for (item : list) {

}
```
## Loop control
#### Break
```
break.
```
#### Continue
```
continue.
```

## Comments  
// Inline comment   
/*   
Multi line comment   
*/  
  
## Variables  
  
Declare a variable with val.   
Each datatype can be mutable (mdatatype) or constant (cdatatype).  
  
Example:  
  
val cstr name = "Teapot".  
  
## Encoding  
  
Teapot uses UTF-8 encoding.  
  
## Entry point  
  
The program starts at fc main()!void {}.  
  
## Naming  
  
Names cannot match any of the following cases:  
- Starts with a number  
- Has a non-alphanumeric character other than _ or - in it  
- Starts with any non-alphabetic character  
- Exactly matches a reserved word (see next section)  
  
Names are case-sensitive.  
  
## Reserved words

These are keywords that are used by the language. They cannot be used as identifiers outside of strings.

Following is the exhaustive list of reserved words:

#### Modules and visibility
- `attach`: Imports a module
- `as`: Creates an alias for an imported module
- `pub`: Makes an object public

#### Functions
- `fc`: Declares a function
- `exit`: Returns a value from a function
- `operator`: Declares a custom operator overload

#### Variables and memory
- `val`: Declares a variable
- `ref`: Declares a reference
- `free`: Frees memory when using manual memory management
- `null`: Represents no value

#### Control flow
- `if`: Conditional statement
- `elif`: Else-if conditional branch
- `else`: Else conditional branch
- `while`: While loop
- `for`: For loop
- `break`: Exits the current loop
- `continue`: Skips to the next loop iteration

#### Error handling
- `do`: Starts the error-handling block
- `fail`: Defines the error-handling branch
- `err`: Declares an error type

#### Data structures
- `sct`: Declares a struct
- `enm`: Declares an enum
- `list`: Declares a dynamic list
- `map`: Declares a map/dictionary

#### Primitive data types
- `void`: Function returns no value
- `str`: UTF-8 string
- `char`: Character
- `bln`: Boolean
- `aint`: Arbitrary precision integer
- `dml`: Decimal floating-point number
- `f32`: 32-bit floating-point number
- `f64`: 64-bit floating-point number

#### Signed integer types
- `si8`: Signed 8-bit integer
- `si16`: Signed 16-bit integer
- `si32`: Signed 32-bit integer
- `si64`: Signed 64-bit integer

#### Unsigned integer types
- `ui8`: Unsigned 8-bit integer
- `ui16`: Unsigned 16-bit integer
- `ui32`: Unsigned 32-bit integer
- `ui64`: Unsigned 64-bit integer

#### Mutable and constant types

The following prefixes are reserved:

- `m`: Mutable type
- `c`: Constant type

Examples:

##### Mutable types
- `mstr`: Mutable string
- `mbln`: Mutable boolean
- `msi8`: Mutable signed 8-bit integer
- `msi16`: Mutable signed 16-bit integer
- `msi32`: Mutable signed 32-bit integer
- `msi64`: Mutable signed 64-bit integer
- `mui8`: Mutable unsigned 8-bit integer
- `mui16`: Mutable unsigned 16-bit integer
- `mui32`: Mutable unsigned 32-bit integer
- `mui64`: Mutable unsigned 64-bit integer
- `maint`: Mutable arbitrary precision integer
- `mf32`: Mutable 32-bit float
- `mf64`: Mutable 64-bit float
- `mdml`: Mutable decimal

##### Constant types
- `cstr`: Constant string
- `cbln`: Constant boolean
- `csi8`: Constant signed 8-bit integer
- `csi16`: Constant signed 16-bit integer
- `csi32`: Constant signed 32-bit integer
- `csi64`: Constant signed 64-bit integer
- `cui8`: Constant unsigned 8-bit integer
- `cui16`: Constant unsigned 16-bit integer
- `cui32`: Constant unsigned 32-bit integer
- `cui64`: Constant unsigned 64-bit integer
- `caint`: Constant arbitrary precision integer
- `cf32`: Constant 32-bit float
- `cf64`: Constant 64-bit float
- `cdml`: Constant decimal

#### Boolean literals
- `true`: Boolean true value
- `false`: Boolean false value
  
## Operators  
  
Following is an exhaustive list of all the operators.  
  
### Arithmetic  
- +: addition  
- -: subtraction  
- *: multiplication  
- /: division  
- %: modulus  
- **: exponentiation  
### Comparison  
- ==: is equal to  
- \>: is greater than  
- <: is less than  
- \>=: is greater than or equal to  
- <=: is less than or equal to  
- ~=: is not equal to  
### Logical  
- &&: and  
- ||: or  
- ~: not  
### Assignment  
- =: set the variable to the value specified  
- +=: set the variable to its current value added to the value specified  
- -=: set the variable to its current value subtracted from the value specified  
- *=: set the variable to its current value multiplied by the value specified  
- /=: set the variable to its current value divided by the value specified  
  
## Comments  
- //: inline comment  
- /*: start multi-line comment  
- */: end multi-line comment  
  
Comment declarations inside of comments or strings will be ignored.  
  
## Whitespaces  
Keywords must be separated with whitespaces, while operators do not. Any whitespaces outside of this case will be ignored.