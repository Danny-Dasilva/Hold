# # initializing dictionary
# test_dict = {"Gfg" : [1, 2], "is" : [3, 4], "best" : [5]}
  
# # printing original dictionary
# print("The original dictionary is : " + str(test_dict))
# filt_keys = ["Gfg", "is"]
# # Concatenating dictionary value lists
# # Using sum() + values()
# res = sum(map(test_dict.get, filt_keys), [])
  
# # printing result 
# print("The Concatenated list values are : " + str(res))


target = [
            {
                'user_id': 198,
                'id': 504508,
                'first_name': 'John',
                'last_name': 'Doe',
                'active': True,
                'email_address': 'jd@test.com',
                'new_orders': False,
                'addresses': [
                    {
                        'location': 'home',
                        'address': 300,
                        'street': 'Fulton Rd.'
                    }
                ]
            },
            {
                'user_id': 209,
                'id': 504508,
                'first_name': 'Jane',
                'last_name': 'Doe',
                'active': True,
                'email_address': 'jd@test.com',
                'new_orders': True,
                'addresses2': [
                    {
                        'location': 'home',
                        'address': 251,
                        'street': 'Maverick Dr.'
                    },
                    {
                        'location': 'work',
                        'address': 333,
                        'street':  'Fulton Cir.'
                    },
                ],
                'addresses': [
                    {
                        'location': 'home',
                        'address': 251,
                        'street': 'Maverick Dr.'
                    },
                    {
                        'location': 'work',
                        'address': 4532,
                        'street':  'Fulton Cir.'
                    },
                ]
            },
        ]


from glom import glom, Flatten

t = glom(target,  (['addresses', 'addresses2'], Flatten(),  [{'address': 'address'}]))

from pprint import pprint
pprint(t)