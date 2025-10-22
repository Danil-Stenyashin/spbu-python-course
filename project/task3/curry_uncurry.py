from typing import Any, Callable, TypeVar, cast

T = TypeVar("T")
R = TypeVar("R")


def curry_explicit(function: Callable[..., R], arity: int) -> Callable[..., Any]:
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


def uncurry_explicit(function: Callable[..., Any], arity: int) -> Callable[..., R]:
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

    def uncurried(*args: Any) -> R:
        if len(args) != arity:
            raise TypeError(
                f"Function takes exactly {arity} arguments, but {len(args)} were given"
            )

        result: Any = function
        for arg in args:
            result = result(arg)
        return cast(R, result)

    return uncurried


def cache_results(
    max_size: int | None = None,
) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    Decorator for caching function results.

    Parameters:
        max_size: Maximum number of results to cache (None for unlimited)

    Returns:
        Decorated function with caching support
    """

    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        cache: dict[tuple[tuple[Any, ...], tuple[tuple[Any, Any], ...]], R] = {}
        cache_order: list[tuple[tuple[Any, ...], tuple[tuple[Any, Any], ...]]] = []

        def wrapper(*args: Any, **kwargs: Any) -> R:
            key = (args, tuple(sorted(kwargs.items())))

            if key in cache:
                cache_order.remove(key)
                cache_order.append(key)
                return cache[key]

            result: R = func(*args, **kwargs)

            cache[key] = result
            cache_order.append(key)

            if max_size is not None and len(cache) > max_size:
                oldest_key = cache_order.pop(0)
                del cache[oldest_key]

            return result

        def clear_cache() -> None:
            cache.clear()
            cache_order.clear()

        def get_cache_info() -> dict[str, Any]:
            return {
                "cache_size": len(cache),
                "max_size": max_size,
                "cache_keys": list(cache.keys()),
            }

        wrapper.clear_cache = clear_cache
        wrapper.cache_info = get_cache_info

        return wrapper

    return decorator
