"""
This is a Mapped schema class

It is used to map json and pydantic models to each other
"""
from abc import ABC, abstractmethod
from typing import Union

# Installed Packages
from glom import glom
from pydantic import BaseModel as BM
from pydantic import validator

class DefaultBaseModel(BM):
    class Config:
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True
        orm_mode = True
        nones_to_default = True

    @validator("*", pre=True, always=True)
    def _convert_nones_to_default(cls, val, field):
        nones_to_default = getattr(cls.Config, "nones_to_default", True)
        if nones_to_default and field.default and val is None:
            return field.default
        return val

class IgnoreGlom(str):
    """
    Ignore Glom nested string lookup
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    def __repr__(self):
        return f"IgnoreGlom({super().__repr__()})"


class _MappingMixinBase(ABC):
    @property
    @abstractmethod
    def output_model(self) -> DefaultBaseModel:
        return DefaultBaseModel

    @property
    @abstractmethod
    def map(self):
        return self.default_map()

    def process_map(self, map_dict: dict, input_dict: dict):
        return {k: self.process_map_value(v, input_dict) for k, v in map_dict.items()}

    def process_map_value(self, value, input_dict: dict):
        if isinstance(value, IgnoreGlom):
            # This needs to be at the top
            return str(value)
        if isinstance(value, str):
            return glom(input_dict, value, default=value)

        if isinstance(value, tuple):
            keys, search = value
            if isinstance(keys, list):
                combined = []
                for val in keys:
                    result = glom(input_dict, (val, search), default=None)
                    if isinstance(result, list):
                        combined += result
                    if isinstance(result, str):
                        combined.append(result)
                return combined
            if isinstance(keys, str):
                return glom(input_dict, value, default=None)
        if isinstance(value, dict):
            return self.process_map(value, input_dict)
        if isinstance(value, list):
            return [self.process_map_value(v, input_dict) for v in value]

        if callable(value):
            return value(input_dict)
        else:
            return value


class MappedModel(DefaultBaseModel, _MappingMixinBase, ABC):
    """
    A Pydantic Mapped model class

    ...

    Class Attributes
    ----------
    mapped : Model
        converts a python dict to the corresponding mapped model
    output_model : DefaultBaseModel
        return a DefaultBaseModel
    map : int
        returns a map of dict keys

    Methods
    -------
    default_map(exclude: Union[set, dict]):
        returns mapped dict keys with optionalexclude keys param
    """

    @property
    def mapped(self):
        input_dict = self.dict()
        processed_map = self.process_map(self.map, input_dict)
        return self.output_model(**processed_map)

    def default_map(self, exclude: Union[set, dict] = None):
        input_dict = self.dict(exclude=exclude)
        return {k: k for k in input_dict.keys()}

    @property
    def output_model(self) -> DefaultBaseModel:
        return DefaultBaseModel

    @property
    def map(self):
        return self.default_map()


class MapDictToModel(_MappingMixinBase, ABC):
    """Leverages Glom to map python dictionaries to a mapped pydantic model

    glom works by by doing nested dictionary searches
    so instead of data['a']['b']['c']
    we use glom(data, 'a.b.c')

    This class uses glom to map key value pairs to a Pydantic model Field
    map: dict = {
        "Pydantic Model Field": "glom.recursive.lookup"
        }

    We leverage tuples to collapse values to a list and to merge nested structs

    # nested dictionary structures
    key: ("lookup.value", [{"nested_key", "nested_key_lookup"}])

    # merged keys
    key: (["lookup.value"], "loo")

    Example dictionary Input:

        input_dict = {
                "items": {
                    "price": 7,
                    "price2": 7,
                    "nested": [
                        {"list_val": 1, "amount": 3.05},
                        {"list_val": 2, "amount": 4},
                    ],
                    "identical": "value to be combined",
                },
                "items2": {"identical": "second value to be combined"},
            }
    Example Pydantic Model:

        class APydanticModel(BM):
            my_pydantic_field: int
            my_nested_fields: list
            my_collapsible_field: list

    Example MapDictToModel class:

         class MyClass(MapDictToModel):
            output_model = APydanticModel

            map: dict = {
                "my_pydantic_field": "items.price",
                "my_nested_fields": (
                    "items.nested",
                    [
                        {
                            "my_list_val": "list_val",
                            "my_amount": "amount",
                        }
                    ],
                ),
                "my_collapsible_field": (["items", "items2"], "identical"),
            }

    Usage:
        my_pydantic_model = MyClass(input_dict).mapped
        my_pydantic_model.my_pydantic_field
            result -> 7
        my_pydantic_model.my_nested_fields
            result -> [{'my_list_val': 1, 'my_amount': 3.05}, {'my_list_val': 2, 'my_amount': 4}]
        my_pydantic_model.my_collapsible_field
            result -> ['value to be combined', 'second value to be combined']
    """

    input_dict: dict = None

    def __init__(self, input_dict: dict, *args, **kwargs):
        """
        Initializes input dictionary and super inits _MappingMixinBase
        """
        self.input_dict = input_dict
        super().__init__(*args, **kwargs)

    @property
    def mapped(self):
        processed_map = self.process_map(self.map, self.input_dict)
        return self.output_model(**processed_map)


def update_nested_data(key: str, old_data: list, new_data: list) -> list:
    """Updates dict information nested inside a list if the key values match"""
    lookup = {x[key]: x for x in old_data}
    lookup.update({x[key]: x for x in new_data})
    return list(lookup.values())
