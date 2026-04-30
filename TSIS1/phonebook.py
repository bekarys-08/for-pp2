import csv
import json
import os
import psycopg2
from connect import get_connection


def print_contacts(rows):
    if not rows:
        print("  (no contacts found)")
        return
    print("-" * 65)
    for row in rows:
        cid, first, last, email, birthday, group = row
        full = f"{first or ''} {last or ''}".strip()
        print(f"  [{cid}] {full}")
        print(f"       Email   : {email or '-'}")
        print(f"       Birthday: {birthday or '-'}")
        print(f"       Group   : {group or '-'}")
    print("-" * 65)


def print_contacts_with_phones(rows):
    if not rows:
        print("  (no contacts found)")
        return
    print("-" * 65)
    seen = set()
    for row in rows:
        cid, first, last, email, birthday, group, phone, ptype = row
        full = f"{first or ''} {last or ''}".strip()
        if cid not in seen:
            print(f"  [{cid}] {full}")
            print(f"       Email   : {email or '-'}")
            print(f"       Birthday: {birthday or '-'}")
            print(f"       Group   : {group or '-'}")
            seen.add(cid)
        if phone:
            print(f"       Phone   : {phone}  ({ptype or '?'})")
    print("-" * 65)


def setup_schema():
    # FIX 1: use relative path instead of hardcoded Windows path
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    conn = get_connection()
    cur = conn.cursor()
    try:
        with open(schema_path, "r") as f:
            cur.execute(f.read())
        conn.commit()
        print("Schema applied successfully.")

        # Also apply procedures
        proc_path = os.path.join(os.path.dirname(__file__), "procedures.sql")
        if os.path.exists(proc_path):
            with open(proc_path, "r") as f:
                cur.execute(f.read())
            conn.commit()
            print("Procedures applied successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error applying schema: {e}")
    finally:
        cur.close()
        conn.close()


def add_contact():
    print("\n--- Add New Contact ---")
    first = input("First name: ").strip()
    if not first:
        print("First name cannot be empty.")
        return
    last  = input("Last name (leave blank to skip): ").strip() or None
    email    = input("Email (leave blank to skip): ").strip() or None
    birthday = input("Birthday YYYY-MM-DD (leave blank to skip): ").strip() or None

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name FROM groups ORDER BY id")
        groups = cur.fetchall()
        print("Groups:")
        for g in groups:
            print(f"  {g[0]}. {g[1]}")
        group_input = input("Group number (leave blank to skip): ").strip()
        group_id = int(group_input) if group_input.isdigit() else None

        phone_number = input("Main phone number (leave blank to skip): ").strip() or None

        cur.execute(
            """
            INSERT INTO contacts (first_name, last_name, phone_number, email, birthday, group_id)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
            """,
            (first, last, phone_number, email, birthday, group_id)
        )
        contact_id = cur.fetchone()[0]

        while True:
            phone = input("Extra phone (leave blank to stop): ").strip()
            if not phone:
                break
            ptype = input("Type (home / work / mobile): ").strip().lower()
            if ptype not in ("home", "work", "mobile"):
                ptype = "mobile"
            cur.execute(
                "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                (contact_id, phone, ptype)
            )

        conn.commit()
        print(f"Contact '{first} {last or ''}' added (id={contact_id}).")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()


def filter_by_group():
    print("\n--- Filter by Group ---")
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name FROM groups ORDER BY id")
        groups = cur.fetchall()
        print("Available groups:")
        for g in groups:
            print(f"  {g[0]}. {g[1]}")

        choice = input("Enter group number: ").strip()
        if not choice.isdigit():
            print("Invalid input.")
            return

        cur.execute(
            """
            SELECT c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            WHERE c.group_id = %s
            ORDER BY c.first_name, c.last_name
            """,
            (int(choice),)
        )
        rows = cur.fetchall()
        print_contacts(rows)
    finally:
        cur.close()
        conn.close()


