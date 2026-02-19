class Person:
    def __init__(self, name):
        self.name = name

class Student(Person):
    def __init__(self, name, grade):
        super().__init__(name)
        self.grade = grade

s1 = Student("Aigul", "A")

print(s1.name)
print(s1.grade)
