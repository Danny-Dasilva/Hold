
def some_func():
    return [1, 2, 3]
result = (r for i in range(10000) for r in some_func())

r = list(result)