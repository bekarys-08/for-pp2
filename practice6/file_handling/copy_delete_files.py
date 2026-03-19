import shutil
import os

# append new line
with open("sample.txt", "a") as file:
    file.write("Line 4: Appended text\n")

print("Text appended.")

# copy file
shutil.copy("sample.txt", "backup_sample.txt")
print("File copied as backup_sample.txt")

# delete file safely
if os.path.exists("backup_sample.txt"):
    os.remove("backup_sample.txt")
    print("Backup file deleted.")


# copy file
shutil.copy("sample.txt", "backup.txt")
print("File copied")

if os.path.exists("backup.txt"):
    os.remove("backup.txt")
    print("File deleted")