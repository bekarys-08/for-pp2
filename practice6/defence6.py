
import os
from functools import reduce

os.makedirs("sales", exist_ok=True)

with open("sales/store1.txt", "w") as st :
    st.write("Phone,12\n")
    st.write("Charger,25\n")
    st.write("Case,30\n")
    st.write("Cable,40\n")

with open("sales/store2.txt", "w") as st:
    st.write("Phone,7\n")
    st.write("Charger,15\n")
    st.write("Case,20\n")
    st.write("Cable,18\n")

with open("sales/store3.txt", "w") as st:
    st.write("Phone,5\n")
    st.write("Charger,10\n")
    st.write("Case,14\n")
    st.write("Cable,9\n")
products = []

for fname in os.listdir("sales"):
    filepath = os.path.join("sales", fname)
    with open(filepath, "r") as x:
        for line in x:
            line = line.strip()
            if line:
                name, count = line.split(",")
                products.append((name, int(count)))

print(products)

quantities = [count for name, count in products]
names = [name for name, count in products]

total_records = len(products)
print(total_records)

total_count = sum(quantities)
print(total_count)

highest = max(quantities)
lowest = min(quantities)
print(highest)
print(lowest)

#плюсуем на два (map)
increase = list(map(lambda x: x + 2, quantities))
print(increase)

# товары которые проданы больше 10 (filter)
popular = list(filter(lambda x: x[1] > 10, products))
print(popular)

product_of_all = reduce(lambda a, b: a * b, quantities)
print(product_of_all)

# enumerate()  товар c индексом 
for index, (name, count) in enumerate(products, start=1):
    print(index, name, count)

# zip() —  имена и количества
zipped = list(zip(names, quantities))
print(zipped)

# sorted() — сортировка по количеству
sorted_products = sorted(products, key=lambda x: x[1], reverse=True)
print(sorted_products)


avg = round(total_count / total_records, 1)
popular_for_report = [(name, count) for name, count in sorted_products if count > 10]

with open("sales_result.txt", "w") as report:
    report.write("Total records: " + str(total_records) + "\n")
    report.write("Average quantity sold: " + str(avg) + "\n")
    report.write("Highest quantity sold: " + str(highest) + "\n")
    report.write("Lowest quantity sold: " + str(lowest) + "\n")
    report.write("\nPopular products:\n")
    for name, count in popular_for_report:
        report.write(name + " " + str(count) + "\n")
