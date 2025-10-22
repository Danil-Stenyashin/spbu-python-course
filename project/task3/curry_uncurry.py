from typing import Any, Callable, Dict, List, Tuple, Union


def curry_explicit(function: Callable[..., Any], arity: int) -> Callable[..., Any]:
    """
    Transforms a multi-parameter function into a curried function.

    Parameters:
        function: The original function to be curried
        arity: Number of arguments the function should accept

    Returns:
        Curried version of the function

    Raises:
        TypeError: If arity is negative or not an integer
    """
    if not isinstance(arity, int) or arity < 0:
        raise TypeError("Arity must be a non-negative integer")

    if arity == 0:
        return lambda: function()

    def curried(arg: Any) -> Any:
        if arity == 1:
            return function(arg)

        def next_curried(next_arg: Any) -> Any:
            return curry_explicit(lambda *args: function(arg, *args), arity - 1)(
                next_arg
            )

        return next_curried

    return curried


def uncurry_explicit(function: Callable[..., Any], arity: int) -> Callable[..., Any]:
    """
    Transforms a curried function back into a regular multi-parameter function.

    Parameters:
        function: The curried function
        arity: Number of arguments the function should accept

    Returns:
        Regular version of the function

    Raises:
        TypeError: If arity is negative or not an integer
    """
    if not isinstance(arity, int) or arity < 0:
        raise TypeError("Arity must be a non-negative integer")

    if arity == 0:
        return lambda: function()

    def uncurried(*args: Any) -> Any:
        if len(args) != arity:
            raise TypeError(
                f"Function takes exactly {arity} arguments, but {len(args)} were given"
            )

        result: Any = function
        for arg in args:
            result = result(arg)
        return result

    return uncurried


def cache_results(
    max_size: Union[int, None] = None
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator for caching function results.

    Parameters:
        max_size: Maximum number of results to cache (None for unlimited)

    Returns:
        Decorated function with caching support
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        cache: Dict[Tuple[Tuple[Any, ...], Tuple[Tuple[Any, Any], ...]], Any] = {}
        cache_order: List[Tuple[Tuple[Any, ...], Tuple[Tuple[Any, Any], ...]]] = []

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = (args, tuple(sorted(kwargs.items())))

            if key in cache:
                cache_order.remove(key)
                cache_order.append(key)
                return cache[key]

            result: Any = func(*args, **kwargs)

            cache[key] = result
            cache_order.append(key)

            if max_size is not None and len(cache) > max_size:
                oldest_key = cache_order.pop(0)
                del cache[oldest_key]

            return result

        def clear_cache() -> None:
            cache.clear()
            cache_order.clear()

        def get_cache_info() -> Dict[str, Any]:
            return {
                "cache_size": len(cache),
                "max_size": max_size,
                "cache_keys": list(cache.keys()),
            }

        class CachedFunction:
            def __call__(self, *args: Any, **kwargs: Any) -> Any:
                return wrapper(*args, **kwargs)

            def clear_cache(self) -> None:
                clear_cache()

            def cache_info(self) -> Dict[str, Any]:
                return get_cache_info()

        return CachedFunction()

    return decorator
