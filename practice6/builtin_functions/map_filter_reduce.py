from functools import reduce

numbers = [1, 2, 3, 4, 5, 6]

# map example
squared = list(map(lambda x: x**2, numbers))
print("Squared numbers:", squared)

# filter example
even_numbers = list(filter(lambda x: x % 2 == 0, numbers))
print("Even numbers:", even_numbers)

# reduce example
sum_numbers = reduce(lambda a, b: a + b, numbers)
print("Sum using reduce:", sum_numbers)


numbers = [1, 2, 3, 4, 5]

doubled = list(map(lambda x: x * 2, numbers))
print(f"Doubled: {doubled}")

even = list(filter(lambda x: x % 2 == 0, numbers))
print(f"Even: {even}")

total = reduce(lambda a, b: a + b, numbers)
print(f"Sum: {total}")