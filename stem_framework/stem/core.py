from typing import Optional
from typing_extensions import Protocol
import dataclasses
import re

def pascal_case_to_snake_case(name: str) -> str:
    return re.sub(
        r"(?<=\w)[A-Z][a-z]",
        r"_\g<0>",
        name
    ).lower()


class Named:
    _name: Optional[str] = None

    @property
    def name(self):
        if self._name is not None:
            return self._name
        else:
            return pascal_case_to_snake_case(self.__class__.__name__)


class Dataclass(Protocol):
    number: int = 0
    value: float = 0.0
    data: Optional[list] = dataclasses.field(default_factory=list)
    name: Optional[str] = "here we go"
