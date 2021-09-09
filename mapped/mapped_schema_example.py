from mapped_schema import IgnoreGlom
from typing import Optional

# Installed Packages
from pydantic import BaseModel

# ReCharge Adapter Local Files
from mapped_schema import MappedModel, MapDictToModel


my_json_data = {"store_hash": "11111"}


output_data = {
    "store_id": None,
    "platform": "BigCommerce",
    "store_hash": my_json_data["store_hash"],
}


















class OutputModel(BaseModel):

    store_id: Optional[int] = None
    platform: Optional[str] = None
    store_hash: Optional[str] = None


class ExampleInputModel(MappedModel):

    store_hash: Optional[str] = None

    @property
    def output_model(self):
        return OutputModel

    @property
    def map(self):
        return {
            "store_id": None,
            "platform":0.05,
            "store_hash": self.store_hash,
        }


model = ExampleInputModel(store_hash="11111").mapped
breakpoint()






my_json_data = {"store_hash": "11111"}

mapped_model = ExampleInputModel(**my_json_data)
breakpoint()





########## Map Dict to Model Example
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


class APydanticModel(BaseModel):
    my_pydantic_field: int
    my_nested_fields: list
    my_collapsible_field: list


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
breakpoint()
# # my_pydantic_model.my_pydantic_field
# #     result -> 7
# # my_pydantic_model.my_nested_fields
# #     result -> [{'my_list_val': 1, 'my_amount': 3.05}, {'my_list_val': 2, 'my_amount': 4}]
# # my_pydantic_model.my_collapsible_field
# #     result -> ['value to be combined', 'second value to be combined']





class ExampleIgnoreModel(MappedModel):

    store_hash: Optional[str] = None

    @property
    def output_model(self):
        return OutputModel

    @property
    def map(self):
        return {
            "store_id": None,
            "platform":0.05,
            "store_hash": IgnoreGlom("self.store.hash"),
        }


model = ExampleIgnoreModel(store_hash="22222").mapped
breakpoint()
