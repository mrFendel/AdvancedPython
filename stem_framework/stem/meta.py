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


def get_meta_attr(meta: Meta, key: str, default: Optional[Any] = None) -> Optional[Any]:
    if type(meta) is dict:
        try:
            return meta[key]
        except KeyError:
            return default
    else:
        try:
            return getattr(meta, key)
        except AttributeError:
            return default


def update_meta(meta: Meta, **kwargs):
    if type(meta) is dict:
        for keyword, arg in kwargs.items():
            meta[keyword] = arg
    else:
        for keyword, arg in kwargs.items():
            setattr(meta, keyword, arg)
