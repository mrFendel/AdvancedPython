from dataclasses import dataclass, is_dataclass
from typing import Optional, Any, Union, Type, Tuple
from stem_framework.stem.core import Dataclass


Meta = Union[dict, Dataclass]

SpecificationField = Tuple[object, Union[Type, Tuple[Type, ...], Type[Meta]]]

Specification = Union[Type[Dataclass], Type[SpecificationField]]


class SpecificationError(Exception):
    pass


@dataclass
class MetaFieldError:
    required_key: str
    required_types: Optional[tuple[type]] = None
    presented_type: Optional[type] = None
    presented_value: Any = None


class MetaVerification:

    def __init__(self, *errors: Union[MetaFieldError, "MetaVerification"]):
        self.error = errors

    @property
    def checked_success(self):
        flag = True
        for err in self.error:
            if isinstance(err, MetaFieldError):
                flag = False
                break
        return flag

    @staticmethod
    def verify(meta: Meta,
               specification: Optional[Specification] = None) -> "MetaVerification":
        if is_dataclass(meta):
            meta_keys = meta.__dataclass_fields__.keys()
        elif isinstance(meta, dict):
            meta_keys = meta.keys()
        else:
            meta_keys = tuple()

        if is_dataclass(specification):
            specification_keys = specification.__dataclass_fields__.keys()
        else:
            specification = dict(specification)
            specification_keys = specification.keys()

        errors = list()
        for required_key in specification_keys:
            if is_dataclass(specification):
                required_types = specification.__dataclass_fields__[required_key].type
            else:
                required_types = specification[required_key]

Metadata processing:
    This principle postulates that, during the
processing of data, only initial data and it's metadata are allowed to be used as input.
This means no user instructions (scripts) or
manually managed intermediate states are possible.
"""