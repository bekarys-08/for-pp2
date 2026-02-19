students = [
    ("Aigul", 90),
    ("Arslan", 85),
    ("Bekarys", 92)
]

sorted_students = sorted(students, key=lambda x: x[1], reverse=True)

print("Sorted by score:", sorted_students)
