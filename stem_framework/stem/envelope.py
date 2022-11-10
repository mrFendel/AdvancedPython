import array
import mmap
from asyncio import StreamReader, StreamWriter
from dataclasses import is_dataclass, asdict
from io import RawIOBase, BufferedReader, BytesIO
from json import JSONEncoder
from typing import Optional, Union, Any
from .meta import Meta
import json


Binary = Union[bytes, bytearray, memoryview, array.array, mmap.mmap]


class MetaEncoder(JSONEncoder):

    def default(self, obj: Meta) -> Any:
        if is_dataclass(obj):
            return asdict(obj)
        elif isinstance(obj, dict):
            return obj
        else:
            raise TypeError


class Envelope:
    _MAX_SIZE = 128*1024*1024

    def __init__(self, meta: Meta, data: Optional[Binary] = None):
        self.meta = meta
        self.data = data

    def __str__(self):
        return str(self.meta)

    @staticmethod
    def read(input_: BufferedReader) -> "Envelope":
        input_.read(2)
        metaLength = int.from_bytes(input_.read(4))
        dataLength = int.from_bytes(input_.read(4))
        meta = json.loads(input_.read(metaLength))

        if dataLength < Envelope._MAX_SIZE:
            data = input_.read(dataLength)
        else:
            data = mmap.mmap(input_.fileno(), dataLength, offset=input_.tell())
        return Envelope(meta, data)

    @staticmethod
    def from_bytes(buffer: bytes) -> "Envelope":
        return Envelope.read(BytesIO(buffer))

    def to_bytes(self) -> bytes:
        output = BytesIO()
        self.write_to(output)
        output.seek(0)
        return output.read()

    def write_to(self, output: RawIOBase):
        output.write(b'#~')
        output.write(b'DF02')
        output.write(b'..')
        meta_str = bytes(json.dumps(self.meta), 'utf8')

        output.write(len(meta_str).to_bytes(4))
        output.write(len(self.data).to_bytes(4))
        output.write(meta_str)
        output.write(self.data)

        output.write(b'~#')

    @staticmethod
    async def async_read(reader: StreamReader) -> "Envelope":
        pass  # TODO(Assignment 11)

    async def async_write_to(self, writer: StreamWriter):
        pass  # TODO(Assignment 11)
