# write_files.py

with open("sample.txt", "w") as file:
    file.write("Python File Handling Example\n")
    file.write("Line 2: Learning Python\n")
    file.write("Line 3: File operations\n")

print("File created and data written.")


with open("output.txt", "w") as f:
    f.write("This is a new file\n")
    f.write("Second line\n")

with open("output.txt", "a") as f:
    f.write("Appended line\n")

print("File created and updated")