from flask import Flask, redirect, render_template
from datetime import datetime, date, timedelta
from models import db, User, TrekkerProfile, StaffProfile, Trek, Booking
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'trekking_secret_key_1234'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trekking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Dummy seed data for all tables, only when the target table is empty.
def seed_dummy_data():
    if User.query.first() is None:
        users = [
            User(email="admin@trek.com", password="adminpassword", role="admin", status="Active")
        ]

        for i in range(1, 51):
            users.append(User(
                email=f"trekker{i}@trek.com",
                password=f"trekker{i}pass",
                role="trekker",
                status="Active"
            ))

        for i in range(1, 51):
            users.append(User(
                email=f"staff{i}@trek.com",
                password=f"staff{i}pass",
                role="staff",
                status="Active"
            ))

        db.session.bulk_save_objects(users)
        db.session.commit()
        print("Seeded 101 users (1 admin, 50 trekkers, 50 staff).")
    else:
        print("User table already contains data; skipping user seed.")

    if TrekkerProfile.query.first() is None:
        trekker_users = User.query.filter_by(role='trekker').all()
        trekker_profiles = []
        genders = ['Male', 'Female', 'Other']
        for index, user in enumerate(trekker_users, start=1):
            trekker_profiles.append(TrekkerProfile(
                user_id=user.id,
                name=f"Trekker {index}",
                contact=f"98765{10000 + index}",
                age=18 + (index % 30),
                gender=genders[index % len(genders)],
                joined_date=datetime.utcnow()
            ))

        if trekker_profiles:
            db.session.bulk_save_objects(trekker_profiles)
            db.session.commit()
            print(f"Seeded {len(trekker_profiles)} trekker profiles.")
        else:
            print("No trekker users available to seed trekker profiles.")
    else:
        print("TrekkerProfile table already contains data; skipping trekker profile seed.")

    if StaffProfile.query.first() is None:
        staff_users = User.query.filter_by(role='staff').all()
        staff_profiles = []
        for index, user in enumerate(staff_users, start=1):
            staff_profiles.append(StaffProfile(
                user_id=user.id,
                name=f"Staff Guide {index}",
                contact=f"87654{10000 + index}",
                approval_status='Approved'
            ))

        if staff_profiles:
            db.session.bulk_save_objects(staff_profiles)
            db.session.commit()
            print(f"Seeded {len(staff_profiles)} staff profiles.")
        else:
            print("No staff users available to seed staff profiles.")
    else:
        print("StaffProfile table already contains data; skipping staff profile seed.")

    if Trek.query.first() is None:
        locations = [
            'Himalayan Foothills', 'Valley Ridge', 'Misty Peaks', 'Sunset Pass',
            'Emerald Forest', 'Crystal Lake', 'Thunder Gorge', 'Silver Summit',
            'Wildflower Trail', 'Ancient Canyon'
        ]
        difficulties = ['Easy', 'Moderate', 'Hard']
        statuses = ['Open', 'Pending', 'Closed', 'Completed']
        staff_profiles = StaffProfile.query.all()
        treks = []

        for i in range(1, 51):
            duration = 3 + (i % 5)
            start_date = date.today() + timedelta(days=7 + i * 2)
            end_date = start_date + timedelta(days=duration)
            total_slots = 15 + (i % 16)
            available_slots = max(0, total_slots - (i % 6))
            assigned_staff = staff_profiles[(i - 1) % len(staff_profiles)] if staff_profiles else None

            treks.append(Trek(
                name=f"{locations[i % len(locations)]} Trek {i}",
                location=locations[i % len(locations)],
                difficulty=difficulties[i % len(difficulties)],
                duration=duration,
                total_slots=total_slots,
                available_slots=available_slots,
                start_date=start_date,
                end_date=end_date,
                status=statuses[i % len(statuses)],
                staff_profile_id=assigned_staff.id if assigned_staff else None
            ))

        db.session.bulk_save_objects(treks)
        db.session.commit()
        print("Seeded 50 treks.")
    else:
        print("Trek table already contains data; skipping trek seed.")

    if Booking.query.first() is None:
        trekker_ids = [user.id for user in User.query.filter_by(role='trekker').all()]
        trek_ids = [trek.id for trek in Trek.query.all()]
        bookings = []
        booking_statuses = ['Booked', 'Cancelled', 'Completed']
        payment_statuses = ['Pending', 'Paid', 'Failed']

        if trekker_ids and trek_ids:
            for i in range(1, 51):
                bookings.append(Booking(
                    user_id=trekker_ids[(i - 1) % len(trekker_ids)],
                    trek_id=trek_ids[(i - 1) % len(trek_ids)],
                    booking_date=datetime.utcnow() - timedelta(days=i),
                    status=booking_statuses[i % len(booking_statuses)],
                    payment_status=payment_statuses[i % len(payment_statuses)]
                ))

            db.session.bulk_save_objects(bookings)
            db.session.commit()
            print("Seeded 50 bookings.")
        else:
            print("Not enough trekker or trek data available to seed bookings.")
    else:
        print("Booking table already contains data; skipping booking seed.")

# Programmatic Database and Admin Creation with robust Error Handling
with app.app_context():
    try:
        db.create_all()
        seed_dummy_data()
    except Exception as e:
        db.session.rollback()
        print(f"Database Initialization Error: {e}")

# Blueprints Registration
from routes.auth import auth_bp
from routes.admin import admin_bp 
from routes.staff import staff_bp 
from routes.user import user_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(user_bp)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)