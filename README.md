# MWOT, an esolang


## The MWOT Language

MWOT is an esoteric language for writing individual bits as readable
text.
Or text that is entirely unreadable.
The only requirement is that each word have a number of letters equal to
the bit it represents, modulo 2.
The full rules of the language are:

- Words are separated by whitespace.
- A word with an odd number of letters (not including digits or
  punctuation) generates a 1.
- A word with an even number of letters generates a 0.
- A word with no letters is ignored.
- A shebang (a sequence at the very start of a file starting with "#!"
  and ending with a newline) is ignored.

MWOT's design allows perfectly valid data to be written as a poem, a
story, a manifesto, or a lot of nonsense.
Its broad definition of "letter" allows it to work with any written
language.
And its ability to conceal data in plain text gives it excellent
steganographic potential.

Because raw bits aren't very useful, MWOT compiles to two formats:
brainfuck and binary.

### Brainfuck MWOT

A true esoteric programming language.
Every three bits encode a brainfuck instruction.

| MWOT                    | bits | brainfuck |
| :---------------------- | :--- | :-------: |
| An Indirect Kiss        | 000  |    `>`    |
| Drop Beat Dad           | 001  |    `<`    |
| Greg the Babysitter     | 010  |    `+`    |
| On the Run              | 011  |    `-`    |
| Super Watermelon Island | 100  |    `.`    |
| Beach City Drift        | 101  |    `,`    |
| Story for Steven        | 110  |    `[`    |
| Catch and Release       | 111  |    `]`    |

### Binary MWOT

Bits are grouped into bytes.
Think of it like a really inefficient base64.

| MWOT                               | bits     | byte   |
| :--------------------------------- | :------- | :----: |
| I can show you how to be strong /  | 11011000 | `\xd8` |
| In the real way / And I know that  | 01011100 |  `\\`  |
| we can be strong / In the real way | 01000101 |  `E`   |

### Etymology

"MWOT" stands for Massive Wall Of Text, something that is unavoidable
when rendering even small amounts of data in this format.

Or maybe it stands for Massive Waste Of Time.
Do you know how long it takes to *write* a massive wall of text that
compiles to exactly what you wanted it to?


## The `mwot` Program

`mwot` can compile or decompile MWOT.
It also comes with a brainfuck interpreter built in.

Its options include:

- Free choice to take source code (also, interpreter input) from
  standard input, a file, or a string
- Shebang and executable permission control
- Multiple decompilers to try
- Full control of the brainfuck interpreter's implementation details

### Usage examples

```sh
# Compile `hello.mwot` as brainfuck
mwot -cb hello.mwot -o hello.b

# Decompile `goodbye.txt` as binary data
mwot -dy goodbye.txt -o goodbye.txt.mwot

# Execute brainfuck
mwot -xb hello.b

# Compile `hello.mwot` to an executable brainfuck script
mwot -cbSX hello.mwot -o hello

# Generate a very literal `hello.mwot`, using standard I/O
mwot -db -D basic --vocab 'zero one' < hello.b > hello-literal.mwot

# Execute brainfuck with strict settings and no input
mwot -xb --eof=-1 --wraparound false --no-shebang-in --input '' hello.b

# Execute brainfuck MWOT without compiling to a file
mwot -ib hello.mwot
```
