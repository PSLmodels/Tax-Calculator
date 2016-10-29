import pytest
from taxcalc.filings.util import TracedMap, trace_map_func


def test_trace_map_func():
    # It raises a value error when used with args that aren't hashable
    not_hashable_objects = [[1, 2, 3], {4: {}}, {1, 2}, TracedMap]

    with pytest.raises(TypeError):
        @trace_map_func(not_hashable_objects, '1')
        def foo(x):
            return x

    # It decorates a function and writes input and output metadata
    hashable_objects_1 = (1, 1., 'abc', (1, 2))
    hashable_objects_2 = (frozenset(), ValueError, False)

    @trace_map_func(hashable_objects_1, hashable_objects_2)
    def foo(x):
        return x

    assert foo.trace_map_inputs == hashable_objects_1
    assert foo.trace_map_outputs == hashable_objects_2


def test_traced_map():
    # It can be created and used without any maps
    subject = TracedMap()
    assert subject.input_keys() == set()
    assert subject.input_keys_of('1') == set()
    assert subject.output_keys() == set()
    assert subject.output_keys_of(47) == set()
    assert subject.map({1: 'a'}) == {}

    # It can map using a dict
    map_dict = {1: '1', 2: TypeError, 3: (3, 3)}
    subject = TracedMap(_dict=map_dict)
    assert subject.input_keys() == {1, 2, 3}
    assert subject.output_keys() == {'1', TypeError, (3, 3)}
    assert subject.output_keys_of(2) == {TypeError}
    assert subject.input_keys_of((3, 3)) == {3}
    assert subject.map({1: 1, 2: 2, 3: 3}) == {'1': 1, TypeError: 2, (3, 3): 3}

    # It errors when dict values aren't hashable.
    with pytest.raises(TypeError):
        TracedMap(_dict={1: [1, 2]})

    # It can map using functions
    @trace_map_func((1, 2, 3), 'a')
    def map_func_1(x):
        return {'a': x.get(1) + x.get(1) + x.get(1)}

    @trace_map_func(1, ('a', 'b'))
    def map_func_2(x):
        return {'a': x.get(1), 'b': x.get(1) * 47}

    subject = TracedMap(funcs=[map_func_1, map_func_2])
    assert subject.input_keys() == {1, 2, 3}
    assert subject.output_keys() == {'a', 'b'}
    assert subject.output_keys_of(1) == {'a', 'b'}
    assert subject.input_keys_of('a') == {1, 2, 3}
    assert subject.map({1: 1, 2: 2, 3: 3}) == {'a': 1, 'b': 47}

    # It errors when functions aren't annotated with @trace_map_func.
    def some_func(x):
        return x

    with pytest.raises(AttributeError):
        TracedMap(funcs=[some_func])

    # It can map with a dict and funcs and apply a formatter
    def wrap_it(key, value):
        return "-{}-".format(value)

    subject = TracedMap(
        _dict=map_dict, funcs=[map_func_1, map_func_2], formatter=wrap_it
    )
    assert subject.input_keys() == {1, 2, 3}
    assert subject.output_keys() == {'a', 'b', '1', TypeError, (3, 3)}
    assert subject.output_keys_of(1) == {'a', 'b', '1'}
    assert subject.input_keys_of('a') == {1, 2, 3}
    assert subject.map({1: 1, 2: 2, 3: 3}) == {
        'a': '-1-', 'b': '-47-', '1': '-1-', TypeError: '-2-', (3, 3): '-3-'
    }
