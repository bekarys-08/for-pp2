def sum_all(*numbers):
    total = 0
    for n in numbers:
        total += n
    return total

print("Sum:", sum_all(1, 2, 3, 4))

def user_info(**info):
    for key, value in info.items():
        print(f"{key}: {value}")

user_info(name="Aigul", age=18, city="Almaty")
