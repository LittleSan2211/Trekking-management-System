from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# 1. Core User Table (For Auth & Access Control Only)
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)        # 'admin', 'staff', 'trekker'
    status = db.Column(db.String(20), default='Active')    # 'Active' or 'Blacklisted'

    # One-to-One Relationships for Profiles
    trekker_profile = db.relationship('TrekkerProfile', backref='auth_user', uselist=False, cascade="all, delete-orphan")
    staff_profile = db.relationship('StaffProfile', backref='auth_user', uselist=False, cascade="all, delete-orphan")
    

    bookings = db.relationship('Booking', backref='trekker', lazy=True)

# 2. Trekker / Customer Profile Table
# models.py ke andar TrekkerProfile ko aise update karein:
class TrekkerProfile(db.Model):
    __tablename__ = 'trekker_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(15), nullable=True)
    age = db.Column(db.Integer, nullable=True)         
    gender = db.Column(db.String(10), nullable=True)     
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)

# 3. Staff Profile Table
class StaffProfile(db.Model):
    __tablename__ = 'staff_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    approval_status = db.Column(db.String(20), default='Pending') # 'Pending', 'Approved', 'Rejected'
    

    treks = db.relationship('Trek', backref='assigned_guide', lazy=True)

# 4. Trek Table
class Trek(db.Model):
    __tablename__ = 'treks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)   # 'Easy', 'Moderate', 'Hard'
    duration = db.Column(db.Integer, nullable=False)        # In days
    total_slots = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Pending')    # 'Pending', 'Open', 'Closed', 'Completed'
    
    # Relationship: StaffProfile <-> Trek
    staff_profile_id = db.Column(db.Integer, db.ForeignKey('staff_profiles.id'), nullable=True)
    
    bookings = db.relationship('Booking', backref='trek', lazy=True, cascade='all, delete-orphan')

# 5. Booking Table
class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False) 
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Booked')     # 'Booked', 'Cancelled', 'Completed'
    payment_status = db.Column(db.String(20), default='Pending')