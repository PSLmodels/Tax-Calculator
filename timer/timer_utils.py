from timeit import default_timer as timer
from contextlib import contextmanager
from functools import wraps


class cumulative_timer(object):
    """
    Timer for use with timing specific lines of code and accumulating the same
    timer in multiple places

    ex.
    Declaration:        example_timer_name = (
                        Cumulative_Timer("Insert description to be printed"))

    Timing:             with example_timer_name.time():

                            ## everything inside indentation will be timed
                            ## code block #1

                        do_not_time_this_function()


                        with example_timer_name.time():
                            ## code block #2 to be timed

    Print results:      print(example_timer_name)
                        # will print the combined time of code block
                        # #1 & #2, along with timer description
    """
    def __init__(self, name):
        self.name = name
        self.duration = 0

    @contextmanager
    def time(self):
        ts = timer()
        yield
        te = timer()
        self.duration += te - ts

    def __repr__(self):
        return "~~~ {name} takes {duration}s".format(name=self.name,
                                                     duration=self.duration)


def time_this(function, running_timer=None):
    """
    Decorator that prints the execution time of a function,
    optionally adds the time to a running timer

    example usage:     @time_this or @time_this(timer_name)

    :param function:        the function to be timed
    :param running_timer:   an optional cumulative_timer, of which
                            to add the time elapsed of the passed function
                            Set to None by default,
                            prints time for the called function only
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        start = timer()
        if running_timer is not None:
            with running_timer.time():
                result = function(*args, **kwargs)
        else:
            result = function(*args, **kwargs)
        end = timer()
        print ("~function: '{}' takes : {}s".format(function.__name__,
                                                    end-start))
        return result
    return wrapper
