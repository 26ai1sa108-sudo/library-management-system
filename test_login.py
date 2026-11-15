import os, sys, tempfile
sys.path.insert(0, os.getcwd())
import app as A
A.DB_PATH = os.path.join(tempfile.mkdtemp(), "t.db")
A.init_db()

def ok(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        sys.exit(1)

c = A.app.test_client()
pages = ["/", "/books", "/members", "/issue", "/overdue"]
for p in pages:
    r = c.get(p)
    ok(f"{p} redirects to login when not logged in", r.status_code == 302 and "/login" in r.headers["Location"])
ok("POST pages are protected too", c.post("/books/add", data={"title": "T", "author": "A"}).status_code == 302)
ok("login page opens", c.get("/login").status_code == 200)
ok("wrong password rejected", b"Wrong username or password" in c.post("/login", data={"username": "admin", "password": "bad"}, follow_redirects=True).data)
ok("wrong username rejected", b"Wrong username or password" in c.post("/login", data={"username": "root", "password": "admin123"}, follow_redirects=True).data)
ok("still locked after failed logins", c.get("/books").status_code == 302)
r = c.post("/login", data={"username": "admin", "password": "admin123"})
ok("correct login redirects to dashboard", r.status_code == 302 and r.headers["Location"].endswith("/"))
ok("all pages open after login", all(c.get(p).status_code == 200 for p in pages))
ok("logout link is shown", b"Logout" in c.get("/").data)
c.get("/logout")
ok("pages locked again after logout", c.get("/books").status_code == 302)
r = c.post("/login?next=/overdue", data={"username": "admin", "password": "admin123"})
ok("login returns to the page that was asked for", r.headers["Location"].endswith("/overdue"))
c.get("/logout")
r = c.post("/login?next=//evil.com", data={"username": "admin", "password": "admin123"})
ok("outside redirect is ignored", "evil.com" not in r.headers["Location"])
ok("password is not stored as plain text in the code", "admin123" not in open("app.py").read().split("ADMIN_PASSWORD_HASH =")[1].split("\n")[0])
print("ALL LOGIN TESTS PASSED")
