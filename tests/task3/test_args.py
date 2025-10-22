import pytest
import random

from project.task3.smart_args import smart_args, Evaluated, Isolated


def test_isolated():
    @smart_args()
    def func(*, data=Isolated):
        data.append(1)
        return data

    original = []
    result = func(data=original)
    assert result == [1]
    assert original == []


def test_evaluated():
    calls = 0

    def counter():
        nonlocal calls
        calls += 1
        return calls

    @smart_args()
    def func(*, x=Evaluated(counter)):
        return x

    assert func() == 1
    assert func() == 2
    assert func(x=10) == 10
    assert calls == 2


def test_isolated_with_dict():
    @smart_args()
    def func(*, d=Isolated):
        d["changed"] = True
        return d

    original = {}
    result = func(d=original)
    assert result == {"changed": True}
    assert original == {}


def test_evaluated_random():
    @smart_args()
    def func(*, x=Evaluated(lambda: random.randint(1, 100))):
        return x

    results = {func() for _ in range(10)}
    assert len(results) > 1


def test_missing_isolated():
    @smart_args()
    def func(*, data=Isolated):
        return data

    with pytest.raises(TypeError):
        func()


def test_positional_disabled():
    with pytest.raises(ValueError):

        @smart_args()
        def func(x=Isolated):
            pass


def test_positional_enabled():
    @smart_args(support_positional=True)
    def func(x=Isolated, *, y=Evaluated(lambda: 5)):
        return x, y

    result = func([1])
    assert result == ([1], 5)


def test_builtin_functions_with_smart_args():
    @smart_args()
    def custom_len(*, data=Isolated):
        return len(data)

    @smart_args()
    def custom_max(*, numbers=Isolated, default=Evaluated(lambda: 0)):
        return max(numbers) if numbers else default

    test_list = [1, 2, 3]
    result = custom_len(data=test_list)
    assert result == 3
    assert test_list == [1, 2, 3]

    assert custom_max(numbers=[]) == 0
    assert custom_max(numbers=[5, 10, 3]) == 10


def test_various_arities_with_smart_args():
    @smart_args()
    def constant(*, value=Evaluated(lambda: 100)):
        return value

    @smart_args()
    def increment(*, x=Isolated):
        return x + 1

    @smart_args()
    def calculate(*, a=Isolated, b=Isolated, multiplier=Evaluated(lambda: 1)):
        return (a + b) * multiplier

    assert constant() == 100
    assert increment(x=5) == 6

    result = calculate(a=2, b=3)
    assert result == 5
    result_with_multiplier = calculate(a=2, b=3, multiplier=10)
    assert result_with_multiplier == 50


def test_complex_smart_args_scenarios():
    call_counter = 0

    def counting_factory():
        nonlocal call_counter
        call_counter += 1
        return f"called_{call_counter}"

    @smart_args()
    def complex_function(
        *,
        required_data=Isolated,
        computed_value=Evaluated(counting_factory),
        optional_value=42,
    ):
        return {
            "data": required_data,
            "computed": computed_value,
            "optional": optional_value,
        }

    result1 = complex_function(required_data=[1, 2, 3])
    assert result1["data"] == [1, 2, 3]
    assert result1["computed"] == "called_1"
    assert result1["optional"] == 42

    result2 = complex_function(required_data={"test": "value"})
    assert result2["computed"] == "called_2"
    assert result2["data"] == {"test": "value"}

    result3 = complex_function(
        required_data="hello", computed_value="manual", optional_value=100
    )
    assert result3["computed"] == "manual"
    assert result3["optional"] == 100
