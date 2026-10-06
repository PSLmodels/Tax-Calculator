# Tax-Calculator Decorators

Documentation of the `taxcalc.decorators` module.

## id_wrapper

```python
def id_wrapper(*dec_args, **dec_kwargs)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/decorators.py#L33)

```text
Function wrapper when numba package is not being used during debugging.
```

## jit_cache_root

```python
def jit_cache_root()
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/decorators.py#L60)

```text
Return path of folder that holds the on-disk cache of JIT-compiled
functions, which is the TAXCALC_JIT_CACHE_DIR environment variable
value if set, otherwise the taxcalc subfolder of the NUMBA_CACHE_DIR
folder if set, otherwise the taxcalc folder in the user's cache folder.
```

## source_hash

```python
def source_hash()
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/decorators.py#L76)

```text
Return hash of the calcfunctions.py and decorators.py source code
and of the Python, NumPy, and Numba versions, all of which affect the
JIT-compiled code.  Any change in these produces a new hash value.
```

## prune_jit_cache

```python
def prune_jit_cache(root, current)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/decorators.py#L92)

```text
Mark the current cache folder in the root folder as used now, and
delete the other cache folders in the root folder that have not
been used for more than JIT_CACHE_MAX_AGE_DAYS days.  Only folders
whose names look like a source_hash() value are ever deleted.
```

## jit_cache_class

```python
def jit_cache_class()
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/decorators.py#L115)

```text
Return the Numba cache class that stores the compiled code in the
jit_cache_root()/source_hash() folder, or None if that folder is not
writable or if Numba does not provide the internal classes needed to
construct the cache class.
```

## enable_jit_cache

```python
def enable_jit_cache(dispatcher, tag)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/decorators.py#L181)

```text
Turn on on-disk caching of the specified Numba dispatcher's compiled
code, where tag uniquely identifies the dispatcher's function.  If
the cache folder is not writable, the dispatcher is left uncached.
```

## cached_jit

```python
def cached_jit(cache_tag=None, **kwargs)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/decorators.py#L198)

```text
Return a decorator that JIT-compiles a function using numba.jit with
the specified kwargs and caches the compiled code on disk if the
function is defined in the CACHED_MODULE or if cache_tag is not None.
```

## GetReturnNode

```python
class GetReturnNode()
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/decorators.py#L224)

```text
A NodeVisitor to get the return tuple names from a calc-style function.
```

### GetReturnNode.visit_Return

```python
def visit_Return(self, node)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/decorators.py#L228)

```text
visit_Return is used by NodeVisitor.visit method.
```

## create_apply_function_string

```python
def create_apply_function_string(sigout, sigin, parameters)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/decorators.py#L237)

```text
Create a string for a function of the form::

   def ap_fuc(x_0, x_1, x_2, ...):
       for i in range(len(x_0)):
           x_0[i], ... = jitted_f(x_j[i], ...)
       return x_0[i], ...

where the specific args to jitted_f and the number of
values to return is determined by sigout and sigin.

Parameters
----------
sigout: iterable of the out arguments

sigin: iterable of the in arguments

parameters: iterable of which of the args (from in_args) are parameter
            variables (as opposed to column records). This influences
            how we construct the apply-style function

Returns
-------
a String representing the function
```

## create_toplevel_function_string

```python
def create_toplevel_function_string(args_out, args_in, pm_or_pf)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/decorators.py#L281)

```text
Create a string for a function of the form:

    def hl_func(x_0, x_1, x_2, ...):
        outputs = (...) = calc_func(...)
        header = [...]
        return DataFrame(data, columns=header)

Parameters
----------
args_out: iterable of the out arguments

args_in: iterable of the in arguments

pm_or_pf: iterable of strings for object that holds each arg

Returns
-------
a String representing the function
```

## make_apply_function

```python
def make_apply_function(func, out_args, in_args, parameters, do_jit=DO_JIT, **kwargs)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/decorators.py#L340)

```text
Takes a calc-style function and creates the necessary Python code for
an apply-style function. Will also jit the function if desired.

Parameters
----------
func: the calc-style function

out_args: list of out arguments for the apply-style function

in_args: list of in arguments for the apply-style function

parameters: iterable of which of the args (from in_args) are parameter
            variables (as opposed to column records).  This influences
            how we construct the apply-style function.

do_jit: Bool, if True, jit the resulting apply-style function

Returns
-------
apply-style function
```

## apply_jit

```python
def apply_jit(dtype_sig_out, dtype_sig_in, parameters=None, **kwargs)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/decorators.py#L383)

```text
Make a decorator that takes in a calc-style function, handle apply step.
```

## iterate_jit

```python
def iterate_jit(parameters=None, **kwargs)
```

[source](https://github.com/PSLmodels/Tax-Calculator/blob/master/taxcalc/decorators.py#L422)

```text
Public decorator for a calc-style function (see calcfunctions.py) that
transforms the calc-style function into an apply-style function that
can be called by Calculator class methods (see calculator.py).
```
