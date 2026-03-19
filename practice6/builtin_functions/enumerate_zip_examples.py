names = ["Alice", "Bob", "Charlie"]
scores = [85, 90, 78]

# enumerate example
for index, name in enumerate(names):
    print(index, name)

# zip example
for name, score in zip(names, scores):
    print(name, score)

# sorted example
nums = [5, 2, 9, 1]
print("Sorted numbers:", sorted(nums))

# type conversion
num = "10"
converted = int(num)
print(type(converted), converted)


fruits = ["apple", "banana", "cherry"]
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")

names = ["Alice", "Bob", "Charlie"]
ages = [25, 30, 35]
for name, age in zip(names, ages):
    print(f"{name}: {age}")

numbers = [5, 2, 8, 1, 9]
print(f"Sorted: {sorted(numbers)}")
