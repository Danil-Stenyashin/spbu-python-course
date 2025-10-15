import copy
import inspect
from functools import wraps


class Evaluated:
    """
    Wrapper for default values
    """

    def __init__(self, func):
        if not callable(func):
            raise TypeError("Evaluated requires a callable function")
        self.func = func


class Isolated:
    """
    Marker for arguments that should be deep copied when passed to the function.
    """

    pass


def smart_args(support_positional=False):
    """
    Decorator that analyzes default values and handles Evaluated/Isolated markers.

    Parameters:
        support_positional: If True, enables support for positional arguments

    Returns:
        Decorated function with smart argument handling
    """

    def decorator(func):
        sig = inspect.getfullargspec(func)
        arg_names = sig.args
        defaults = sig.defaults or ()
        kwonlydefaults = sig.kwonlydefaults or {}

        default_values = {}

        if defaults:
            offset = len(arg_names) - len(defaults)
            for i, default in enumerate(defaults):
                param_name = arg_names[offset + i]
                default_values[param_name] = default

        default_values.update(kwonlydefaults)

        for param_name, default_val in default_values.items():
            is_evaluated = isinstance(default_val, Evaluated)
            is_isolated = default_val is Isolated

            if is_evaluated and is_isolated:
                raise ValueError(
                    f"Parameter '{param_name}' cannot use both Evaluated and Isolated"
                )

            if not support_positional and param_name in arg_names:
                if is_evaluated or is_isolated:
                    raise ValueError(
                        f"Evaluated/Isolated can only be used with keyword-only arguments. "
                        f"Parameter '{param_name}' is positional."
                    )

        @wraps(func)
        def wrapper(*args, **kwargs):
            final_kwargs = {}

            try:
                bound = inspect.signature(func).bind(*args, **kwargs)
                bound_args = bound.arguments
            except TypeError as e:
                missing_params = [
                    name
                    for name in default_values
                    if default_values[name] is Isolated
                    and name not in kwargs
                    and (not support_positional or name not in arg_names[: len(args)])
                ]
                if missing_params:
                    raise TypeError(f"Missing required argument")
                raise e

            for param_name in default_values:
                default_val = default_values[param_name]

                if param_name in bound_args:
                    arg_value = bound_args[param_name]
                    if default_val is Isolated:
                        final_kwargs[param_name] = copy.deepcopy(arg_value)
                    else:
                        final_kwargs[param_name] = arg_value
                else:
                    if isinstance(default_val, Evaluated):
                        final_kwargs[param_name] = default_val.func()
                    elif default_val is Isolated:
                        raise TypeError(f"Missing required argument")
                    else:
                        final_kwargs[param_name] = default_val

            return func(**final_kwargs)

        return wrapper

    return decorator
