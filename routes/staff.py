# routes/staff.py
from flask import Blueprint, render_template, redirect, request, url_for, flash, session
from models import db, User, StaffProfile, Trek, Booking, TrekkerProfile

staff_bp = Blueprint('staff', __name__, url_prefix='/staff')


def get_logged_in_staff():
    if 'user_id' not in session or session.get('role') != 'staff':
        return None
    # Fetch staff profile tied to user session
    return StaffProfile.query.filter_by(user_id=session['user_id']).first()

@staff_bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    staff = get_logged_in_staff()
    if not staff:
        flash("Access Denied or Session Expired!", "error")
        return redirect('/auth/login')
    

    if request.method == 'POST' and request.form.get('action') == 'update_profile':
        new_name = request.form.get('name')
        new_contact = request.form.get('contact')
        
        staff.name = new_name
        staff.contact = new_contact
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('staff.dashboard'))
        
    # Fetch only assigned treks for this staff member
    assigned_treks = Trek.query.filter_by(staff_profile_id=staff.id).all()
    
    return render_template('staff/dashboard.html', staff=staff, treks=assigned_treks)

@staff_bp.route('/manage_trek/<int:trek_id>', methods=['POST'])
def manage_trek(trek_id):
    staff = get_logged_in_staff()
    if not staff: return redirect('/auth/login')
    
    trek = Trek.query.get_or_404(trek_id)
    
    # Security Check: Ensure only assigned staff can manage this specific trek
    if trek.staff_profile_id != staff.id:
        flash("Unauthorized management attempt!", "error")
        return redirect(url_for('staff.dashboard'))
        
    # Update slots and status
    new_slots = request.form.get('available_slots')
    new_status = request.form.get('status')
    
    if new_slots is not None:
        slots_int = int(new_slots)
        if slots_int <= trek.total_slots:
            trek.available_slots = slots_int
        else:
            flash(f"Available slots cannot exceed total slots ({trek.total_slots})!", "error")
            return redirect(url_for('staff.dashboard'))
            
    if new_status:
        trek.status = new_status
        
    db.session.commit()
    flash(f"Trek #{trek.id} details updated successfully!", "success")
    return redirect(url_for('staff.dashboard'))

@staff_bp.route('/participants/<int:trek_id>')
def view_participants(trek_id):
    staff = get_logged_in_staff()
    if not staff: return redirect('/auth/login')
    
    trek = Trek.query.get_or_404(trek_id)
    
    # Security Check
    if trek.staff_profile_id != staff.id:
        flash("Unauthorized data access!", "error")
        return redirect(url_for('staff.dashboard'))
        
    # Fetch registered users through bookings linked to this trek
    bookings = Booking.query.filter_by(trek_id=trek.id).all()
    
    return render_template('staff/participants.html', trek=trek, bookings=bookings)