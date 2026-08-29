from flask import Blueprint, render_template, redirect, request, url_for, flash, session
from models import db, User, TrekkerProfile, Trek, Booking

user_bp = Blueprint('user', __name__, url_prefix='/user')

def get_logged_in_trekker():
    if 'user_id' not in session or session.get('role') != 'trekker':
        return None
    return TrekkerProfile.query.filter_by(user_id=session['user_id']).first()

@user_bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    trekker = get_logged_in_trekker()
    if not trekker:
        flash("Access Denied! Please login as a Trekker.", "error")
        return redirect('/auth/login')

    search_location = request.args.get('location', '')
    filter_difficulty = request.args.get('difficulty', '')

    query = Trek.query.filter_by(status='Open')

    if search_location:
        query = query.filter(Trek.location.like(f"%{search_location}%"))
    if filter_difficulty:
        query = query.filter_by(difficulty=filter_difficulty)

    available_treks = query.all()
    return render_template('user/dashboard.html', trekker=trekker, treks=available_treks, 
                           search_location=search_location, filter_difficulty=filter_difficulty)

@user_bp.route('/book_trek/<int:trek_id>', methods=['POST'])
def book_trek(trek_id):
    trekker = get_logged_in_trekker()
    if not trekker: return redirect('/auth/login')

    trek = Trek.query.get_or_404(trek_id)

    if trek.status != 'Open' or trek.available_slots <= 0:
        flash("Sorry! This trek is either full or closed for bookings.", "error")
        return redirect(url_for('user.dashboard'))

    existing_booking = Booking.query.filter_by(user_id=session['user_id'], trek_id=trek.id).first()
    if existing_booking:
        flash("You have already booked this trek program!", "warning")
        return redirect(url_for('user.view_bookings'))

    try:
        new_booking = Booking(user_id=session['user_id'], trek_id=trek.id, status='Booked', payment_status='Pending')
        trek.available_slots -= 1
        
        db.session.add(new_booking)
        db.session.commit()
        flash(f"Congratulations! Your booking for {trek.name} is confirmed.", "success")
    except Exception:
        db.session.rollback()
        flash("Booking processing failed due to high traffic or database error. Try again!", "error")
        
    return redirect(url_for('user.view_bookings'))

@user_bp.route('/my_bookings')
def view_bookings():
    trekker = get_logged_in_trekker()
    if not trekker: return redirect('/auth/login')

    my_bookings = Booking.query.filter_by(user_id=session['user_id']).order_by(Booking.booking_date.desc()).all()
    return render_template('user/bookings.html', trekker=trekker, bookings=my_bookings)

@user_bp.route('/profile', methods=['GET', 'POST'])
def edit_profile():
    trekker = get_logged_in_trekker()
    if not trekker:
        flash("Access Denied! Please login as a Trekker.", "error")
        return redirect('/auth/login')

    if request.method == 'POST':
        try:
            trekker.name = request.form.get('name')
            trekker.contact = request.form.get('contact')
            trekker.age = int(request.form.get('age')) if request.form.get('age') else None
            trekker.gender = request.form.get('gender')
            
            db.session.commit()
            flash("Your profile has been updated successfully!", "success")
        except Exception:
            db.session.rollback()
            flash("Failed to update profile details. Please try again.", "error")
        return redirect(url_for('user.edit_profile'))

    return render_template('user/profile.html', trekker=trekker)