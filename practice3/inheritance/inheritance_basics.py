class Person:
    def __init__(self, name):
        self.name = name

    def greet(self):
        print(f"Hello, I am {self.name}")

class Student(Person):
    pass

s1 = Student("Aigul")
s1.greet()
