"""
Tests for the fine calculation.
Rule: fine = number of late days x Rs 5.  A book returned on or before the due date has no fine.

Each test issues a book, moves its due date back by N days (to pretend the book is late),
returns the book and checks the stored fine.  It uses a temporary database, so your real data is safe.
Run:  python test_fine.py
"""
import os, sqlite3, sys, tempfile
from datetime import date, timedelta

sys.path.insert(0, os.getcwd())
import app as A

A.DB_PATH = os.path.join(tempfile.mkdtemp(), "fine_test.db")
A.init_db()
c = A.app.test_client()
c.post("/login", data={"username": "admin", "password": "admin123"})
c.post("/members/add", data={"name": "Test Student", "email": "t@example.com", "phone": "", "member_type": "Student"})

def db():
    d = sqlite3.connect(A.DB_PATH)
    d.row_factory = sqlite3.Row
    return d

def run_case(days_late):
    """Issue book 1, make it `days_late` days late (negative = not yet due), return it, give the stored fine."""
    c.post("/issue", data={"book_id": "1", "member_id": "1"})
    d = db()
    issue_id = d.execute("SELECT MAX(issue_id) FROM issue_records").fetchone()[0]
    due = date.today() - timedelta(days=days_late)
    d.execute("UPDATE issue_records SET due_date=? WHERE issue_id=?", (str(due), issue_id))
    d.commit()
    c.post(f"/return/{issue_id}")
    fine = d.execute("SELECT fine_amount FROM issue_records WHERE issue_id=?", (issue_id,)).fetchone()[0]
    d.close()
    return fine, issue_id

passed = 0
def check(name, actual, expected, money=True):
    global passed
    good = actual == expected
    unit = "Rs " if money else ""
    print(("PASS " if good else "FAIL ") + f"{name}: expected {unit}{expected}, got {unit}{actual}")
    if not good:
        sys.exit(1)
    passed += 1

# (late days, expected fine, description)
cases = [
    (-5, 0, "returned 5 days before the due date"),
    (0, 0, "returned exactly on the due date"),
    (1, 5, "1 day late"),
    (2, 10, "2 days late"),
    (4, 20, "4 days late"),
    (7, 35, "7 days late"),
    (10, 50, "10 days late"),
    (30, 150, "30 days late"),
]
for days, expected, text in cases:
    fine, _ = run_case(days)
    check(text, fine, expected)

# the fine rate comes from one constant
A.FINE_PER_DAY = 10
fine, _ = run_case(3)
check("3 days late when the rate is changed to Rs 10", fine, 30)
A.FINE_PER_DAY = 5

# returning the same record twice must not change the fine
fine, issue_id = run_case(4)
c.post(f"/return/{issue_id}")
d = db()
check("fine unchanged after a second return click", d.execute("SELECT fine_amount FROM issue_records WHERE issue_id=?", (issue_id,)).fetchone()[0], 20)

# copies must be back to the full count after every return
check("available copies back to total", d.execute("SELECT available_copies FROM books WHERE book_id=1").fetchone()[0],
      d.execute("SELECT total_copies FROM books WHERE book_id=1").fetchone()[0], money=False)

# a late book that is not returned yet appears on the overdue report with the right fine
c.post("/issue", data={"book_id": "2", "member_id": "1"})
iid = d.execute("SELECT MAX(issue_id) FROM issue_records").fetchone()[0]
d.execute("UPDATE issue_records SET due_date=? WHERE issue_id=?", (str(date.today() - timedelta(days=6)), iid))
d.commit()
page = c.get("/overdue").data
check("overdue report shows Rs 30 for 6 days late", b"Rs 30" in page, True, money=False)
check("overdue report shows total pending fine Rs 30", b"<b>Rs 30</b>" in page, True, money=False)

print(f"ALL FINE TESTS PASSED ({passed} checks)")
