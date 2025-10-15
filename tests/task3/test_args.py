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
