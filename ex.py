
l = []
product_data = ["aaa", "bbb"]
for product in product_data:
    try:
        product = int(product)
    except:
        print("erre")
        pass
    l.append(product)

print(l)