# MWOT Wonders

Herein lie works of esoteric programming specific to MWOT.


## The Polyglot

[`polyglot.mwot`](polyglot.mwot) is the source for both
[`polyglot.b`](polyglot.b) and [`polyglot.sh`](polyglot.sh).
All three files contain the exact same information: two programs, both
of which print the message "Hello World!" when executed, one using
brainfuck; the other, POSIX shell.
Each file can be transpiled byte-for-byte from either of the others
using `mwot`.


## The Quine

[`quine.mwot.b`](quine.mwot.b) can be decompiled with
`mwot -db -D basic --vocab "AA A" --width none` or simply run with
`mwot -xb` to generate
[a self-printing brainfuck MWOT program](quine.mwot).
