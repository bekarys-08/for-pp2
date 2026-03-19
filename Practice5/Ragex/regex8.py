import re
a=input()
b=re.findall(r'[a-zA-Z]',a)

result = ' '.join([x.upper() for x in b])
print(result)
