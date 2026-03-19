import os

# create directories
os.makedirs("test_dir/sub_dir", exist_ok=True)
print("Directories created.")

# list files and folders
print("Current directory files:")
print(os.listdir())

# show current working directory
print("Current path:", os.getcwd())


os.makedirs("test_folder", exist_ok=True)
print("Folder created")

# list files
items = os.listdir(".")
print("\nFiles and folders:")
for item in items:
    print(f"  {item}")

txt_files = [f for f in os.listdir(".") if f.endswith(".txt")]
print(f"\n.txt files: {txt_files}")