def search_by_email():
    print("\n--- Search by Email ---")
    query = input("Enter email fragment (e.g. 'gmail'): ").strip()
    if not query:
        return

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            WHERE c.email ILIKE %s
            ORDER BY c.first_name, c.last_name
            """,
            (f"%{query}%",)
        )
        rows = cur.fetchall()
        print_contacts(rows)
    finally:
        cur.close()
        conn.close()


def list_sorted():
    print("\n--- List Contacts (Sorted) ---")
    print("Sort by: 1. Name  2. Birthday  3. Date Added")
    choice = input("Choice: ").strip()

    # FIX 2: use whitelist mapping to avoid SQL injection via f-string
    order_map = {
        "1": "c.first_name, c.last_name",
        "2": "c.birthday",
        "3": "c.created_at"
    }
    order_col = order_map.get(choice, "c.first_name, c.last_name")

    conn = get_connection()
    cur = conn.cursor()
    try:
        # Safe: order_col comes strictly from our own whitelist dict above
        cur.execute(
            f"""
            SELECT c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            ORDER BY {order_col} NULLS LAST
            """
        )
        rows = cur.fetchall()
        print_contacts(rows)
    finally:
        cur.close()
        conn.close()


def paginated_view():
    print("\n--- Paginated Contact List ---")
    PAGE_SIZE = 3
    page = 0
    conn = get_connection()
    cur = conn.cursor()
    try:
        while True:
            offset = page * PAGE_SIZE
            cur.execute("SELECT * FROM get_contacts_page(%s, %s)", (PAGE_SIZE, offset))
            rows = cur.fetchall()

            print(f"\n  --- Page {page + 1} ---")
            print_contacts(rows)

            # FIX 3: don't auto-decrement on empty page — just show message and ask
            if not rows:
                print("  No more contacts on this page.")

            # Build prompt based on position
            options = []
            if rows:
                options.append("[n]ext")
            if page > 0:
                options.append("[p]rev")
            options.append("[q]uit")

            cmd = input(f"  {' '.join(options)}: ").strip().lower()
            if cmd == "n" and rows:
                page += 1
            elif cmd == "p":
                if page > 0:
                    page -= 1
                else:
                    print("  Already on first page.")
            elif cmd == "q":
                break
    finally:
        cur.close()
        conn.close()


def search_all_fields():
    print("\n--- Search Contacts (name / email / phone) ---")
    query = input("Enter search term: ").strip()
    if not query:
        return
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM search_contacts(%s)", (query,))
        rows = cur.fetchall()
        print_contacts_with_phones(rows)
    finally:
        cur.close()
        conn.close()


def add_phone_to_contact():
    print("\n--- Add Phone to Existing Contact ---")
    first = input("Contact first name: ").strip()
    phone = input("Phone number: ").strip()
    ptype = input("Type (home / work / mobile): ").strip().lower()
    if ptype not in ("home", "work", "mobile"):
        ptype = "mobile"
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CALL add_phone(%s, %s, %s)", (first, phone, ptype))
        conn.commit()
        print("Phone added successfully.")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error: {e.pgerror}")
    finally:
        cur.close()
        conn.close()


def move_contact_to_group():
    print("\n--- Move Contact to Group ---")
    first = input("Contact first name: ").strip()
    group = input("Group name: ").strip()
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CALL move_to_group(%s, %s)", (first, group))
        conn.commit()
        print(f"Contact moved to group '{group}'.")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error: {e.pgerror}")
    finally:
        cur.close()
        conn.close()


def export_to_json():
    print("\n--- Export Contacts to JSON ---")
    filename = input("Output filename (default: contacts.json): ").strip()
    if not filename:
        filename = "contacts.json"
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT c.id, c.first_name, c.last_name, c.email,
                   TO_CHAR(c.birthday, 'YYYY-MM-DD'), g.name
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            ORDER BY c.id
            """
        )
        contacts = cur.fetchall()
        result = []
        for row in contacts:
            cid, first, last, email, birthday, group = row
            cur.execute("SELECT phone, type FROM phones WHERE contact_id = %s", (cid,))
            phones = [{"phone": p[0], "type": p[1]} for p in cur.fetchall()]
            result.append({
                "first_name": first,
                "last_name":  last,
                "email":      email,
                "birthday":   birthday,
                "group":      group,
                "phones":     phones
            })
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Exported {len(result)} contacts to '{filename}'.")
    finally:
        cur.close()
        conn.close()


