class Student:
    def __init__(self, name):
        self.name = name
    def school(self):
        return (f"welcome to school {self.name}")

s1 = Student("Aigul")
s2 = Student("Arslan")

print(s1.school())
print(s2.school())
