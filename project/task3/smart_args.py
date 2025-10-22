import copy
import inspect
from functools import wraps
from typing import Any, Callable, Dict, List, Tuple, Set


class Evaluated:
    """
    Wrapper for default values
    """

    def __init__(self, func: Callable[[], Any]) -> None:
        if not callable(func):
            raise TypeError("Evaluated requires a callable function")
        self.func = func


class Isolated:
    """
    Marker for arguments that should be deep copied when passed to the function.
    """

    pass


def smart_args(
    support_positional: bool = False,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator that analyzes default values and handles Evaluated/Isolated markers.

    Parameters:
        support_positional: If True, enables support for positional arguments

    Returns:
        Decorated function with smart argument handling
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        sig: inspect.FullArgSpec = inspect.getfullargspec(func)
        arg_names: List[str] = sig.args
        defaults: Tuple[Any, ...] = sig.defaults or ()
        kwonlydefaults: Dict[str, Any] = sig.kwonlydefaults or {}

        default_values: Dict[str, Any] = {}

        evaluated_params: Set[str] = set()
        isolated_params: Set[str] = set()

        if defaults:
            offset: int = len(arg_names) - len(defaults)
            for i, default in enumerate(defaults):
                param_name: str = arg_names[offset + i]
                default_values[param_name] = default
                if isinstance(default, Evaluated):
                    evaluated_params.add(param_name)
                elif default is Isolated:
                    isolated_params.add(param_name)

        for param_name, default_val in kwonlydefaults.items():
            default_values[param_name] = default_val
            if isinstance(default_val, Evaluated):
                evaluated_params.add(param_name)
            elif default_val is Isolated:
                isolated_params.add(param_name)

        for param_name, default_val in default_values.items():
            is_evaluated: bool = isinstance(default_val, Evaluated)
            is_isolated: bool = default_val is Isolated

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
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            final_kwargs: Dict[str, Any] = {}
            try:
                bound: inspect.BoundArguments = inspect.signature(func).bind(
                    *args, **kwargs
                )
                bound_args: Dict[str, Any] = bound.arguments
            except TypeError as e:
                missing_params = [
                    name for name in isolated_params if name not in bound_args
                ]
                if missing_params:
                    raise TypeError(
                        f"Missing required arguments: {', '.join(missing_params)}"
                    )
                raise e

            all_param_names = (
                set(arg_names) | set(kwonlydefaults.keys()) | set(sig.kwonlyargs)
            )

            for param_name in all_param_names:
                if param_name in bound_args:
                    arg_value = bound_args[param_name]
                    if param_name in isolated_params:
                        final_kwargs[param_name] = copy.deepcopy(arg_value)
                    else:
                        final_kwargs[param_name] = arg_value
                else:
                    if param_name in evaluated_params:
                        final_kwargs[param_name] = default_values[param_name].func()
                    elif param_name in isolated_params:
                        raise TypeError(f"Missing required argument: '{param_name}'")
                    elif param_name in default_values:
                        final_kwargs[param_name] = default_values[param_name]
                    else:
                        raise TypeError(f"Missing required argument: '{param_name}'")

            return func(**final_kwargs)

        return wrapper

    return decorator
