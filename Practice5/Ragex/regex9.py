import re

text = input()

result = re.sub(r"([A-Z])", r" \1", text)

print(result.strip())