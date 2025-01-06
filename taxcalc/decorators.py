"""
Implement numba JIT decorators used to speed-up the execution
of Tax-Calculator functions in the calcfunctions.py module.
"""
# CODING-STYLE CHECKS:
# pycodestyle decorators.py
# pylint --disable=locally-disabled decorators.py

import os
import io
import ast
import inspect
import numba
from taxcalc.policy import Policy


DO_JIT = True
# One way to use the Python debugger is to do these two things:
#  (a) change the line immediately above this comment from
#      "DO_JIT = True" to "DO_JIT = False", and
#  (b) import pdb package and call pdb.set_trace() in either the
#      calculator.py or calcfunctions.py file.


def id_wrapper(*dec_args, **dec_kwargs):  # pylint: disable=unused-argument
    """
    Function wrapper when numba package is not being used during debugging.
    """
    def wrap(fnc):
        """
        wrap function nested in id_wrapper function.
        """
        def wrapped_f(*args, **kwargs):
            """
            wrapped_f function nested in wrap function.
            """
            return fnc(*args, **kwargs)
        return wrapped_f
    return wrap


if DO_JIT is False or 'NOTAXCALCJIT' in os.environ:
    JIT = id_wrapper
else:
    JIT = numba.jit


class GetReturnNode(ast.NodeVisitor):
    """
    A NodeVisitor to get the return tuple names from a calc-style function.
    """
    def visit_Return(self, node):  # pylint: disable=invalid-name
        """
        visit_Return is used by NodeVisitor.visit method.
        """
        if isinstance(node.value, ast.Tuple):
            return [e.id for e in node.value.elts]
        return [node.value.id]


def create_apply_function_string(sigout, sigin, parameters):
    """
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
    """
    fstr = io.StringIO()
    total_len = len(sigout) + len(sigin)
    out_args = ["x_" + str(i) for i in range(0, len(sigout))]
    in_args = ["x_" + str(i) for i in range(len(sigout), total_len)]

    fstr.write(f"def ap_func({','.join(out_args + in_args)}):\n")
    fstr.write("  for i in range(len(x_0)):\n")
    out_index = [x + "[i]" for x in out_args]
    in_index = []
    for arg, _var in zip(in_args, sigin):
        in_index.append(arg + "[i]" if _var not in parameters else arg)
    fstr.write("    " + ",".join(out_index) + " = ")
    fstr.write("jitted_f(" + ",".join(in_index) + ")\n")
    fstr.write("  return " + ",".join(out_args) + "\n")
    return fstr.getvalue()


def create_toplevel_function_string(args_out, args_in, pm_or_pf):
    """
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
    """
    fstr = io.StringIO()
    fstr.write("def hl_func(pm, pf")
    fstr.write("):\n")
    fstr.write("    from pandas import DataFrame\n")
    fstr.write("    import numpy as np\n")
    fstr.write("    import pandas as pd\n")
    fstr.write("    def get_values(x):\n")
    fstr.write("        if isinstance(x, pd.Series):\n")
    fstr.write("            return x.values\n")
    fstr.write("        else:\n")
    fstr.write("            return x\n")
    fstr.write("    outputs = \\\n")

    outs = []
    for ppp, attr in zip(pm_or_pf, args_out + args_in):
        outs.append(ppp + "." + attr + ", ")
    outs = [m_or_f + "." + arg for m_or_f, arg in zip(pm_or_pf, args_out)]
    fstr.write("        (" + ", ".join(outs) + ") = \\\n")
    fstr.write("        " + "applied_f(")
    for ppp, attr in zip(pm_or_pf, args_out + args_in):
        # Bring Policy parameter values down a dimension.
        if ppp == "pm":
            attr += "[0]"
        fstr.write("get_values(" + ppp + "." + attr + ")" + ", ")
    fstr.write(")\n")
    fstr.write("    header = [")
    col_headers = ["'" + out + "'" for out in args_out]
    fstr.write(", ".join(col_headers))
    fstr.write("]\n")
    if len(args_out) == 1:
        fstr.write("    return DataFrame(data=outputs,"
                   "columns=header)")
    else:
        fstr.write("    return DataFrame(data=np.column_stack("
                   "outputs),columns=header)")
    return fstr.getvalue()


