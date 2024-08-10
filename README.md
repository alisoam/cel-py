# CEL-PY

A very simple and fast implementation of the CEL language in Python.

## Instalation
 pip install 

## example
``` python
text = """ arg1.a == 1"""
program = cel.Compiler.compile(text)
result = program.eval(args={"arg1": {"a": 1, "b": 2, "c": 3}})
```
