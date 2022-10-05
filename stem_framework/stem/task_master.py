from enum import Enum, auto
from typing import Optional, Callable, TypeVar, Generic
from functools import cached_property
from dataclasses import dataclass

from .meta import Meta
from .task import Task
from .workspace import Workspace
from .task_runner import TaskRunner, SimpleRunner
from .task_tree import TaskMetaError, TaskNode, TaskTree

T = TypeVar("T")


class TaskStatus(Enum):
    DEPENDENCIES_ERROR = auto()
    META_ERROR = auto()
    RUNTIME_ERROR = auto()
    CONTAINS_DATA = auto()


@dataclass
class TaskResult(Generic[T]):
    status: TaskStatus
    task_node: TaskNode
    meta_errors: list[TaskMetaError] = field(default_factory=list)
    lazy_data: Callable[[], T] = lambda: None

    @cached_property
    def data(self) -> Optional[T]:
        return self.lazy_data()


class TaskMaster:

    def __init__(self, task_runner: TaskRunner[T] = SimpleRunner(), task_tree: Optional[TaskTree] = None):
        self.task_runner = task_runner
        self.task_tree = task_tree

    def execute(self, meta: Meta, task: Task[T], workspace: Optional[Workspace] = None) -> TaskResult[T]:
        pass # TODO()