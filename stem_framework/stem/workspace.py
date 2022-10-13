from abc import abstractmethod, ABC, ABCMeta
from importlib import import_module
from types import ModuleType
from typing import Optional, Any, TypeVar, Union
from typing_extensions import Self

from .core import Named
from .meta import Meta
from .task import Task

T = TypeVar("T")


class TaskPath:
    def __init__(self, path: Union[str, list[str]]):
        if isinstance(path, str):
            self._path = path.split(".")
        else:
            self._path = path

    @property
    def is_leaf(self):
        return len(self._path) == 1

    @property
    def sub_path(self):
        return TaskPath(self._path[1:])

    @property
    def head(self):
        return self._path[0]

    @property
    def name(self):
        return self._path[-1]

    def __str__(self):
        return ".".join(self._path)


class ProxyTask(Task[T]):

    def __init__(self, proxy_name, task: Task):
        self._name = proxy_name
        self._task = task

    @property
    def dependencies(self):
        return self._task.dependencies

    @property
    def specification(self):
        return self._task.specification

    def check_by_meta(self, meta: Meta):
        self._task.check_by_meta(meta)

    def transform(self, meta: Meta, /, **kwargs: Any) -> T:
        return self._task.transform(meta, **kwargs)


class IWorkspace(ABC, Named):

    @property
    @abstractmethod
    def tasks(self) -> dict[str, Task]:
        pass

    @property
    @abstractmethod
    def workspaces(self) -> set["IWorkspace"]:
        pass

    def find_task(cls, task_path: Union[str, TaskPath]) -> Optional[Task]:
        if not isinstance(task_path, TaskPath):
            task_path = TaskPath(task_path)
        if not task_path.is_leaf:
            for elem in cls.workspaces:
                if elem.name == task_path.head:
                    return elem.find_task(task_path.sub_path)
            return None
        else:
            for task_name in cls.tasks:
                if task_name == task_path.name:
                    return cls.tasks[task_name]
            for elem in cls.workspaces:
                if attr := elem.find_task(task_path) is not None:
                    return attr
            return None

    @classmethod
    def has_task(self, task_path: Union[str, TaskPath]) -> bool:
        return self.find_task(task_path) is not None

    def get_workspace(self, name) -> Optional["IWorkspace"]:
        for workspace in self.workspaces:
            if workspace.name == name:
                return workspace
        return None

    def structure(self) -> dict:
        return {
            "name": self.name,
            "tasks": list(self.tasks.keys()),
            "workspaces": [w.structure() for w in self.workspaces]
        }

    @staticmethod
    def find_default_workspace(task: Task) -> "IWorkspace":
        try:
            return task._stem_workspace
        except AttributeError:
            module = import_module(task.__module__)
            return IWorkspace.module_workspace(module)

    @staticmethod
    def module_workspace(module: ModuleType) -> "IWorkspace":
        try:
            return module.__stem_workspace

        except AttributeError:
            tasks = dict
            workspaces = set

            for elem in dir(module):
                attr = getattr(module, elem)
                if isinstance(attr, Task):
                    tasks[elem] = attr
                if isinstance(attr, IWorkspace):
                    workspaces.add(attr)

            module.__stem_workspace = LocalWorkspace(
                module.__name__, tasks, workspaces
            )

            return module.__stem_workspace


class ILocalWorkspace(IWorkspace):

    @property
    def tasks(self) -> dict[str, Task]:
        return self._tasks

    @property
    def workspaces(self) -> set["IWorkspace"]:
        return self._workspaces


class LocalWorkspace(ILocalWorkspace):

    def __init__(self, name,  tasks=(), workspaces=()):
        self._name = name
        self._tasks = tasks
        self._workspaces = workspaces


class Workspace(ABCMeta, ILocalWorkspace):
    def __new__(mcls: type[Self], name: str, bases: tuple[type, ...], namespace: dict[str, Any], **kwargs: Any) -> Self:

        cls = super().__new__(ABCMeta, name, bases, namespace, **kwargs)

        try:
            workspaces = set(cls.workspaces)
        except AttributeError:
            workspaces = set()

        cls_dict = {elem: attr for elem, attr in cls.__dict__.items() if not elem.startswith('__')}

        tasks_to_replace = {elem: ProxyTask(elem, attr) for elem, attr in cls_dict.items() if not callable(attr) and isinstance(attr, Task)}

        for elem, attr in tasks_to_replace.items():
            setattr(cls, elem, attr)
            cls_dict[elem] = attr

        for elem, attr in cls_dict.items():
            if isinstance(attr, Task):
                attr._stem_workspace = cls

        tasks_to_show = {elem: attr for elem, attr in cls_dict.items() if isinstance(attr, Task)}

        cls._tasks = tasks_to_show
        cls._workspaces = workspaces
        cls._name = name

        def __new(userclass, *args, **kwargs):
            return userclass

        cls.__new__ = __new

        return cls
