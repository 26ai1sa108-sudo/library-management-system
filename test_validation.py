import os, sys, tempfile
sys.path.insert(0, os.getcwd())
import app as A
A.DB_PATH = os.path.join(tempfile.mkdtemp(), "t.db")
A.init_db()
c = A.app.test_client()
c.post("/login", data={"username": "admin", "password": "admin123"})  # log in first
def ok(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond: sys.exit(1)
def post(url, **d):
    return c.post(url, data=d, follow_redirects=True).data
def books_count():
    import sqlite3; return sqlite3.connect(A.DB_PATH).execute("SELECT COUNT(*) FROM books").fetchone()[0]
def members_count():
    import sqlite3; return sqlite3.connect(A.DB_PATH).execute("SELECT COUNT(*) FROM members").fetchone()[0]
b0 = books_count()
ok("empty title rejected", b"Title cannot be empty" in post("/books/add", title="  ", author="A", total_copies="1") and books_count() == b0)
ok("empty author rejected", b"Author cannot be empty" in post("/books/add", title="T", author="", total_copies="1"))
ok("copies=abc rejected (no crash)", b"whole number" in post("/books/add", title="T", author="A", total_copies="abc"))
ok("copies=0 rejected", b"whole number" in post("/books/add", title="T", author="A", total_copies="0"))
ok("copies=-3 rejected", b"whole number" in post("/books/add", title="T", author="A", total_copies="-3"))
ok("copies=101 rejected", b"whole number" in post("/books/add", title="T", author="A", total_copies="101"))
ok("bad isbn rejected", b"ISBN must have" in post("/books/add", title="T", author="A", total_copies="1", isbn="123"))
ok("nothing was saved by bad books", books_count() == b0)
ok("valid book accepted", b"Book added successfully" in post("/books/add", title="Good", author="Me", total_copies="2", isbn="978-0-13-235088-4") and books_count() == b0 + 1)
m0 = members_count()
ok("empty name rejected", b"Name cannot be empty" in post("/members/add", name=" ", email="", phone=""))
ok("bad email rejected", b"valid email" in post("/members/add", name="X", email="abc", phone=""))
ok("bad phone rejected", b"exactly 10 digits" in post("/members/add", name="X", email="", phone="123"))
ok("nothing saved by bad members", members_count() == m0)
ok("valid member accepted", b"registered successfully" in post("/members/add", name="Neha", email="neha@example.com", phone="9876543210"))
ok("duplicate email rejected", b"already exists" in post("/members/add", name="Other", email="NEHA@example.com", phone=""))
ok("member without email ok", b"registered successfully" in post("/members/add", name="NoMail", email="", phone=""))
ok("edit with bad copies rejected", b"whole number" in post("/books/1/edit", title="T", author="A", total_copies="x"))
ok("pages still load", all(c.get(p).status_code == 200 for p in ["/", "/books", "/members", "/issue", "/overdue"]))
print("ALL VALIDATION TESTS PASSED")
