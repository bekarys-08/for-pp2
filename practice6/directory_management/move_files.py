import shutil
import os

# create directory
os.makedirs("storage", exist_ok=True)

# move file
if os.path.exists("sample.txt"):
    shutil.move("sample.txt", "storage/sample.txt")
    print("File moved to storage folder")

# copy file
shutil.copy("storage/sample.txt", "storage/sample_copy.txt")
print("File copied inside storage")

os.makedirs("source", exist_ok=True)
os.makedirs("destination", exist_ok=True)

with open("source/test.txt", "w") as f:
    f.write("test content")

shutil.move("source/test.txt", "destination/test.txt")
print("File moved")
