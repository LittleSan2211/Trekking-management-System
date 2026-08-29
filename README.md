# TrekPlan

TrekPlan is a Flask-based trekking management application designed to coordinate treks, staff, bookings, and user profiles in a single role-based platform. The project is built as a server-rendered web app with SQLite persistence and supports three user roles: admin, staff, and trekker.

## Project Overview

This application allows:

- Trekkers to browse available trekking programs and book available slots
- Staff members to manage assigned treks, update slot availability, and view participant lists
- Administrators to create treks, assign staff, manage user and staff approval status, and review booking records

The project is implemented as a multi-role operational dashboard using Flask and SQLAlchemy, with templates rendered on the server and a simple SQLite database for persistence.

## Main Features Implemented

- Role-based authentication and session management
- Registration for trekkers and staff
- Admin approval workflow for staff accounts
- Admin dashboard with summary metrics
- Trek creation, deletion, and staff assignment
- Staff dashboard for managing assigned treks
- Trekker dashboard for filtering and browsing open treks
- Booking flow with slot deduction and duplicate booking prevention
- User and staff profile updates
- Booking history and admin booking log
- Seeded sample data for demo/testing setup

## User Roles and Functionality

### 1. Admin

Admin users can:

- Sign in using the admin role
- View dashboard statistics for treks, users, staff, and bookings
- Create new treks and assign staff guides
- Delete treks
- Approve or blacklist staff accounts
- Activate or blacklist trekker accounts
- View booking history across the application

### 2. Staff

Staff users can:

- Sign in only after their account is approved by an admin
- Update their own profile information
- View treks assigned to them by the admin
- Modify available slot counts for assigned treks
- Update trek status values such as Pending, Open, Closed, and Completed
- View registered participants for each assigned trek

### 3. Trekker

Trekker users can:

- Register and log in as a trekker
- Search and filter open treks by location and difficulty
- Book a trek if slots are still available
- Prevent duplicate bookings for the same trek
- View their booking history
- Update their profile details

## Tech Stack

### Backend

- Python 3
- Flask 3.0.3
- Flask-SQLAlchemy 3.1.1
- SQLAlchemy 2.0.31
- SQLite

### Frontend

- Jinja2 templating engine
- Bootstrap 5
- Bootstrap Icons
- Custom CSS stylesheets in the static folder

### Application Structure

- Flask blueprints for modular routing
- Server-side rendered HTML pages instead of a separate frontend framework

## Backend and Frontend Architecture

### Backend Architecture

The backend is organized around Flask blueprints and a shared SQLAlchemy model layer:

- `app.py`: application entry point, database initialization, seeded demo data, route registration
- `models.py`: database models and ORM relationships
- `routes/auth.py`: login, registration, logout, and session setup
- `routes/admin.py`: admin-only dashboard and administrative actions
- `routes/staff.py`: staff-specific dashboard and trek management actions
- `routes/user.py`: trekker booking and profile flows

### Frontend Architecture

The front end is not a React or Vue application. It uses:

- Server-rendered Jinja templates inside `templates/`
- Shared base layout in `templates/base.html`
- Role-specific dashboard templates under `templates/admin/`, `templates/staff/`, and `templates/user/`
- Styling in `static/css/` for admin, user, staff, and home pages

## Authentication and Authorization Approach

The application uses a simple session-based authentication pattern:

- User credentials are checked during login using the submitted email, password, and selected role
- Session variables store `user_id`, `role`, and `email`
- Role-based access is enforced in the route handlers
- Admin routes verify that the session role is `admin`
- Staff routes verify that the session role is `staff`
- Trekker routes verify that the session role is `trekker`
- Blacklisted users cannot log in
- Staff accounts must have `approval_status == 'Approved'` before login is permitted

This project does not use Flask-Login, JWTs, OAuth, or a separate identity provider.

## Database and ORM Usage

The application uses SQLite with SQLAlchemy ORM.

Core models include:

- `User`: authentication and role tracking
- `TrekkerProfile`: trekker profile metadata
- `StaffProfile`: staff metadata and approval state
- `Trek`: trek data, schedule, capacity, and assigned staff
- `Booking`: trek booking records and payment status

Relationships implemented:

- One-to-one between `User` and `TrekkerProfile`
- One-to-one between `User` and `StaffProfile`
- One-to-many between `StaffProfile` and `Trek`
- One-to-many between `User` and `Booking`
- One-to-many between `Trek` and `Booking`

