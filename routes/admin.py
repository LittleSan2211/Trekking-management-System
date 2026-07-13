from flask import Blueprint, render_template, redirect, request, url_for, flash, session
from models import db, User, TrekkerProfile, StaffProfile, Trek, Booking
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def check_admin():
    if 'user_id' not in session or session.get('role') != 'admin':
        return False
    return True

@admin_bp.route('/dashboard')
def dashboard():
    if not check_admin():
        flash("Access Denied!", "error")
        return redirect('/auth/login')
    

    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role='trekker').count()
    total_staff = User.query.filter_by(role='staff').count()
    total_bookings = Booking.query.count()
    

    recent_bookings = Booking.query.order_by(Booking.booking_date.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                           total_treks=total_treks, total_users=total_users,
                           total_staff=total_staff, total_bookings=total_bookings,
                           recent_bookings=recent_bookings)

# 2. Manage Treks (List & Add)
@admin_bp.route('/treks', methods=['GET', 'POST'])
def manage_treks():
    if not check_admin(): return redirect('/auth/login')
    
    if request.method == 'POST':
        name = request.form.get('name')
        location = request.form.get('location')
        difficulty = request.form.get('difficulty')
        duration = int(request.form.get('duration'))
        slots = int(request.form.get('slots'))
        start_dt = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        end_dt = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        
        new_trek = Trek(name=name, location=location, difficulty=difficulty,
                        duration=duration, total_slots=slots, available_slots=slots,
                        start_date=start_dt, end_date=end_dt, status='Open')
        db.session.add(new_trek)
        db.session.commit()
        flash('New Trek Route Added Successfully!', 'success')
        return redirect(url_for('admin.manage_treks'))
    
    # Search & Filter Logic
    search_query = request.args.get('search', '')
    if search_query:
        all_treks = Trek.query.filter((Trek.name.like(f"%{search_query}%")) | (Trek.id == search_query)).all()
    else:
        all_treks = Trek.query.all()
        
    staff_list = StaffProfile.query.filter_by(approval_status='Approved').all()
    return render_template('admin/treks.html', treks=all_treks, staff_list=staff_list, search_query=search_query)

# 3. Assign Staff to Trek
@admin_bp.route('/assign_staff/<int:trek_id>', methods=['POST'])
def assign_staff(trek_id):
    if not check_admin(): return redirect('/auth/login')
    trek = Trek.query.get_or_404(trek_id)
    staff_profile_id = request.form.get('staff_profile_id')
    
    if staff_profile_id:
        trek.staff_profile_id = int(staff_profile_id)
        db.session.commit()
        flash('Staff Assigned Successfully!', 'success')
    return redirect(url_for('admin.manage_treks'))

# 4. Action: Delete Trek
@admin_bp.route('/delete_trek/<int:trek_id>')
def delete_trek(trek_id):
    if not check_admin(): return redirect('/auth/login')
    trek = Trek.query.get_or_404(trek_id)
    db.session.delete(trek)
    db.session.commit()
    flash('Trek removed successfully.', 'info')
    return redirect(url_for('admin.manage_treks'))

# 5. Manage Staff (Approval & Blacklist)
@admin_bp.route('/staff')
def manage_staff():
    if not check_admin(): return redirect('/auth/login')
    search_query = request.args.get('search', '')
    
    if search_query:
        staff_members = StaffProfile.query.filter(StaffProfile.name.like(f"%{search_query}%")).all()
    else:
        staff_members = StaffProfile.query.all()
        
    return render_template('admin/staff.html', staff_members=staff_members, search_query=search_query)

@admin_bp.route('/staff_action/<int:profile_id>/<string:action>')
def staff_action(profile_id, action):
    if not check_admin(): return redirect('/auth/login')
    profile = StaffProfile.query.get_or_404(profile_id)
    
    if action == 'approve':
        profile.approval_status = 'Approved'
    elif action == 'blacklist':
        profile.auth_user.status = 'Blacklisted'
    elif action == 'activate':
        profile.auth_user.status = 'Active'
        
    db.session.commit()
    flash(f'Staff status updated successfully!', 'success')
    return redirect(url_for('admin.manage_staff'))

# 6. Manage Users (View & Blacklist)
@admin_bp.route('/users')
def manage_users():
    if not check_admin(): return redirect('/auth/login')
    search_query = request.args.get('search', '')
    
    if search_query:
        users = TrekkerProfile.query.filter(TrekkerProfile.name.like(f"%{search_query}%")).all()
    else:
        users = TrekkerProfile.query.all()
        
    return render_template('admin/users.html', users=users, search_query=search_query)

@admin_bp.route('/user_action/<int:profile_id>/<string:action>')
def user_action(profile_id, action):
    if not check_admin(): return redirect('/auth/login')
    profile = TrekkerProfile.query.get_or_404(profile_id)
    
    if action == 'blacklist':
        profile.auth_user.status = 'Blacklisted'
    elif action == 'activate':
        profile.auth_user.status = 'Active'
        
    db.session.commit()
    flash('User status updated successfully.', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/history')
def global_history():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/auth/login')
        
    # Query all booking records in the entire database
    all_bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template('admin/history.html', bookings=all_bookings)

