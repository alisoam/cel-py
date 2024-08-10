# CEL-PY

A very simple module to quickly evaluate [CEL](https://github.com/google/cel-spec) expressions in Python.
CEL expressions converted to python code and evaluated using Python's `exec` function.
Parsing copied from [cel-python](https://github.com/cloud-custodian/cel-python).

## Instalation
 pip install 

## example
``` python
import cel

text = """ arg1.a == 1"""
program = cel.Compiler.compile(text)
result = program.eval(args={"arg1": {"a": 1, "b": 2, "c": 3}})
```
