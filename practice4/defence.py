import json
import math
a='{"len":17,"eni":5}'
b=json.loads(a)
perimetr=((b["len"]+b["eni"])*2)
d=math.ceil(perimetr/3)

result='{"square":500}'
result_load=json.loads(result)
result_load["value"]=d
new_dumps=json.dumps(result_load)
print(new_dumps)