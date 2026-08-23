from collections.abc import Callable
from typing import Any

from app.tasks.fibonacci import fibonacci
from app.tasks.prime_factorization import prime_factorization

TaskFn = Callable[[int], Any]

TASKS: dict[str, TaskFn] = {
    "fibonacci": fibonacci,
    "prime_factorization": prime_factorization,
}


def get_task_names() -> list[str]:
    return list(TASKS.keys())


def get_task(name: str) -> TaskFn:
    if name not in TASKS:
        raise ValueError(f"Unknown task: {name}")
    return TASKS[name]
