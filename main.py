
from abc import ABC, abstractmethod
from typing import Type, Union, Optional, List

from glom import glom

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
        if isinstance(value, dict):
            return self.process_map(value, input_dict)
        if isinstance(value, list):
            return [self.process_map_value(v, input_dict) for v in value]
        if isinstance(value, tuple):
            print("here")
            func, search, model = value
            return func(input_dict, search, model)
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




v2 = {"line_items":
    
      {
        "quantity": 7,
        "prices": "1.00",
        "addresses": {"city": "BOca Raon",
                    "state": "FLORIDA "},
        "test": [{"city": "BOca Raon",
                    "state": "FLORIDA "},
                    {"city": "Maimi",
                    "state": "FLORIDA "}],
        "nested": [{"items_1": { "discounts": [
                        {
                            "id": 3,
                            "discounted_amount": 3.05
                        },
                        {
                            "id": 4,
                            "discounted_amount": 4
                        }
                    ]}
                    
                    },
                    {"items_2": { "discounts": [
                        {
                            "id": 3,
                            "discounted_amount": 3.05
                        },
                        {
                            "id": 4,
                            "discounted_amount": 4
                        }
                    ]}
                    
                    }]

      }
    ,}

checkouts = {"line_items":
    
      {
        "prices": "1.00",
        "addresses": {"city": "Grenaccres",
                    "state": "Ohie "},
        "test": [{"cities": "Boca",
                    "states": "FLORIDA "},
                    {"cities": "Maimi",
                    "states": "FLORIDA "}],
        "grams": 4536,
        "line_price": "7.00",
        "order_day_of_month": False,
        "order_day_of_week": False,
        "order_interval_frequency": 30,
        "order_interval_unit": "day",
        "order_interval_unit_type": "day",
        "original_price": "450.00",
        "product_id": 4313321766958,
        "product_type": "",
        "properties": False,
        "quantity": 7,
        "recurring_price": "1.00",
        "requires_shipping": False,
        "sku": "MILK-1",
        "taxable": False,
        "title": "Milk renamed",
        "variant_id": 30995615318062,
        "variant_title": "a / b",
        "vendor": "nemanjateststore"
      }
    }

class Nested(MappedModel):
    city: list
    state: str
    @property
    def map(self):
        map_dict = self.default_map(exclue={"test"})
        map_dict["test"] = parse_obj_as(List[Address], self.test)
        return map_dict
    @property
    def output_model(self) -> property:
        return property

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
    test: list
    address: Address
    nested: list 

    #missint map and output model
    @property
    def map(self):
        map_dict = self.default_map(exclue={"test"})
        map_dict["test"] = parse_obj_as(List[Address], self.test)
        return map_dict
    @property
    def output_model(self) -> property:
        return property
# class Cities(MapDictToModel):
#     output_model = Address
#     map: dict = {
#         "city": "cities",
#         "states": "states",
#     }
class LineItems(MapDictToModel):
    output_model = RechargeLineItems
    
    map: dict = {
        "price": "line_items.prices",
        "address": "line_items.addresses",
        "test": (list_class, "line_items.test", Address),
        "nested": (list_class, "line_items.nested", Nested)
    }


# r = list_class(v2, "line_items.test")
r = LineItems(v2)
print(r.mapped)


# users = [
#     {
#         "quantity": 8,
#         "price": "3.00",
#         "address": {"city": "Raon",
#                     "state": "US "},
#         "test": [{"city": "BOca Raon",
#                     "state": "US "},
#                     {"city": "MI",
#                     "state": "US "}],
#         "Ahhhhhhhhhhhhhhhhhhhhhhhhhhhhh": "non used value"
#       }, 
#     {
#         "quantity": 7,
#         "price": "1.00",
#         "address": {"city": "BOca Raon",
#                     "state": "FLORIDA "},
#         "test": [{"city": "BOca Raon",
#                     "state": "FLORIDA "},
#                     {"city": "Maimi",
#                     "state": "FLORIDA "}],
#       }
# ]

# m = parse_obj_as(List[RechargeLineItems], users)
# for item in m:
#     print(item.json())
# print(dict(m))