"""
Library Management System
Tech stack: Python (Flask) + SQLite
Team: Saksham Seth, Shubh Asati, Rajkrishnapal Malviya
MITS-DU Gwalior - Skills Development Micro Project

Run:  python app.py   (or double-click run.bat on Windows)
Open: http://127.0.0.1:5000
"""
import os
import sqlite3
import threading
import webbrowser
from datetime import date, timedelta

from flask import Flask, flash, g, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "library-micro-project"

# The database file is created next to app.py
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "library.db")

LOAN_DAYS = 14      # number of days a book can be kept
FINE_PER_DAY = 5    # fine in Rs per late day


# ---------------------------------------------------------------- database
def get_db():
    """One database connection per request."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Creates the tables from the ER diagram: books, members, issue_records."""
    db = sqlite3.connect(DB_PATH)
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS books (
            book_id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title            TEXT NOT NULL,
            author           TEXT NOT NULL,
            category         TEXT,
            isbn             TEXT,
            total_copies     INTEGER NOT NULL DEFAULT 1,
            available_copies INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS members (
            member_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            email       TEXT,
            phone       TEXT,
            member_type TEXT NOT NULL DEFAULT 'Student',
            join_date   TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS issue_records (
            issue_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id     INTEGER NOT NULL REFERENCES books(book_id),
            member_id   INTEGER NOT NULL REFERENCES members(member_id),
            issue_date  TEXT NOT NULL,
            due_date    TEXT NOT NULL,
            return_date TEXT,
            fine_amount INTEGER NOT NULL DEFAULT 0
        );
        """
    )
    # Add some sample data on the first run
    if db.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 0:
        db.executemany(
            "INSERT INTO books (title, author, category, isbn, total_copies, available_copies)"
            " VALUES (?,?,?,?,?,?)",
            [
                ("Database System Concepts", "Silberschatz", "DBMS", "9780078022159", 3, 3),
                ("Introduction to Algorithms", "Cormen", "Algorithms", "9780262033848", 2, 2),
                ("Operating System Concepts", "Galvin", "OS", "9781119800361", 2, 2),
            ],
        )
        db.execute(
            "INSERT INTO members (name, email, phone, member_type, join_date) VALUES (?,?,?,?,?)",
            ("Sample Student", "student@example.com", "9999999999", "Student", str(date.today())),
        )
    db.commit()
    db.close()


# --------------------------------------------------------------- dashboard
@app.route("/")
def index():
    db = get_db()
    stats = {
        "books": db.execute("SELECT COUNT(*) FROM books").fetchone()[0],
        "members": db.execute("SELECT COUNT(*) FROM members").fetchone()[0],
        "issued": db.execute(
            "SELECT COUNT(*) FROM issue_records WHERE return_date IS NULL"
        ).fetchone()[0],
        "overdue": db.execute(
            "SELECT COUNT(*) FROM issue_records WHERE return_date IS NULL AND due_date < ?",
            (str(date.today()),),
        ).fetchone()[0],
    }
    return render_template("index.html", stats=stats)


# ------------------------------------------------------------------- books
@app.route("/books")
def books():
    q = request.args.get("q", "").strip()
    db = get_db()
    if q:
        like = f"%{q}%"
        rows = db.execute(
            "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR category LIKE ?"
            " ORDER BY title",
            (like, like, like),
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM books ORDER BY title").fetchall()
    return render_template("books.html", books=rows, q=q)


@app.route("/books/add", methods=["POST"])
def add_book():
    f = request.form
    copies = max(1, int(f.get("total_copies") or 1))
    db = get_db()
    db.execute(
        "INSERT INTO books (title, author, category, isbn, total_copies, available_copies)"
        " VALUES (?,?,?,?,?,?)",
        (f["title"].strip(), f["author"].strip(), f.get("category", "").strip(),
         f.get("isbn", "").strip(), copies, copies),
    )
    db.commit()
    flash("Book added successfully.", "ok")
    return redirect(url_for("books"))


@app.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
def edit_book(book_id):
    db = get_db()
    book = db.execute("SELECT * FROM books WHERE book_id = ?", (book_id,)).fetchone()
    if book is None:
        flash("Book not found.", "err")
        return redirect(url_for("books"))
    if request.method == "POST":
        f = request.form
        new_total = max(1, int(f.get("total_copies") or 1))
        issued_now = book["total_copies"] - book["available_copies"]
        if new_total < issued_now:
            flash(f"Total copies cannot be less than {issued_now}, because that many are currently issued.", "err")
            return redirect(url_for("edit_book", book_id=book_id))
        db.execute(
            "UPDATE books SET title=?, author=?, category=?, isbn=?, total_copies=?,"
            " available_copies=? WHERE book_id=?",
            (f["title"].strip(), f["author"].strip(), f.get("category", "").strip(),
             f.get("isbn", "").strip(), new_total, new_total - issued_now, book_id),
        )
        db.commit()
        flash("Book updated successfully.", "ok")
        return redirect(url_for("books"))
    return render_template("edit_book.html", book=book)


@app.route("/books/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    db = get_db()
    issued = db.execute(
        "SELECT COUNT(*) FROM issue_records WHERE book_id=? AND return_date IS NULL", (book_id,)
    ).fetchone()[0]
    if issued:
        flash("This book is currently issued and cannot be deleted.", "err")
    else:
        db.execute("DELETE FROM issue_records WHERE book_id=?", (book_id,))
        db.execute("DELETE FROM books WHERE book_id=?", (book_id,))
        db.commit()
        flash("Book deleted successfully.", "ok")
    return redirect(url_for("books"))


# ----------------------------------------------------------------- members
@app.route("/members")
def members():
    rows = get_db().execute("SELECT * FROM members ORDER BY name").fetchall()
    return render_template("members.html", members=rows)


@app.route("/members/add", methods=["POST"])
def add_member():
    f = request.form
    db = get_db()
    db.execute(
        "INSERT INTO members (name, email, phone, member_type, join_date) VALUES (?,?,?,?,?)",
        (f["name"].strip(), f.get("email", "").strip(), f.get("phone", "").strip(),
         f.get("member_type", "Student"), str(date.today())),
    )
    db.commit()
    flash("Member registered successfully.", "ok")
    return redirect(url_for("members"))


@app.route("/members/<int:member_id>/delete", methods=["POST"])
def delete_member(member_id):
    db = get_db()
    issued = db.execute(
        "SELECT COUNT(*) FROM issue_records WHERE member_id=? AND return_date IS NULL",
        (member_id,),
    ).fetchone()[0]
    if issued:
        flash("This member still has issued books and cannot be deleted.", "err")
    else:
        db.execute("DELETE FROM issue_records WHERE member_id=?", (member_id,))
        db.execute("DELETE FROM members WHERE member_id=?", (member_id,))
        db.commit()
        flash("Member deleted successfully.", "ok")
    return redirect(url_for("members"))


# ----------------------------------------------------------- issue / return
@app.route("/issue")
def issue_page():
    db = get_db()
    available_books = db.execute(
        "SELECT * FROM books WHERE available_copies > 0 ORDER BY title"
    ).fetchall()
    all_members = db.execute("SELECT * FROM members ORDER BY name").fetchall()
    current = db.execute(
        "SELECT i.*, b.title, m.name FROM issue_records i"
        " JOIN books b ON b.book_id = i.book_id JOIN members m ON m.member_id = i.member_id"
        " WHERE i.return_date IS NULL ORDER BY i.due_date"
    ).fetchall()
    history = db.execute(
        "SELECT i.*, b.title, m.name FROM issue_records i"
        " JOIN books b ON b.book_id = i.book_id JOIN members m ON m.member_id = i.member_id"
        " WHERE i.return_date IS NOT NULL ORDER BY i.return_date DESC, i.issue_id DESC LIMIT 20"
    ).fetchall()
    today = str(date.today())
    current = [
        {**dict(r), "late_days": max(0, (date.today() - date.fromisoformat(r["due_date"])).days)}
        for r in current
    ]
    for r in current:
        r["fine_now"] = r["late_days"] * FINE_PER_DAY
    return render_template(
        "issue.html", books=available_books, members=all_members, current=current,
        history=history, today=today, loan_days=LOAN_DAYS, fine_per_day=FINE_PER_DAY,
    )


@app.route("/issue", methods=["POST"])
def issue_book():
    book_id = int(request.form["book_id"])
    member_id = int(request.form["member_id"])
    db = get_db()
    book = db.execute("SELECT * FROM books WHERE book_id=?", (book_id,)).fetchone()
    if book is None or book["available_copies"] < 1:
        flash("This book is not available right now.", "err")
        return redirect(url_for("issue_page"))
    already = db.execute(
        "SELECT COUNT(*) FROM issue_records WHERE book_id=? AND member_id=? AND return_date IS NULL",
        (book_id, member_id),
    ).fetchone()[0]
    if already:
        flash("This book is already issued to this member.", "err")
        return redirect(url_for("issue_page"))
    today = date.today()
    db.execute(
        "INSERT INTO issue_records (book_id, member_id, issue_date, due_date) VALUES (?,?,?,?)",
        (book_id, member_id, str(today), str(today + timedelta(days=LOAN_DAYS))),
    )
    db.execute("UPDATE books SET available_copies = available_copies - 1 WHERE book_id=?", (book_id,))
    db.commit()
    flash(f"Book issued successfully. Due date: {today + timedelta(days=LOAN_DAYS)}", "ok")
    return redirect(url_for("issue_page"))


@app.route("/return/<int:issue_id>", methods=["POST"])
def return_book(issue_id):
    db = get_db()
    rec = db.execute(
        "SELECT * FROM issue_records WHERE issue_id=? AND return_date IS NULL", (issue_id,)
    ).fetchone()
    if rec is None:
        flash("Record not found, or the book has already been returned.", "err")
        return redirect(url_for("issue_page"))
    today = date.today()
    late_days = max(0, (today - date.fromisoformat(rec["due_date"])).days)
    fine = late_days * FINE_PER_DAY            # fine = late days x Rs 5
    db.execute(
        "UPDATE issue_records SET return_date=?, fine_amount=? WHERE issue_id=?",
        (str(today), fine, issue_id),
    )
    db.execute("UPDATE books SET available_copies = available_copies + 1 WHERE book_id=?", (rec["book_id"],))
    db.commit()
    if fine:
        flash(f"Book returned {late_days} day(s) late. Fine: Rs {fine}.", "err")
    else:
        flash("Book returned on time. No fine.", "ok")
    return redirect(url_for("issue_page"))


# --------------------------------------------------------------------- run
if __name__ == "__main__":
    init_db()
    threading.Timer(1.2, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(debug=False)
