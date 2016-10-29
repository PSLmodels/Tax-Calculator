import collections
import six


def cast_to_iterable(value):
    if isinstance(value, collections.Iterable) and \
            not isinstance(value, six.string_types):
        return value
    else:
        return [value]


def trace_map_func(inputs, outputs):
    """
    A decorator to write input and output keys as metadata on a function
    """

    # Turn args into collections if they're not already
    inputs = cast_to_iterable(inputs)
    outputs = cast_to_iterable(outputs)

    # If args aren't hashable, we'll get an error when parsing in a TracedMap.
    # Raise it here instead to simplify debugging.
    for arg in [inputs, outputs]:
        for io_key in arg:
            if not isinstance(io_key, collections.Hashable):
                raise TypeError('hashable input/output keys required, got {}'
                                .format(io_key))

    # Save our metadata on the function itself
    def decorator(func):
        func.trace_map_inputs = inputs
        func.trace_map_outputs = outputs
        return func

    return decorator


class TracedMap(object):
    """
    Maps an input dict to an output dict in a single direction.
    Exposes traces between input and output.

    Can use _dict for 1-1 mappings.
    Can also use funcs annotated with @annotate_trace_map for many-many.

    Maps with arbitrary depth can be accomplished by serializing your keys.
    Caches on construction, so should be relatively safe to pass around.
    """

    def __init__(self, _dict=None, funcs=None, formatter=None):
        """
        Creates the map and prepares its trace cache.
        """
        self._dict = _dict.copy() if _dict else {}
        self._formatter = formatter
        self._funcs = tuple(funcs) if funcs else ()

        self._dict_i_keys = set()
        self._dict_o_keys = set()
        self._dict_i_keys_by_o_key = {}
        self._dict_o_keys_by_i_key = {}

        for i_key, o_key in self._dict.items():
            self._dict_i_keys.add(i_key)
            self._dict_o_keys.add(o_key)
            self._dict_i_keys_by_o_key[o_key] = {i_key}
            self._dict_o_keys_by_i_key[i_key] = {o_key}

        self._funcs_i_keys = set()
        self._funcs_o_keys = set()
        self._funcs_o_keys_by_i_key = {}
        self._funcs_i_keys_by_o_key = {}

        for func in self._funcs:
            inputs = func.trace_map_inputs
            outputs = func.trace_map_outputs

            self._funcs_i_keys.update(inputs)
            self._funcs_o_keys.update(outputs)

            for i_key in inputs:
                if i_key not in self._funcs_o_keys_by_i_key:
                    self._funcs_o_keys_by_i_key[i_key] = set()
                self._funcs_o_keys_by_i_key[i_key].update(outputs)

            for o_key in outputs:
                if o_key not in self._funcs_i_keys_by_o_key:
                    self._funcs_i_keys_by_o_key[o_key] = set()
                self._funcs_i_keys_by_o_key[o_key].update(inputs)

    def input_keys(self):
        """
        Returns a set of all possible input keys.
        """
        return self._dict_i_keys | self._funcs_i_keys

    def input_keys_of(self, output_key):
        """
        Returns a set of all input keys derivable from output_key
        """
        return self._dict_i_keys_by_o_key.get(output_key, set()) \
            | self._funcs_i_keys_by_o_key.get(output_key, set())

    def output_keys(self):
        """
        Returns a set of all possible output keys.
        """
        return self._dict_o_keys | self._funcs_o_keys

    def output_keys_of(self, input_key):
        """
        Returns a set of all output keys derivable from input_key
        """
        return self._dict_o_keys_by_i_key.get(input_key, set()) \
            | self._funcs_o_keys_by_i_key.get(input_key, set())

    def map(self, _input):
        """
        Perform the map procedures on _input and return the output data.
        """
        result = self._map_with_dict(_input)
        result.update(self._map_with_funcs(_input))
        return result

    def _map_with_dict(self, _input):
        """
        Perform the dict map on _input and return output.
        """
        return {
            self._dict[key]: self._format(key, value)
            for key, value in _input.items()
            if key in self._dict
        }

    def _map_with_funcs(self, _input):
        """
        Perform funcs on _input and return output.
        """
        output = {}
        for func in self._funcs:
            # funcs can return None
            result = func(_input)
            if result:
                output.update(result)

        if self._formatter:
            for key in list(output.keys()):
                output[key] = self._format(key, output[key])

        return output

    def _format(self, output_key, value):
        """
        Format the output values according to their key if formatter provided.
        """
        return self._formatter(output_key, value) if self._formatter else value
