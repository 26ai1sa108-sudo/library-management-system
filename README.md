# Library Management System

A micro project built for the **Skills Development Monitoring System (SDMS), MITS-DU Gwalior**.
It helps a library manage its books and members digitally: add books, register members,
issue and return books, and calculate late fines automatically.

## Team

| Name | Role |
|------|------|
| Saksham Seth | Database design and Books module |
| Shubh Asati | Members module |
| Rajkrishnapal Malviya | Issue / return module and fine calculation |

## Features

- **Book management:** add, edit, delete and categorize books (title, author, ISBN, copies)
- **Member management:** register students / staff and keep their records
- **Issue & return:** track issue date, due date and return date for each book
- **Fine calculation:** automatic late fee based on overdue days
- **Search & filter:** find books by title, author, category or availability
- **Reports:** issued books, overdue books and member history

## Database Design

Three main tables:

| Table | Important columns |
|-------|-------------------|
| `books` | book_id (PK), title, author, category, isbn, total_copies, available_copies |
| `members` | member_id (PK), name, email, phone, member_type, join_date |
| `issue_records` | issue_id (PK), book_id (FK), member_id (FK), issue_date, due_date, return_date, fine_amount |

One book can be issued many times, and one member can issue many books (1 : N on both sides).

## Tech Stack

- Frontend: HTML, CSS, JavaScript
- Backend: [Python / Java / PHP / Node.js] (change this)
- Database: [MySQL / SQLite] (change this)

## How to Run

1. Clone the repository
   ```bash
   git clone https://github.com/<your-username>/library-management-system.git
   cd library-management-system
   ```
2. Install requirements (edit for your stack)
   ```bash
   # example for Python
   pip install -r requirements.txt
   ```
3. Set up the database using the SQL file (if you have one)
4. Start the project
   ```bash
   # example
   python app.py
   ```
5. Open the project in your browser (for example `http://localhost:5000`)

A quick browser-only demo is available in `demo/index.html` (open the file directly,
no installation needed).

## Project Milestones

- [x] **Milestone 1:** requirement analysis and system design (ER diagram, workflow, wireframes)
- [ ] **Milestone 2:** core modules (books, members, issue / return)
- [ ] **Milestone 3:** fine calculation, search, reports and final testing

## Screenshots

See the `showcase/` folder for the poster, ER diagram, workflow, features and architecture images.

## License

Made for academic purposes.
