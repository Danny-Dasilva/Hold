from abc import ABC, abstractmethod
from typing import Type, Union, Optional, List

from glom import glom, Coalesce, merge
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

    def merge(self, value, input_dict: dict):
        keys, search = value
        if isinstance(keys, list):
            return [
                r for val in keys for r in glom(input_dict, (val, search), default=None)
            ]

    def process_map(self, map_dict: dict, input_dict: dict):
        return {k: self.process_map_value(v, input_dict) for k, v in map_dict.items()}

    def process_map_value(self, value, input_dict: dict):
        if isinstance(value, str):
            return glom(input_dict, value, default=None)
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


from glom import flatten


def merge(input_dict, filt_keys):
    # res = sum(glom())
    res = flatten([glom(input_dict, i) for i in filt_keys])
    return res


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


rc_line_items = {
    "line_items": {
        "physical_items": [
            {
                "id": "e0cf6d1d-9d27-4c0e-89ec-afb5d38b9d9d",
                "parent_id": False,
                "variant_id": 84,
                "product_id": 116,
                "sku": "085423",
                "name": "1 time and Sub GNC Glucosamine Sulfate 500 mg",
                "url": "https://recharge-cameo-dev-1.mybigcommerce.com/gnc-glucosamine-sulfate-500-mg/",
                "quantity": 1,
                "taxable": False,
                "image_url": "https://cdn11.bigcommerce.com/s-ezugzr2hlz/products/116/images/377/2__23615.1612461887.220.290.png?c=1",
                "discounts": [{"id": 1, "discounted_amount": 7.64}],
                "coupons": [],
                "discount_amount": 0,
                "coupon_amount": 0,
                "list_price": 15,
                "sale_price": 15,
                "extended_list_price": 15,
                "extended_sale_price": 15,
                "is_require_shipping": False,
                "is_mutable": False,
            },
            {
                "id": "702c702a-3821-40ca-83b1-e41d33ae1bcd",
                "parent_id": False,
                "variant_id": 83,
                "product_id": 115,
                "sku": "130622",
                "name": "1X+Sub GNC SAM-e 400 MG.",
                "url": "https://recharge-cameo-dev-1.mybigcommerce.com/gnc-sam-e-400-mg/",
                "quantity": 1,
                "taxable": False,
                "image_url": "https://cdn11.bigcommerce.com/s-ezugzr2hlz/products/115/images/376/1__44321.1612461774.220.290.png?c=1",
                "discounts": [
                    {"id": 1, "discounted_amount": 3.05},
                    {"id": 7, "discounted_amount": 4},
                ],
                "coupons": [],
                "discount_amount": 4,
                "coupon_amount": 0,
                "list_price": 10,
                "sale_price": 6,
                "extended_list_price": 10,
                "extended_sale_price": 6,
                "is_require_shipping": True,
                "is_mutable": True,
            },
            {
                "id": "4cccd760-e0c2-4d98-90f3-e871f3bf619d",
                "parent_id": False,
                "variant_id": 87,
                "product_id": 119,
                "sku": "721312",
                "name": "1x Hydroslide Edge Jr Wakeboard",
                "url": "https://recharge-cameo-dev-1.mybigcommerce.com/1x-hydroslide-edge-jr-wakeboard/",
                "quantity": 1,
                "taxable": True,
                "image_url": "https://cdn11.bigcommerce.com/s-ezugzr2hlz/products/119/images/380/wb__57800.1612483498.220.290.png?c=1",
                "discounts": [{"id": 1, "discounted_amount": 101.81}],
                "coupons": [],
                "discount_amount": 0,
                "coupon_amount": 0,
                "list_price": 199.99,
                "sale_price": 199.99,
                "extended_list_price": 199.99,
                "extended_sale_price": 199.99,
                "is_require_shipping": True,
                "is_mutable": True,
            },
        ],
        "digital_items": [
            {
                "id": "4cccd760-e0c2-4d98-90f3-e871f3bf619d",
                "parent_id": False,
                "variant_id": 87,
                "product_id": 119,
                "sku": "721312",
                "name": "1x Hydroslide Edge Jr Wakeboard",
                "url": "https://recharge-cameo-dev-1.mybigcommerce.com/1x-hydroslide-edge-jr-wakeboard/",
                "quantity": 1,
                "taxable": True,
                "image_url": "nnnnnnnnnnnnnnnnnnnn",
                "discounts": [{"id": 1, "discounted_amount": 101.81}],
                "coupons": [],
                "discount_amount": 0,
                "coupon_amount": 0,
                "list_price": 199.99,
                "sale_price": 199.99,
                "extended_list_price": 199.99,
                "extended_sale_price": 199.99,
                "is_require_shipping": True,
                "is_mutable": True,
            }
        ],
        "gift_certificates": [],
        "custom_items": [],
    }
}
print("Original:")
pprint(rc_line_items)
from typing import Optional
from pydantic import BaseModel, PrivateAttr


class RCItems(MappedModel):
    product_id: Optional[int]
    quantity: Optional[int]
    requires_shipping: Optional[bool]
    taxable: Optional[bool]
    variant_id: Optional[int]
    price: Optional[float]
    discounts: Optional[list]

    @property
    def map(self):
        pass

    @property
    def output_model(self):
        pass

    @property
    def summed_discounts(self):
        return sum([val.get("discounted_amount", []) for val in self.discounts])


class RechargeLineItems(MappedModel):
    physical_items: List[RCItems]

    @property
    def map(self):
        map_dict = self.default_map(exclude={"physical_items"})
        # map_dict["test"] = parse_obj_as(List[Address], self.test)
        return map_dict

    @property
    def summed_discounts(self):
        return sum([val.summed_discounts for val in self.physical_items])

    @property
    def output_model(self) -> property:
        return property


def my_sum(*integers):
    result = 0
    for x in integers:
        result += x
    return result


print(my_sum(1, 2, 3))


class BCLineItems(MapDictToModel):
    output_model = RechargeLineItems

    map: dict = {
        "physical_items": (
            [
                "line_items.physical_items",
                "line_items.digital_items",
                "line_items.gift_certificates",
                "line_items.custom_items",
            ],
            [
                {
                    "productmy_collapsible_field_id": "product_id",
                    "quantity": "quantity",
                    "requires_shipping": "is_require_shipping",
                    "taxable": "taxable",
                    "variant_id": "variant_id",
                    "price": "list_price",
                    "discounts": (
                        "discounts",
                        [
                            {
                                "discounted_amount": "discounted_amount",
                            }
                        ],
                    ),
                }
            ],
        ),
    }


print("Updated:")

# r = BCLineItems(rc_line_items)
# pprint(r.mapped.dict())


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
    "items2": {
        "identical": "second value to be combined"
        },
}


class APydanticModel(BM):
    my_pydantic_field: int
    my_nested_fields: list
    my_collapsible_field: list

        key: ("lookup.value", [{"nested_key", "nested_key_lookup"}])

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




my_pydantic_model = MyClass(input_dict).mapped

print(my_pydantic_model.my_pydantic_field)
print(my_pydantic_model.my_nested_fields)
print(my_pydantic_model.my_collapsible_field)
# returns 7
# data = {'a': {'b': {'c': 'd'}}}

# print(glom(data, 'a.b.c'))
