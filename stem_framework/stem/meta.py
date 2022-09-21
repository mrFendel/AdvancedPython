from dataclasses import dataclass
from typing import Optional, Any, Union


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
        errors = list()
        for required_key in specification_keys:
            if is_dataclass(specification):
                required_types = specification.__dataclass_fields__[required_key].type
            else:
                required_types = specification[required_key]

def update_meta(meta: Meta, **kwargs):
    if type(meta) is dict:
        for keyword, arg in kwargs.items():
            meta[keyword] = arg
    else:
        for keyword, arg in kwargs.items():
            setattr(meta, keyword, arg)
