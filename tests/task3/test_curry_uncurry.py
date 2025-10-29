import pytest

from project.task3.curry_uncurry import curry_explicit, cache_results, uncurry_explicit


def test_curry_basic_functionality():
    def add_three(a, b, c):
        return a + b + c

    curried = curry_explicit(add_three, 3)
    assert curried(1)(2)(3) == 6


def test_uncurry_basic_functionality():
    def add_three(a, b, c):
        return a + b + c

    curried = curry_explicit(add_three, 3)
    uncurried = uncurry_explicit(curried, 3)
    assert uncurried(1, 2, 3) == 6


def test_curry_uncurry_roundtrip():
    def multiply_four(a, b, c, d):
        return a * b * c * d

    curried = curry_explicit(multiply_four, 4)
    uncurried = uncurry_explicit(curried, 4)
    assert uncurried(2, 3, 4, 5) == 120


def test_arity_zero():
    def constant_value():
        return 42

    curried = curry_explicit(constant_value, 0)
    assert curried() == 42

    uncurried = uncurry_explicit(curried, 0)
    assert uncurried() == 42


def test_arity_one():
    def square(x):
        return x * x

    curried = curry_explicit(square, 1)
    assert curried(5) == 25

    uncurried = uncurry_explicit(curried, 1)
    assert uncurried(5) == 25


def test_error_handling_negative_arity():
    def simple_func(x):
        return x

    with pytest.raises(TypeError):
        curry_explicit(simple_func, -1)

    with pytest.raises(TypeError):
        uncurry_explicit(simple_func, -1)


def test_error_handling_wrong_argument_count():
    def simple_func(x):
        return x

    curried = curry_explicit(simple_func, 1)
    with pytest.raises(TypeError):
        curried(1)(2)

    uncurried = uncurry_explicit(curried, 1)
    with pytest.raises(TypeError):
        uncurried()
    with pytest.raises(TypeError):
        uncurried(1, 2)


def test_lambda_functions():
    curried_lambda = curry_explicit(lambda x, y: x**y, 2)
    assert curried_lambda(2)(3) == 8

    uncurried_lambda = uncurry_explicit(curried_lambda, 2)
    assert uncurried_lambda(2, 3) == 8


def test_function_composition():
    curried_add = curry_explicit(lambda x, y: x + y, 2)
    curried_mult = curry_explicit(lambda x, y: x * y, 2)

    add_result = curried_add(2)(3)
    mult_result = curried_mult(add_result)(4)
    assert mult_result == 20


def test_mutable_arguments():
    def process_data(data, modifier, count):
        return [modifier(item) * count for item in data]

    curried = curry_explicit(process_data, 3)
    step1 = curried([1, 2, 3])
    step2 = step1(lambda x: x + 1)
    result = step2(2)
    assert result == [4, 6, 8]


def test_strict_single_argument():
    def func(a, b, c):
        return a + b + c

    curried = curry_explicit(func, 3)

    assert curried(1)(2)(3) == 6

    with pytest.raises(TypeError):
        curried(1, 2)(3)

    with pytest.raises(TypeError):
        curried(1)(2, 3)


def test_builtin_functions():
    pow_curried = curry_explicit(lambda x, y: x**y, 2)
    assert pow_curried(2)(3) == 8

    len_curried = curry_explicit(lambda x: len(x), 1)
    assert len_curried("hello") == 5

    uncurried_pow = uncurry_explicit(pow_curried, 2)
    assert uncurried_pow(3, 2) == 9


def test_variable_arity_functions():
    def sum_three(a, b, c):
        return a + b + c

    def sum_four(a, b, c, d):
        return a + b + c + d

    curried_three = curry_explicit(sum_three, 3)
    curried_four = curry_explicit(sum_four, 4)

    assert curried_three(1)(2)(3) == 6
    assert curried_four(1)(2)(3)(4) == 10

    uncurried_three = uncurry_explicit(curried_three, 3)
    uncurried_four = uncurry_explicit(curried_four, 4)

    assert uncurried_three(1, 2, 3) == 6
    assert uncurried_four(1, 2, 3, 4) == 10


def test_complex_currying():
    functions = [
        (lambda: 42, 0),
        (lambda x: x * 2, 1),
        (lambda x, y: x + y, 2),
        (lambda x, y, z: x * y * z, 3),
        (lambda a, b, c, d: a + b + c + d, 4),
    ]

    for func, arity in functions:
        curried = curry_explicit(func, arity)
        uncurried = uncurry_explicit(curried, arity)

        if arity == 0:
            assert curried() == func()
        elif arity == 1:
            assert curried(5) == func(5)
        elif arity == 2:
            assert curried(2)(3) == func(2, 3)
        elif arity == 3:
            assert curried(2)(3)(4) == func(2, 3, 4)
        elif arity == 4:
            assert curried(1)(2)(3)(4) == func(1, 2, 3, 4)

        if arity == 0:
            assert uncurried() == func()
        elif arity == 1:
            assert uncurried(5) == func(5)
        elif arity == 2:
            assert uncurried(2, 3) == func(2, 3)
        elif arity == 3:
            assert uncurried(2, 3, 4) == func(2, 3, 4)
        elif arity == 4:
            assert uncurried(1, 2, 3, 4) == func(1, 2, 3, 4)


def test_curry_with_different_types():
    concat_curried = curry_explicit(lambda a, b: a + b, 2)
    assert concat_curried("hello")(" world") == "hello world"

    list_curried = curry_explicit(lambda a, b: a + b, 2)
    assert list_curried([1, 2])([3, 4]) == [1, 2, 3, 4]

    dict_curried = curry_explicit(lambda a, b: {**a, **b}, 2)
    result = dict_curried({"a": 1})({"b": 2})
    assert result == {"a": 1, "b": 2}


def test_cache_simple():
    calls = 0

    @cache_results()
    def add(x, y):
        nonlocal calls
        calls += 1
        return x + y

    assert add(1, 2) == 3
    assert calls == 1
    assert add(1, 2) == 3
    assert calls == 1


def test_cache_different_args():
    calls = 0

    @cache_results()
    def func(x):
        nonlocal calls
        calls += 1
        return x * 2

    assert func(1) == 2
    assert func(1) == 2
    assert calls == 1


def test_curry_high_arity():
    def func(a, b, c, d, e):
        return a + b + c + d + e

    curried = curry_explicit(func, 5)
    result = curried(1)(2)(3)(4)(5)
    assert result == 15


def test_uncurry_high_arity():
    def func(a, b, c, d):
        return a * b * c * d

    curried = curry_explicit(func, 4)
    uncurried = uncurry_explicit(curried, 4)
    assert uncurried(2, 3, 4, 5) == 120


def test_curry_cache_combined():
    calls = 0

    @cache_results()
    def mul(x, y, z):
        nonlocal calls
        calls += 1
        return x * y * z

    assert mul(2, 3, 4) == 24
    assert calls == 1
    assert mul(2, 3, 4) == 24
    assert calls == 1
