import csv
import psycopg2
from config import DB_CONFIG
from connect import get_connection

# ==================== INSERT FROM CSV ====================
def insert_from_csv():
    filepath = r"C:\Users\10W030825\Desktop\for pp2\practice7\contacts.csv"
    conn = get_connection()
    cur = conn.cursor()
    with open(filepath, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute("""
                INSERT INTO phonebook (first_name, phone)
                VALUES (%s, %s)
                ON CONFLICT (phone) DO NOTHING;
            """, (row['first_name'], row['phone']))
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Contacts loaded from CSV")

# ==================== INSERT FROM CONSOLE ====================
def insert_from_console():
    name = input("Enter name: ")
    phone = input("Enter phone: ")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO phonebook (first_name, phone)
        VALUES (%s, %s)
        ON CONFLICT (phone) DO NOTHING;
    """, (name, phone))
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Contact added")

# ==================== SHOW ALL ====================
def show_all_contacts():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM phonebook;")
    rows = cur.fetchall()
    if rows:
        print("\n📋 All contacts:")
        for row in rows:
            print(f"  ID: {row[0]} | Name: {row[1]} | Phone: {row[2]}")
    else:
        print("📭 No contacts found")
    cur.close()
    conn.close()

# ==================== SEARCH ====================
def search_contacts():
    print("1 - by name | 2 - by phone")
    choice = input("Choice: ")
    conn = get_connection()
    cur = conn.cursor()
    if choice == "1":
        name = input("Enter name (or part of it): ")
        cur.execute("SELECT * FROM phonebook WHERE first_name ILIKE %s;", (f"%{name}%",))
    else:
        phone = input("Enter phone (or prefix): ")
        cur.execute("SELECT * FROM phonebook WHERE phone LIKE %s;", (f"{phone}%",))
    rows = cur.fetchall()
    if rows:
        for row in rows:
            print(f"  ID: {row[0]} | Name: {row[1]} | Phone: {row[2]}")
    else:
        print("📭 Nothing found")
    cur.close()
    conn.close()

# ==================== UPDATE ====================
def update_contact():
    phone = input("Enter phone of contact to update: ")
    print("1 - change name | 2 - change phone")
    choice = input("Choice: ")
    conn = get_connection()
    cur = conn.cursor()
    if choice == "1":
        new_name = input("New name: ")
        cur.execute("UPDATE phonebook SET first_name=%s WHERE phone=%s;", (new_name, phone))
    else:
        new_phone = input("New phone: ")
        cur.execute("UPDATE phonebook SET phone=%s WHERE phone=%s;", (new_phone, phone))
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Contact updated")

# ==================== DELETE ====================
def delete_contact():
    print("1 - by name | 2 - by phone")
    choice = input("Choice: ")
    conn = get_connection()
    cur = conn.cursor()
    if choice == "1":
        name = input("Enter name: ")
        cur.execute("DELETE FROM phonebook WHERE first_name=%s;", (name,))
    else:
        phone = input("Enter phone: ")
        cur.execute("DELETE FROM phonebook WHERE phone=%s;", (phone,))
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Contact deleted")

# ==================== MENU ====================
def main():
    while True:
        print("\n===== PhoneBook =====")
        print("1 - Load from CSV")
        print("2 - Add manually")
        print("3 - Show all contacts")
        print("4 - Search contact")
        print("5 - Update contact")
        print("6 - Delete contact")
        print("0 - Exit")
        choice = input("Choice: ")
        if choice == "1":
            insert_from_csv()
        elif choice == "2":
            insert_from_console()
        elif choice == "3":
            show_all_contacts()
        elif choice == "4":
            search_contacts()
        elif choice == "5":
            update_contact()
        elif choice == "6":
            delete_contact()
        elif choice == "0":
            break

if __name__ == "__main__":
    main()
