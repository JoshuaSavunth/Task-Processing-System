import pytest

from app.tasks.executor import execute_task
from app.tasks.fibonacci import fibonacci
from app.tasks.prime_factorization import prime_factorization


def test_fibonacci() -> None:
    assert fibonacci(0) == 0
    assert fibonacci(10) == 55


def test_prime_factorization() -> None:
    assert prime_factorization(84) == [2, 2, 3, 7]
    assert prime_factorization(97) == [97]


@pytest.mark.parametrize("value", [-1, -10])
def test_fibonacci_rejects_negative(value: int) -> None:
    with pytest.raises(ValueError):
        fibonacci(value)


def test_prime_factorization_rejects_one() -> None:
    with pytest.raises(ValueError):
        prime_factorization(1)


def test_executor_rejects_unknown_task() -> None:
    with pytest.raises(ValueError, match="unsupported"):
        execute_task("unknown", 1)