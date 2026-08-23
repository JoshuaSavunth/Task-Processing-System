from typing import Any

from app.tasks.registry import get_task


def execute_task(task_type: str, input_value: int) -> Any:
    task = get_task(task_type)
    return task(input_value)