def import_from_json():
    print("\n--- Import Contacts from JSON ---")
    filename = input("JSON filename (default: contacts.json): ").strip()
    if not filename:
        filename = "contacts.json"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return

    conn = get_connection()
    cur = conn.cursor()
    added = 0
    skipped = 0
    try:
        for item in data:
            first = item.get("first_name", "").strip()
            last  = item.get("last_name", "").strip() or None
            if not first:
                continue

            cur.execute(
                "SELECT id FROM contacts WHERE first_name ILIKE %s AND (last_name ILIKE %s OR last_name IS NULL)",
                (first, last or "")
            )
            existing = cur.fetchone()
            if existing:
                answer = input(f"  '{first} {last or ''}' already exists. [s]kip or [o]verwrite? ").strip().lower()
                if answer != "o":
                    skipped += 1
                    continue
                cur.execute("DELETE FROM contacts WHERE id = %s", (existing[0],))

            group_name = item.get("group")
            group_id = None
            if group_name:
                cur.execute("SELECT id FROM groups WHERE name ILIKE %s", (group_name,))
                g = cur.fetchone()
                if not g:
                    cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (group_name,))
                    g = cur.fetchone()
                group_id = g[0]

            # FIX 4: include phone_number in INSERT (was missing before)
            phones_list = item.get("phones", [])
            main_phone = phones_list[0].get("phone") if phones_list else None

            cur.execute(
                """
                INSERT INTO contacts (first_name, last_name, phone_number, email, birthday, group_id)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
                """,
                (first, last, main_phone, item.get("email"), item.get("birthday"), group_id)
            )
            contact_id = cur.fetchone()[0]

            for ph in phones_list:
                cur.execute(
                    "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                    (contact_id, ph.get("phone"), ph.get("type"))
                )
            added += 1

        conn.commit()
        print(f"Done. Added: {added}, Skipped: {skipped}.")
    except Exception as e:
        conn.rollback()
        print(f"Error during import: {e}")
    finally:
        cur.close()
        conn.close()


def import_from_csv():
    print("\n--- Import Contacts from CSV ---")
    filename = input("CSV filename (default: contacts.csv): ").strip()
    if not filename:
        filename = "contacts.csv"

    # FIX 5: use 'with' so file is always closed even on error
    try:
        f_handle = open(filename, newline="", encoding="utf-8")
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return

    conn = get_connection()
    cur = conn.cursor()
    added = 0
    skipped = 0
    try:
        with f_handle:
            reader = csv.DictReader(f_handle)
            for row in reader:
                first = (row.get("first_name") or row.get("name") or "").strip()
                last  = row.get("last_name", "").strip() or None
                phone = row.get("phone", "").strip()
                if not first:
                    continue

                phone_type = row.get("phone_type", "mobile").strip().lower()
                if phone_type not in ("home", "work", "mobile"):
                    phone_type = "mobile"
                email      = row.get("email", "").strip() or None
                birthday   = row.get("birthday", "").strip() or None
                group_name = row.get("group", "").strip() or None

                cur.execute("SELECT id FROM contacts WHERE first_name ILIKE %s", (first,))
                if cur.fetchone():
                    skipped += 1
                    continue

                group_id = None
                if group_name:
                    cur.execute("SELECT id FROM groups WHERE name ILIKE %s", (group_name,))
                    g = cur.fetchone()
                    if not g:
                        cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (group_name,))
                        g = cur.fetchone()
                    group_id = g[0]

                cur.execute(
                    """
                    INSERT INTO contacts (first_name, last_name, phone_number, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
                    """,
                    (first, last, phone or None, email, birthday, group_id)
                )
                contact_id = cur.fetchone()[0]
                if phone:
                    cur.execute(
                        "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                        (contact_id, phone, phone_type)
                    )
                added += 1

        conn.commit()
        print(f"CSV import done. Added: {added}, Skipped (duplicates): {skipped}.")
    except Exception as e:
        conn.rollback()
        print(f"Error during CSV import: {e}")
    finally:
        cur.close()
        conn.close()


def main():
    menu = {
        "1":  ("Add contact",                          add_contact),
        "2":  ("Filter by group",                      filter_by_group),
        "3":  ("Search by email",                      search_by_email),
        "4":  ("List contacts (sorted)",               list_sorted),
        "5":  ("Paginated view",                       paginated_view),
        "6":  ("Search all fields (name/email/phone)", search_all_fields),
        "7":  ("Add phone to contact",                 add_phone_to_contact),
        "8":  ("Move contact to group",                move_contact_to_group),
        "9":  ("Export to JSON",                       export_to_json),
        "10": ("Import from JSON",                     import_from_json),
        "11": ("Import from CSV",                      import_from_csv),
        "12": ("Apply / update schema",                setup_schema),
        "0":  ("Exit",                                 None),
    }

    print("\n========================================")
    print("   PhoneBook — Extended (TSIS 1)")
    print("========================================")

    while True:
        print()
        for key, (label, _) in menu.items():
            print(f"  {key:>2}. {label}")
        choice = input("\nYour choice: ").strip()

        if choice == "0":
            print("Goodbye!")
            break

        if choice not in menu:
            print("Unknown option, try again.")
            continue

        label, func = menu[choice]
        try:
            func()
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()