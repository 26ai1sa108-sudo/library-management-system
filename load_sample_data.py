"""
Loads sample data into the Library Management System database.

It adds 10 books and 8 members (the three team members and five sample students).
Put this file in the same folder as app.py and run it once:

    python load_sample_data.py      (or double-click it)

It is safe to run again: books and members that already exist are skipped.
All emails and phone numbers below are made-up sample values.
"""
import sqlite3

import app as library_app

# (title, author, category, isbn, copies)
BOOKS = [
    ("Database System Concepts", "Silberschatz, Korth and Sudarshan", "DBMS", "9780078022159", 3),
    ("Introduction to Algorithms", "Cormen, Leiserson, Rivest and Stein", "Algorithms", "9780262033848", 2),
    ("Operating System Concepts", "Silberschatz, Galvin and Gagne", "Operating Systems", "9781119800361", 2),
    ("Computer Networks", "Andrew S. Tanenbaum", "Networks", "9780132126953", 3),
    ("Python Crash Course", "Eric Matthes", "Programming", "9781593279288", 4),
    ("Clean Code", "Robert C. Martin", "Software Engineering", "9780132350884", 2),
    ("The C Programming Language", "Kernighan and Ritchie", "Programming", "9780131103627", 3),
    ("Artificial Intelligence: A Modern Approach", "Russell and Norvig", "Artificial Intelligence", "9780136042594", 2),
    ("Design Patterns", "Gamma, Helm, Johnson and Vlissides", "Software Engineering", "9780201633610", 2),
    ("Software Engineering", "Ian Sommerville", "Software Engineering", "9780133943030", 3),
]

# (name, email, phone, member_type)
MEMBERS = [
    ("Saksham Seth", "saksham.seth@example.com", "9876500001", "Student"),
    ("Shubh Asati", "shubh.asati@example.com", "9876500002", "Student"),
    ("Rajkrishnapal Malviya", "rajkrishnapal.malviya@example.com", "9876500003", "Student"),
    ("Ananya Sharma", "ananya.sharma@example.com", "9876500004", "Student"),
    ("Rohit Verma", "rohit.verma@example.com", "9876500005", "Student"),
    ("Priya Singh", "priya.singh@example.com", "9876500006", "Student"),
    ("Aman Gupta", "aman.gupta@example.com", "9876500007", "Student"),
    ("Neha Jain", "neha.jain@example.com", "9876500008", "Student"),
]


def load():
    library_app.init_db()  # makes sure the tables exist
    db = sqlite3.connect(library_app.DB_PATH)

    # Remove the placeholder student from the first run, if nobody has used it
    placeholder = db.execute(
        "SELECT member_id FROM members WHERE name = 'Sample Student' AND email = 'student@example.com'"
    ).fetchone()
    if placeholder:
        used = db.execute(
            "SELECT COUNT(*) FROM issue_records WHERE member_id = ?", (placeholder[0],)
        ).fetchone()[0]
        if not used:
            db.execute("DELETE FROM members WHERE member_id = ?", (placeholder[0],))
            print("Removed the placeholder member 'Sample Student'.")

    added_books = 0
    for title, author, category, isbn, copies in BOOKS:
        if db.execute("SELECT 1 FROM books WHERE title = ?", (title,)).fetchone():
            continue
        db.execute(
            "INSERT INTO books (title, author, category, isbn, total_copies, available_copies)"
            " VALUES (?,?,?,?,?,?)",
            (title, author, category, isbn, copies, copies),
        )
        added_books += 1

    added_members = 0
    for name, email, phone, member_type in MEMBERS:
        if db.execute("SELECT 1 FROM members WHERE email = ?", (email,)).fetchone():
            continue
        db.execute(
            "INSERT INTO members (name, email, phone, member_type, join_date) VALUES (?,?,?,?,date('now'))",
            (name, email, phone, member_type),
        )
        added_members += 1

    db.commit()
    total_books = db.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    total_members = db.execute("SELECT COUNT(*) FROM members").fetchone()[0]
    db.close()

    print(f"Added {added_books} book(s) and {added_members} member(s).")
    print(f"The library now has {total_books} book(s) and {total_members} member(s).")
    return added_books, added_members


if __name__ == "__main__":
    load()
    try:
        input("Done. Press Enter to close this window...")
    except EOFError:
        pass
