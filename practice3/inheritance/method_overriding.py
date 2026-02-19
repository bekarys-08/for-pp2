class Person:
    def speak(self):
        print("Person speaks")

class Student(Person):
    def speak(self):
        print("Student speaks")

p = Person()
s = Student()

p.speak()
s.speak()
