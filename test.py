from functools import wraps
from functools import wraps

users = [
    {"id": 1, "name": "Oleg", "age": 25},
    {"id": 2, "name": "Artem", "age": 30},
    {"id": 3, "name": "Ivan", "age": 20}
]

def f():
    adult_users = {
        "adult": list(map(lambda x: x["name"], filter(lambda x: x["age"] > 21, users))),
        "young": list(map(lambda x: x["name"], filter(lambda x: x["age"] <= 21, users)))
                   }
    return adult_users  

print(f())