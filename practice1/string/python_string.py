print("Hello")
print('Hello')
#'hello' is the same as "hello".
#----------------------------------------
a = """Lorem ipsum dolor sit amet,
consectetur adipiscing elit,
sed do eiusmod tempor incididunt
ut labore et dolore magna aliqua."""
print(a)
#you can assign a multiline string to a variable by using three quotes:
#----------------------------------------
a = "Hello, World!"
print(a[1])
#Get the character at position 1 (remember that the first character has the position 0):
#----------------------------------------
for x in "banana":
  print(x)
#ince strings are arrays, we can loop through the characters in a string, with a for loop.
#----------------------------------------
a = "Hello, World!"
print(len(a))
#To get the length of a string, use the len() function.
#----------------------------------------
txt = "The best things in life are free!"
print("free" in txt)
#To check if a certain phrase or character is present in a string, we can use the keyword in.
#----------------------------------------
txt = "The best things in life are free!"
if "free" in txt:
  print("Yes, 'free' is present.")
#Use it in an if statement:
#----------------------------------------
txt = "The best things in life are free!"
print("expensive" not in txt)
#To check if a certain phrase or character is NOT present in a string, we can use the keyword not in.
#----------------------------------------
txt = "The best things in life are free!"
if "expensive" not in txt:
  print("No, 'expensive' is NOT present.")
#Use it in an if statement:
#----------------------------------------