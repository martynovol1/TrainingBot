from functools import wraps
from functools import wraps

def retry(n):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(n):
                try:
                    print("Начали")
                    result = func(*args, **kwargs)
                    print("Закончили")
                    return result
                except Exception as e:
                    print(f"Ошибка: попытка {i+1}")
                    if i == n - 1:
                        raise  # на последней попытке пробрасываем ошибку
        return wrapper
    return decorator
    

def gen(n):
    for i in range(0, n-1):
        yield i


def gen(numbers):
    for i in numbers:
        if i % 2 == 0:
            yield i


def gen(numbers):
    for i in numbers:
        yield i ** 2


def gen(numbers):
    for i in numbers:
        if i > 5:
            yield i * 2


def f():
    for i in range(3):
        print("yield", i)
        yield i

g = f()

print(next(g))
print(next(g))