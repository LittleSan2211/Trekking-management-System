from flask import Blueprint, render_template, redirect, request, url_for, flash, session
from models import db, User, TrekkerProfile, StaffProfile

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        user = User.query.filter_by(email=email, role=role).first()

        if not user or user.password != password:
            flash('Invalid Email, Password or Role Selection!', 'error')
            return redirect(url_for('auth.login'))
        
        if user.status == 'Blacklisted':
            flash('Your account has been blacklisted by Admin.', 'error')
            return redirect(url_for('auth.login'))

        if role == 'staff':
            if user.staff_profile.approval_status != 'Approved':
                flash('Your account is pending Admin approval.', 'warning')
                return redirect(url_for('auth.login'))

        # Session Setup
        session['user_id'] = user.id
        session['role'] = user.role
        session['email'] = user.email

        if user.role == 'admin':
            return redirect('/admin/dashboard')
        elif user.role == 'staff':
            return redirect('/staff/dashboard')
        else:
            return redirect('/user/dashboard')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        contact = request.form.get('contact')
        role = request.form.get('role')

        if User.query.filter_by(email=email).first():
            flash('This email is already registered!', 'error')
            return redirect(url_for('auth.register'))

        try:
            # Create Core User
            new_user = User(email=email, password=password, role=role, status='Active')
            db.session.add(new_user)
            db.session.commit()

            # Create Profile Based on Selected Role
            if role == 'trekker':
                age = request.form.get('age')
                gender = request.form.get('gender')
                profile = TrekkerProfile(user_id=new_user.id, name=name, contact=contact, age=age, gender=gender)
                db.session.add(profile)
            elif role == 'staff':
                profile = StaffProfile(user_id=new_user.id, name=name, contact=contact, approval_status='Pending')
                db.session.add(profile)

            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))

        except Exception:
            db.session.rollback()
            flash('Something went wrong during registration. Please try again!', 'error')
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))