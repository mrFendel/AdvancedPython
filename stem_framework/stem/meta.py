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
    required_types: Union[Type, Tuple[Type, ...], None] = None
    presented_type: Union[Type, None] = None
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

            if required_key not in meta_keys:
                errors.append(
                    MetaFieldError(
                        required_key=required_key,
                        required_types=required_types
                    )
                )
            else:
                presented_value = get_meta_attr(meta, required_key)
                presented_type = type(presented_value)

                if (isinstance(required_types, type) or (
                        isinstance(required_types, tuple) and isinstance(required_types[0], type)
                )):
                    if not issubclass(presented_type, required_types):
                        errors.append(
                            MetaFieldError(
                                required_key=required_key,
                                required_types=required_types,
                                presented_value=presented_value,
                                presented_type=presented_type
                            )
                        )
                else:
                    errors_next_level = MetaVerification.verify(
                        get_meta_attr(meta, required_key),
                        required_types
                    ).error

                    if errors_next_level != ():
                        errors.append(errors_next_level)
        return MetaVerification(*errors)

        if is_dataclass(meta):
            meta_keys = meta.__dataclass_fields__.keys()
        elif isinstance(meta, dict):
            meta_keys = meta.keys()
        else:
            meta_keys = ()

        if is_dataclass(specification):
            specification_keys = specification.__dataclass_fields__.keys()
        else:
            specification = dict(specification)
            specification_keys = specification.keys()

        errors = []
        for required_key in specification_keys:
            if is_dataclass(specification):
                required_types = specification.__dataclass_fields__[required_key].type
            else:
                required_types = specification[required_key]

            if required_key not in meta_keys:
                errors.append(
                    MetaFieldError(
                        required_key=required_key,
                        required_types=required_types
                    )
                )
            else:
                presented_value = get_meta_attr(meta, required_key)
                presented_type = type(presented_value)

                if (isinstance(required_types, type) or (
                        isinstance(required_types, tuple) and isinstance(required_types[0], type)
                )):
                    if not issubclass(presented_type, required_types):
                        errors.append(
                            MetaFieldError(
                                required_key=required_key,
                                required_types=required_types,
                                presented_value=presented_value,
                                presented_type=presented_type
                            )
                        )
                else:
                    errors_next_level = MetaVerification.verify(
                        get_meta_attr(meta, required_key),
                        required_types
                    ).error

                    if errors_next_level != ():
                        errors.append(errors_next_level)

        return MetaVerification(*errors)


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
