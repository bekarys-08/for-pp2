students={
100:'marat',
90:'adina',
85:'maksat'
}

gpa={
100:4.0,
90:3.67,
85:3.33
}

for grade in students:
    score=gpa[grade]
    name=students[grade]
    print(name,score)