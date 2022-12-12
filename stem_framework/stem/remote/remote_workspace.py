import json
import mmap
import socket
from io import BytesIO
from typing import Any, TypeVar, Iterator

from stem_framework.stem.envelope import Envelope
from stem_framework.stem.meta import Meta, get_meta_attr
from stem_framework.stem.task import Task
from stem_framework.stem.workspace import IWorkspace

T = TypeVar("T")


class RemoteTask(Task):
    def __init__(self, task_path, address='localhost', port=8888):
        self.task_path = task_path
        self.address = address
        self.port = port

    def transform(self, meta: Meta, /, **kwargs: Any) -> T:
        with socket.create_connection((self.address, self.port)) as socket_obj:
            socket_serial = socket_obj.makefile('rwb')
            request = Envelope({'command': 'run', 'task_path': self.task_path, 'task_meta': meta})
            request.write_to(socket_serial)
            socket_serial.flush()
            response = Envelope.read(socket_serial)

        if get_meta_attr(response.meta, 'status') != 'filled':
            raise ValueError(response.meta)

        if isinstance(response.data, mmap.mmap):
            return json.load(response.data)
        else:
            return json.load(BytesIO(response.data))


class RemoteWorkspace(IWorkspace):

    def __init__(self, path: str, address="localhost", port=8081):
        self.address = address
        self.port = port
        self.workspace_path = path

    def structure(self) -> dict[str, object]:
        with socket.create_connection((self.address, self.port)) as socket_obj:
            socket_serial = socket_obj.makefile('rwb')
            Envelope({'command': 'structure'}).write_to(socket_serial)
            socket_serial.flush()
            response = Envelope.read(socket_serial)

        if get_meta_attr(response.meta, 'status') != 'filled':
            raise ValueError(response.meta)

        if isinstance(response.data, mmap.mmap):
            structure = json.load(response.data)
        else:
            structure = json.load(BytesIO(response.data))

        for subworkspace_name in self.workspace_path.split('.'):
            for subworkspace in structure['workspaces']:
                if subworkspace['name'] == subworkspace_name:
                    structure = subworkspace
                    break

        return structure

    @staticmethod
    def _get_workspace_paths(prefix: str, structure: dict) -> Iterator[str]:
        for workspace in structure['workspaces']:
            yield prefix + workspace['name'] + '.'

    @staticmethod
    def _get_task_paths(prefix: str, structure: dict) -> Iterator[str]:
        for task_name in structure['tasks']:
            yield prefix + task_name

    @property
    def tasks(self) -> dict[str, Task]:
        task_paths = self._get_task_paths(self.workspace_path, self.structure())

        return {task_path: RemoteTask(task_path, self.address, self.port) for task_path in task_paths}

    @property
    def workspaces(self) -> set["IWorkspace"]:
        workspace_paths = self._get_workspace_paths(self.workspace_path, self.structure())
        return set(RemoteWorkspace(self.address, self.port, workspace_path) for workspace_path in workspace_paths)
