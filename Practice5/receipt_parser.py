import re
import json
with open(r"C:/Users/admin/Desktop/PP2/Practice5/raw.txt", encoding="utf-8") as f:
    text = f.read()

# Prices
prices = [float(p.replace(" ", "").replace(",", ".")) 
          for p in re.findall(r"\n([\d ]+,\d{2})\nСтоимость", text)]

# Product names
products = re.findall(r"\d+\.\n(.+)", text)

# Total
total_match = re.search(r"ИТОГО:\n([\d ]+,\d{2})", text)
total = total_match.group(1) if total_match else None

# Date and Time
datetime_match = re.search(r"Время:\s*(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2})", text)
datetime = datetime_match.group(1) if datetime_match else None

# Payment Method
payment_match = re.search(r"(Банковская карта)", text)
payment_method = payment_match.group(1) if payment_match else None

output = {
    "products": products,
    "prices": prices,
    "total": total,
    "datetime": datetime,
    "payment_method": payment_method
}

print(json.dumps(output, ensure_ascii=False, indent=4))