## Background Tasks and Scheduled Jobs

No scheduled jobs, background workers, task queue, or asynchronous processing are implemented in this repository.

The app initializes its database and seed data directly when the Flask app starts, but there are no recurring automation tasks or cron-style jobs.

## Reporting Functionality

Reporting is limited to the administrative booking overview.

- The admin dashboard shows summary counts for treks, users, staff, and bookings
- The admin history page displays a list of booking records ordered by date
- There is no PDF export, CSV report generation, analytics dashboard, or advanced reporting engine in the current codebase

## Project Folder Structure

```text
.
├── app.py
├── models.py
├── requirements.txt
├── README.md
├── instance/
│   └── (database/runtime files)
├── routes/
│   ├── admin.py
│   ├── auth.py
│   ├── staff.py
│   └── user.py
├── static/
│   ├── css/
│   │   ├── admin.css
│   │   ├── auth.css
│   │   ├── home.css
│   │   ├── mai.css
│   │   ├── staff.css
│   │   └── user.css
├── templates/
│   ├── about.html
│   ├── base.html
│   ├── home.html
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── history.html
│   │   ├── staff.html
│   │   ├── treks.html
│   │   └── users.html
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── staff/
│   │   ├── dashboard.html
│   │   └── participants.html
│   └── user/
│       ├── bookings.html
│       ├── dashboard.html
│       └── profile.html
└── trekking.db
```

## Installation and Setup

### Prerequisites

- Python 3.9+
- pip
- Virtual environment support

### 1. Clone the project

```bash
git clone <repository-url>
cd trekking_app
```

### 2. Create and activate a virtual environment

On macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Environment Variables

This project currently stores configuration values directly in `app.py`, including the secret key and database path. For production usage, these should be moved to environment variables.

Use placeholders only; do not commit real secrets.

```bash
export SECRET_KEY="replace-with-secure-secret-key"
export DATABASE_URL="sqlite:///trekking.db"
```

If you are using a local development environment, the project can still run with the default SQLite configuration already present in the codebase.

## How to Run the Application

### Option 1: Run the app directly

```bash
python app.py
```

### Option 2: Run with Flask CLI

```bash
flask --app app run
```

The app is served by Flask and typically runs at:

```text
http://127.0.0.1:5000
```

There is no separate frontend server or SPA in this repository; the interface is rendered server-side through the Flask templates.

## Key Application Workflows

### User registration and login

1. Open the registration page
2. Select a role: `trekker` or `staff`
3. Complete the required form fields
4. Log in with the same email and selected role
5. Users are redirected to their role-based dashboard

### Admin workflow

1. Log in as admin
2. View metrics on the dashboard
3. Add or remove treks
4. Assign staff to specific treks
5. Approve or blacklist staff members
6. Review booking history

### Staff workflow

1. Staff account must be approved by admin before access is granted
2. Staff logs in and views assigned treks
3. Staff updates slot availability and trek status
4. Staff checks participant list for each trek

### Trekker workflow

1. Trekker logs in and sees open treks
2. Filters by location or difficulty
3. Books a trek if slots are available
4. The booking is recorded and availability is reduced
5. Trekker can check booking history and update profile information

## Seeded Demo Data

On first database initialization, the app seeds example records for:

- 1 admin account
- 50 trekker users
- 50 staff users
- 50 trek records
- 50 booking records

This makes the project easy to explore locally without needing manual data entry.

## Future Improvements

The following are not implemented in the current codebase but would be valuable next steps:

- Move configuration values such as secret keys and database settings to environment variables
- Add secure password hashing instead of storing raw passwords
- Add proper validation and business rules for date and slot logic
- Introduce real payment processing and booking status transitions
- Add advanced reporting, CSV/PDF exports, and analytics dashboards
- Add automated tests and CI pipeline
- Add notifications and reminders for treks and bookings
- Improve role-management and permissions with a formal authorization framework
- Replace the SQLite setup with PostgreSQL or MySQL for production use

## Notes

This project is a functional, role-based trekking management application with a strong server-rendered UI and clear separation between admin, staff, and trekker responsibilities. It is suitable for demonstrating backend logic, ORM patterns, database design, and role-based access control in a portfolio project.
