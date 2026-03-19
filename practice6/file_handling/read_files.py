# read_files.py

with open("sample.txt", "r") as file:
    print("Using read():")
    print(file.read())

with open("sample.txt", "r") as file:
    print("Using readline():")
    print(file.readline())

with open("sample.txt", "r") as file:
    print("Using readlines():")
    lines = file.readlines()
    print(lines)


with open("sample.txt", "r") as f:
    content = f.read()
    print("Full content:")
    print(content)

with open("sample.txt", "r") as f:
    line = f.readline()
    print("\nFirst line:")
    print(line)

with open("sample.txt", "r") as f:
    lines = f.readlines()
    print("\nAll lines:")
    print(lines)