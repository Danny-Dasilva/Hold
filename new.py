from abc import ABC, abstractmethod
from typing import Type, Union, Optional, List

from glom import glom, Coalesce
from pprint import pprint

# Installed Packages
from pydantic import BaseModel as BM
from pydantic import validator
from pydantic import parse_obj_as


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


class _MappingMixinBase(ABC):
    @property
    @abstractmethod
    def output_model(self) -> DefaultBaseModel:
        pass

    @property
    @abstractmethod
    def map(self):
        pass

    def process_map(self, map_dict: dict, input_dict: dict):
        return {k: self.process_map_value(v, input_dict) for k, v in map_dict.items()}

    def process_map_value(self, value, input_dict: dict):
        if isinstance(value, str):
            return glom(input_dict, value, default=None)
        if isinstance(value, tuple):
            return glom(input_dict, value, default=None)
        if isinstance(value, dict):
            return self.process_map(value, input_dict)
        if isinstance(value, list):
            return [self.process_map_value(v, input_dict) for v in value]
        if callable(value):
            return value(input_dict)


def list_class(input_dict, value, Model):
    obj = glom(input_dict, value, default=None)
    nested_class = parse_obj_as(List[Model], obj)
    return nested_class


class MappedModel(DefaultBaseModel, _MappingMixinBase, ABC):
    @property
    def mapped(self):
        input_dict = self.dict()
        processed_map = self.process_map(self.map, input_dict)
        return self.output_model(**processed_map)

    def default_map(self, exclude: Union[set, dict] = None):
        input_dict = self.dict(exclude=exclude)
        return {k: k for k in input_dict.keys()}


class MapDictToModel(_MappingMixinBase, ABC):
    input_dict: dict = None

    def __init__(self, input_dict: dict, *args, **kwargs):
        self.input_dict = input_dict
        super().__init__(*args, **kwargs)

    @property
    def mapped(self):
        processed_map = self.process_map(self.map, self.input_dict)
        return self.output_model(**processed_map)


v2 = {
    "items": {
        "quantity": 7,
        "prices": "1.00",
        "addresses": {"city": "BOca Raon", "state": "FLORIDA "},
        "test": [
            {"city": "BOca Raon", "state": "FLORIDA "},
            {"city": "Maimi", "state": "FLORIDA "},
        ],
        "nested": [
            {
                "ex": {
                    "discounts": [
                        {"id": 3, "discount": 3.05},
                        {"id": 4, "discount": 4},
                    ]
                }
            },
            {
                "ex": {
                    "discounts": [
                        {"id": 3, "discount": 3.05},
                        {"id": 4, "discount": 4},
                    ]
                },
            },
        ],
    },
}
print("Original:")
pprint(v2,)




class Nested(MappedModel):
    city: list
    price: str

    @validator("uuid", always=True)
    def uuid_to_str(cls, val):
        if not val:
            return 0
        if getattr(val, "hex", None):
            return val.hex
        return val


class Address(MappedModel):
    city: str
    state: str

    @property
    def map(self):
        map_dict = self.default_map(exclue={"test"})
        map_dict["test"] = parse_obj_as(List[Address], self.test)
        return map_dict

    @property
    def output_model(self) -> property:
        return property


class RechargeLineItems(MappedModel):
    price: float
    opts: Optional[float] = None
    test: list = None
    address: Address
    nested: list

    # missing map and output model
    @property
    def map(self):
        map_dict = self.default_map(exclude={"test"})
        map_dict["test"] = parse_obj_as(List[Address], self.test)
        return map_dict

    @property
    def output_model(self) -> property:
        return property


class LineItems(MapDictToModel):
    output_model = RechargeLineItems

    map: dict = {
        "price": "items.prices",
        "address": "items.addresses",
        "test": (
            "items.test",
            [
                {
                    "city": Coalesce("city", default=""),
                    "state": Coalesce("city", default=""),
                }
            ],
        ),
        "nested": (
            "items.nested",
            [
                {
                    "test": (
                        "ex.discounts",
                        [
                            {
                                "city": Coalesce("id", default=""),
                                "state": Coalesce("discounted_amount", default=""),
                            }
                        ],
                    )
                }
            ],
        ),
    }


print("Updated:")
r = LineItems(v2)
pprint(r.mapped.dict())
