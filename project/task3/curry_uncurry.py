def curry_explicit(function, arity):
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

    def curried(*args):
        if len(args) > arity:
            raise TypeError("Function takes more arguments then given")

        if len(args) == arity:
            return function(*args)

        def next_curried(*next_args):
            return curried(*(args + next_args))

        return next_curried

    return curried


def uncurry_explicit(function, arity):
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

    def uncurried(*args):
        if len(args) != arity:
            raise TypeError("Function takes more arguments then given")

        result = function
        for arg in args:
            result = result(arg)
        return result

    return uncurried


def cache_results(max_size=None):
    """
    Decorator for caching function results.

    Parameters:
        max_size: Maximum number of results to cache (None for unlimited)

    Returns:
        Decorated function with caching support
    """

    def decorator(func):
        cache = {}
        cache_order = []

        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))

            if key in cache:
                cache_order.remove(key)
                cache_order.append(key)
                return cache[key]

            result = func(*args, **kwargs)

            cache[key] = result
            cache_order.append(key)

            if max_size is not None and len(cache) > max_size:
                oldest_key = cache_order.pop(0)
                del cache[oldest_key]

            return result

        wrapper.clear_cache = lambda: (cache.clear(), cache_order.clear())
        wrapper.cache_info = lambda: {
            "cache_size": len(cache),
            "max_size": max_size,
            "cache_keys": list(cache.keys()),
        }

        return wrapper

    return decorator
