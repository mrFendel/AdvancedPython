from typing import TypeVar, Optional, Generic, Type

from .task import Task
from .workspace import IWorkspace

T = TypeVar("T")


class TaskNode(Generic[T]):
    def __init__(self, task: Task[T], workspace: Optional[IWorkspace] = None):
        self.task = task
        self._dependencies = list()
        self._unresolved_dependencies = list()
        self._has_dependence_errors = None
        self.workspace = workspace

        if workspace is None:
            workspace_ = IWorkspace.find_default_workspace(task)
        else:
            workspace_ = workspace

        for dependence in task.dependencies:
            if isinstance(dependence, Task):
                self._dependencies.append(TaskNode(dependence, workspace))
            elif (tsk := workspace_.find_task(dependence)) is None:
                self._unresolved_dependencies.append(dependence)
            else:
                self._dependencies.append(TaskNode(tsk, workspace))

        self._has_dependence_errors = self._unresolved_dependencies != [] or any(
            dependence._has_dependence_errors for dependence in self.dependencies)

    @property
    def dependencies(self) -> list["TaskNode"]:
        return self._dependencies

    @property
    def is_leaf(self) -> bool:
        return self.dependencies == []

    @property
    def unresolved_dependencies(self) -> list["str"]:
        return self._unresolved_dependencies

    @property
    def has_dependence_errors(self) -> bool:
        return self._has_dependence_errors

    def find_node(self, task: Task[T]) -> Optional["TaskNode[T]"]:
        if self.task == task:
            return self
        else:
            for d in self.dependencies:
                if (node := d.resolve_node(task)) is not None:
                    return node

    def resolve_node(self, task: Task[T], workspace: Type[IWorkspace] | None = None) -> "TaskNode[T]":
        if workspace is None or workspace == self.workspace:
            if (node := self.find_node(task)) is not None:
                return node
        else:
            return TaskNode(task, workspace)


class TaskTree(TaskNode):

    def resolve_node(self, task: Task[T], workspace: Optional[IWorkspace] = None) -> TaskNode[T]:
        if workspace is None or workspace == self.workspace:
            if (node := self.find_node(task)) is not None:
                return node
        else:
            return TaskNode(task, workspace)

    @staticmethod
    def build_node(task: Task[T]):
        return TaskNode(task)