def make_apply_function(func, out_args, in_args, parameters,
                        do_jit=DO_JIT, **kwargs):
    """
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
    """
    if do_jit:
        jitted_f = JIT(**kwargs)(func)
    else:
        jitted_f = func
    apfunc = create_apply_function_string(out_args, in_args, parameters)
    func_code = compile(apfunc, "<string>", "exec")
    fakeglobals = {}
    eval(func_code,  # pylint: disable=eval-used
         {"jitted_f": jitted_f}, fakeglobals)
    if do_jit:
        return JIT(**kwargs)(fakeglobals['ap_func'])
    return fakeglobals['ap_func']


def apply_jit(dtype_sig_out, dtype_sig_in, parameters=None, **kwargs):
    """
    Make a decorator that takes in a calc-style function, handle apply step.
    """
    if not parameters:
        parameters = []

    def make_wrapper(func):
        """
        make_wrapper function nested in apply_jit function.
        """
        theargs = inspect.getfullargspec(func).args
        jitted_apply = make_apply_function(func, dtype_sig_out,
                                           dtype_sig_in, parameters, **kwargs)

        def wrapper(*args):
            """
            wrapper function nested in make_wrapper function.
            """
            in_arrays = []
            out_arrays = []
            for farg in theargs:
                if hasattr(args[0], farg):
                    in_arrays.append(getattr(args[0], farg))
                else:
                    in_arrays.append(getattr(args[1], farg))
            for farg in dtype_sig_out:
                if hasattr(args[0], farg):
                    out_arrays.append(getattr(args[0], farg))
                else:
                    out_arrays.append(getattr(args[1], farg))
            final_array = out_arrays + in_arrays
            ans = jitted_apply(*final_array)
            return ans

        return wrapper
    return make_wrapper


def iterate_jit(parameters=None, **kwargs):
    """
    Public decorator for a calc-style function (see calcfunctions.py) that
    transforms the calc-style function into an apply-style function that
    can be called by Calculator class methods (see calculator.py).
    """

    if not parameters:
        parameters = []

    def make_wrapper(func):
        """
        make_wrapper function nested in iterate_jit decorator
        wraps specified func using apply_jit.
        """
        # pylint: disable=too-many-locals
        # Get the input arguments from the function
        in_args = inspect.getfullargspec(func).args
        # Get the numba.jit arguments
        jit_args_list = inspect.getfullargspec(JIT).args + ['nopython']
        kwargs_for_jit = {}
        for key, val in kwargs.items():
            if key in jit_args_list:
                kwargs_for_jit[key] = val

        # Any name that is a parameter
        # Boolean flag is given special treatment.
        # Identify those names here
        param_list = Policy.parameter_list()
        allowed_parameters = param_list
        allowed_parameters += list(arg[1:] for arg in param_list)
        additional_parameters = [arg for arg in in_args if
                                 arg in allowed_parameters]
        additional_parameters += parameters
        # Remote duplicates
        all_parameters = list(set(additional_parameters))

        src = inspect.getsourcelines(func)[0]

        # Discover the return arguments by walking
        # the AST of the function
        grn = GetReturnNode()
        all_out_args = None
        for node in ast.walk(ast.parse(''.join(src))):
            all_out_args = grn.visit(node)
            if all_out_args:
                break
        if not all_out_args:
            raise ValueError("Can't find return statement in function!")

        # Now create the apply-style possibly-jitted function
        applied_jitted_f = make_apply_function(func,
                                               list(reversed(all_out_args)),
                                               in_args,
                                               parameters=all_parameters,
                                               do_jit=DO_JIT,
                                               **kwargs_for_jit)

        def wrapper(*args, **kwargs):
            """
            wrapper function nested in make_wrapper function nested
            in iterate_jit decorator.
            """
            # os TESTING environment only accepts string arguments
            if os.getenv('TESTING') == 'True':
                return func(*args, **kwargs)

            in_arrays = []
            pm_or_pf = []
            for farg in all_out_args + in_args:
                if hasattr(args[0], farg):
                    in_arrays.append(getattr(args[0], farg))
                    pm_or_pf.append("pm")
                elif hasattr(args[1], farg):
                    in_arrays.append(getattr(args[1], farg))
                    pm_or_pf.append("pf")
            # Create the high level function
            high_level_func = create_toplevel_function_string(all_out_args,
                                                              list(in_args),
                                                              pm_or_pf)
            func_code = compile(high_level_func, "<string>", "exec")
            fakeglobals = {}
            eval(func_code,  # pylint: disable=eval-used
                 {"applied_f": applied_jitted_f}, fakeglobals)
            high_level_fn = fakeglobals['hl_func']
            ans = high_level_fn(*args, **kwargs)
            return ans

        return wrapper

    return make_wrapper
