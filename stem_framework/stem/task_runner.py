from typing import Generic, TypeVar
from abc import ABC, abstractmethod

from .meta import Meta
from .task_tree import TaskNode

T = TypeVar("T")


class TaskRunner(ABC, Generic[T]):

    @abstractmethod
    def run(self, meta: Meta, task_node: TaskNode[T]) -> T:
        pass


class SimpleRunner(TaskRunner[T]):

    def run(self, meta: Meta, task_node: TaskNode[T]) -> T:
        pass  # TODO