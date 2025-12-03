from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date, timedelta, datetime

from app import db
from app.models import User, Department, DoctorProfile, Appointment, Treatment

main = Blueprint("main", __name__)

# ======================================================
# AUTHENTICATION
# ======================================================

@main.route("/")
def index():
    return render_template("index.html")


@main.route("/login", methods=["GET", "POST"])
def login():
    # already logged in → go straight to their dashboard
    if current_user.is_authenticated:
        return redirect(url_for(f"main.{current_user.role}_dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email, active=True).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for(f"main.{user.role}_dashboard"))

        flash("Invalid email or password", "danger")

    return render_template("login.html")


@main.route("/register", methods=["GET", "POST"])
def register():
    # self–registration is for patients only
    if request.method == "POST":
        email = request.form.get("email")

        if User.query.filter_by(email=email).first():
            flash("User already exists with this email", "danger")
            return redirect(url_for("main.register"))

        patient = User(
            name=request.form.get("name"),
            email=email,
            role="patient",
            password_hash=generate_password_hash(request.form.get("password"))
        )
        db.session.add(patient)
        db.session.commit()

        flash("Registration successful. Please login.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html")


@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))

# ======================================================
# ADMIN
# ======================================================

@main.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return redirect(url_for("main.index"))

    doctor_count = User.query.filter_by(role="doctor").count()
    patient_count = User.query.filter_by(role="patient").count()
    appointment_count = Appointment.query.count()

    return render_template(
        "admin_dashboard.html",
        doctor_count=doctor_count,
        patient_count=patient_count,
        appointment_count=appointment_count
    )


@main.route("/admin/add-doctor", methods=["GET", "POST"])
@login_required
def add_doctor():
    if current_user.role != "admin":
        return redirect(url_for("main.index"))

    departments = Department.query.all()

    if request.method == "POST":
        email = request.form.get("email")

        if User.query.filter_by(email=email).first():
            flash("Doctor with this email already exists", "danger")
            return redirect(url_for("main.add_doctor"))

        doctor = User(
            name=request.form.get("name"),
            email=email,
            role="doctor",
            password_hash=generate_password_hash(request.form.get("password"))
        )
        db.session.add(doctor)
        db.session.commit()

        profile = DoctorProfile(
            user_id=doctor.id,
            department_id=request.form.get("department_id")
        )
        db.session.add(profile)
        db.session.commit()

        flash("Doctor added successfully", "success")
        return redirect(url_for("main.admin_dashboard"))

    return render_template(
        "add_doctor.html",
        departments=departments
    )


@main.route("/admin/doctors")
@login_required
def view_doctors():
    if current_user.role != "admin":
        return redirect(url_for("main.index"))

    doctors = User.query.filter_by(role="doctor").all()
    return render_template("view_doctors.html", doctors=doctors)


@main.route("/admin/edit-doctor/<int:doctor_id>", methods=["GET", "POST"])
@login_required
def edit_doctor(doctor_id):
    if current_user.role != "admin":
        return redirect(url_for("main.index"))

    doctor = User.query.get_or_404(doctor_id)
    profile = DoctorProfile.query.filter_by(user_id=doctor.id).first()
    departments = Department.query.all()

    if request.method == "POST":
        doctor.name = request.form.get("name")
        profile.department_id = request.form.get("department_id")
        profile.availability = request.form.get("availability")
        db.session.commit()

        flash("Doctor details updated successfully", "success")
        return redirect(url_for("main.view_doctors"))

    return render_template(
        "edit_doctor.html",
        doctor=doctor,
        profile=profile,
        departments=departments
    )


@main.route("/admin/deactivate-doctor/<int:doctor_id>")
@login_required
def deactivate_doctor(doctor_id):
    if current_user.role != "admin":
        return redirect(url_for("main.index"))

    doctor = User.query.get_or_404(doctor_id)

    if doctor.role != "doctor":
        flash("Invalid doctor account", "danger")
        return redirect(url_for("main.view_doctors"))

    doctor.active = False
    db.session.commit()

    flash("Doctor deactivated", "warning")
    return redirect(url_for("main.view_doctors"))


@main.route("/admin/add-department", methods=["GET", "POST"])
@login_required
def add_department():
    if current_user.role != "admin":
        return redirect(url_for("main.index"))

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        if Department.query.filter_by(name=name).first():
            flash("Department already exists", "danger")
            return redirect(url_for("main.add_department"))

        dept = Department(name=name, description=description)
        db.session.add(dept)
        db.session.commit()

        flash("Department added successfully", "success")
        return redirect(url_for("main.admin_dashboard"))

    return render_template("add_department.html")


@main.route("/admin/search", methods=["GET", "POST"])
@login_required
def admin_search():
    if current_user.role != "admin":
        return redirect(url_for("main.index"))

    user_results = []
    doctor_results = []

    if request.method == "POST":
        q = request.form.get("query")

        # patient/doctor search by name/email
        user_results = User.query.filter(
            (User.name.ilike(f"%{q}%")) |
            (User.email.ilike(f"%{q}%"))
        ).all()

        # doctor search by specialization
        doctor_results = (
            db.session.query(User, Department)
            .select_from(DoctorProfile)
            .join(User, DoctorProfile.user_id == User.id)
            .join(Department, DoctorProfile.department_id == Department.id)
            .filter(Department.name.ilike(f"%{q}%"))
            .all()
        )

    return render_template(
        "admin_search.html",
        user_results=user_results,
        doctor_results=doctor_results
    )


@main.route("/admin/edit-patient/<int:patient_id>", methods=["GET", "POST"])
@login_required
def edit_patient(patient_id):
    if current_user.role != "admin":
        return redirect(url_for("main.index"))

    patient = User.query.get_or_404(patient_id)

    if patient.role != "patient":
        flash("Invalid account type", "danger")
        return redirect(url_for("main.admin_search"))

    if request.method == "POST":
        patient.name = request.form.get("name")
        patient.email = request.form.get("email")
        patient.active = True if request.form.get("active") == "on" else False
        db.session.commit()

        flash("Patient updated successfully", "success")
        return redirect(url_for("main.admin_search"))

    return render_template("edit_patient.html", patient=patient)


@main.route("/admin/deactivate-patient/<int:patient_id>")
@login_required
def deactivate_patient(patient_id):
    if current_user.role != "admin":
        return redirect(url_for("main.index"))

    patient = User.query.get_or_404(patient_id)

    if patient.role != "patient":
        flash("Invalid account type", "danger")
        return redirect(url_for("main.admin_search"))

    patient.active = False
    db.session.commit()

    flash("Patient blacklisted", "warning")
    return redirect(url_for("main.admin_search"))


@main.route("/admin/appointments")
@login_required
def admin_appointments():
    if current_user.role != "admin":
        return redirect(url_for("main.index"))

    appointments = Appointment.query.order_by(
        Appointment.date.desc()
    ).all()

    return render_template("admin_appointments.html", appointments=appointments)

# ======================================================
# DOCTOR
# ======================================================

@main.route("/doctor/dashboard")
@login_required
def doctor_dashboard():
    if current_user.role != "doctor":
        return redirect(url_for("main.index"))

    today = date.today()
    week_later = today + timedelta(days=7)

    upcoming = Appointment.query.filter(
        Appointment.doctor_id == current_user.id,
        Appointment.date.between(today, week_later),
        Appointment.status == "Booked"
    ).all()

    patients = (
        db.session.query(User)
        .join(Appointment, Appointment.patient_id == User.id)
        .filter(Appointment.doctor_id == current_user.id)
        .distinct()
        .all()
    )

    return render_template(
        "doctor_dashboard.html",
        upcoming_appointments=upcoming,
        patients=patients
    )


@main.route("/doctor/appointments")
@login_required
def doctor_appointments():
    if current_user.role != "doctor":
        return redirect(url_for("main.index"))

    appointments = Appointment.query.filter_by(
        doctor_id=current_user.id
    ).order_by(Appointment.date).all()

    return render_template("doctor_appointments.html", appointments=appointments)


@main.route("/doctor/complete-appointment/<int:appt_id>", methods=["GET", "POST"])
@login_required
def complete_appointment(appt_id):
    if current_user.role != "doctor":
        return redirect(url_for("main.index"))

    appt = Appointment.query.get_or_404(appt_id)

    if appt.doctor_id != current_user.id:
        flash("Unauthorized", "danger")
        return redirect(url_for("main.doctor_appointments"))

    if request.method == "POST":
        treatment = Treatment(
            appointment_id=appt.id,
            diagnosis=request.form.get("diagnosis"),
            prescription=request.form.get("prescription"),
            notes=request.form.get("notes")
        )
        db.session.add(treatment)
        appt.status = "Completed"
        db.session.commit()

        flash("Appointment marked as completed", "success")
        return redirect(url_for("main.doctor_appointments"))

    return render_template("complete_appointment.html", appointment=appt)


@main.route("/doctor/cancel-appointment/<int:appt_id>")
@login_required
def doctor_cancel_appointment(appt_id):
    if current_user.role != "doctor":
        return redirect(url_for("main.index"))

    appt = Appointment.query.get_or_404(appt_id)

    if appt.doctor_id != current_user.id:
        flash("Unauthorized", "danger")
        return redirect(url_for("main.doctor_appointments"))

    appt.status = "Cancelled"
    db.session.commit()

    flash("Appointment cancelled", "warning")
    return redirect(url_for("main.doctor_appointments"))


@main.route("/doctor/availability", methods=["GET", "POST"])
@login_required
def doctor_availability():
    if current_user.role != "doctor":
        return redirect(url_for("main.index"))

    profile = DoctorProfile.query.filter_by(user_id=current_user.id).first()

    if request.method == "POST":
        profile.availability = request.form.get("availability")
        db.session.commit()
        flash("Availability updated", "success")
        return redirect(url_for("main.doctor_dashboard"))

    return render_template(
        "doctor_availability.html",
        availability=profile.availability
    )

# ======================================================
# PATIENT
# ======================================================

@main.route("/patient/dashboard")
@login_required
def patient_dashboard():
    if current_user.role != "patient":
        return redirect(url_for("main.index"))

    doctors = (
        User.query
        .join(DoctorProfile, DoctorProfile.user_id == User.id)
        .filter(
            User.role == "doctor",
            User.active == True
        )
        .all()
    )

    upcoming = Appointment.query.filter(
        Appointment.patient_id == current_user.id
    ).order_by(Appointment.date).all()

    return render_template(
        "patient_dashboard.html",
        doctors=doctors,
        upcoming_appointments=upcoming
    )


@main.route("/patient/appointments")
@login_required
def patient_appointments():
    if current_user.role != "patient":
        return redirect(url_for("main.index"))

    appointments = Appointment.query.filter_by(
        patient_id=current_user.id
    ).order_by(Appointment.date.desc()).all()

    return render_template("patient_appointments.html", appointments=appointments)


@main.route("/patient/profile", methods=["GET", "POST"])
@login_required
def patient_profile():
    if current_user.role != "patient":
        return redirect(url_for("main.index"))

    if request.method == "POST":
        current_user.name = request.form.get("name")
        current_user.email = request.form.get("email")
        db.session.commit()

        flash("Profile updated", "success")
        return redirect(url_for("main.patient_dashboard"))

    return render_template("patient_profile.html")


@main.route("/patient/cancel-appointment/<int:appt_id>")
@login_required
def cancel_appointment(appt_id):
    if current_user.role != "patient":
        return redirect(url_for("main.index"))

    appt = Appointment.query.get_or_404(appt_id)

    if appt.patient_id != current_user.id:
        flash("Unauthorized", "danger")
        return redirect(url_for("main.patient_appointments"))

    appt.status = "Cancelled"
    db.session.commit()

    flash("Appointment cancelled", "info")
    return redirect(url_for("main.patient_appointments"))


@main.route("/patient/reschedule-appointment/<int:appt_id>", methods=["GET", "POST"])
@login_required
def reschedule_appointment(appt_id):
    if current_user.role != "patient":
        return redirect(url_for("main.index"))

    appt = Appointment.query.get_or_404(appt_id)

    if appt.patient_id != current_user.id or appt.status != "Booked":
        flash("You cannot reschedule this appointment", "danger")
        return redirect(url_for("main.patient_appointments"))

    if request.method == "POST":
        new_date = datetime.strptime(
            request.form.get("date"), "%Y-%m-%d"
        ).date()
        new_time = datetime.strptime(
            request.form.get("time"), "%H:%M"
        ).time()

        conflict = Appointment.query.filter_by(
            doctor_id=appt.doctor_id,
            date=new_date,
            time=new_time,
            status="Booked"
        ).first()

        if conflict:
            flash("Doctor not available at this time", "danger")
            return redirect(url_for("main.reschedule_appointment", appt_id=appt.id))

        appt.date = new_date
        appt.time = new_time
        db.session.commit()

        flash("Appointment rescheduled", "success")
        return redirect(url_for("main.patient_appointments"))

    return render_template("reschedule_appointment.html", appointment=appt)


@main.route("/departments")
@login_required
def view_departments():
    if current_user.role != "patient":
        return redirect(url_for("main.index"))

    departments = Department.query.all()
    return render_template("patient_departments.html", departments=departments)


@main.route("/departments/<int:dept_id>/doctors", methods=["GET", "POST"])
@login_required
def view_doctors_by_department(dept_id):
    if current_user.role != "patient":
        return redirect(url_for("main.index"))

    availability = None
    if request.method == "POST":
        availability = request.form.get("availability")

    query = (
        db.session.query(User)
        .join(DoctorProfile, DoctorProfile.user_id == User.id)
        .filter(
            DoctorProfile.department_id == dept_id,
            User.role == "doctor",
            User.active == True
        )
    )

    if availability:
        query = query.filter(
            DoctorProfile.availability.ilike(f"%{availability}%")
        )

    doctors = query.all()

    return render_template(
        "patient_doctors.html",
        doctors=doctors,
        availability=availability
    )


@main.route("/book-appointment/<int:doctor_id>", methods=["GET", "POST"])
@login_required
def book_appointment(doctor_id):
    if current_user.role != "patient":
        return redirect(url_for("main.index"))

    doctor = User.query.get_or_404(doctor_id)

    if request.method == "POST":
        d = datetime.strptime(request.form.get("date"), "%Y-%m-%d").date()
        t = datetime.strptime(request.form.get("time"), "%H:%M").time()

        conflict = Appointment.query.filter_by(
            doctor_id=doctor.id,
            date=d,
            time=t,
            status="Booked"
        ).first()

        if conflict:
            flash("Doctor is already booked at this time", "danger")
            return redirect(url_for("main.book_appointment", doctor_id=doctor.id))

        appt = Appointment(
            patient_id=current_user.id,
            doctor_id=doctor.id,
            date=d,
            time=t
        )
        db.session.add(appt)
        db.session.commit()

        flash("Appointment booked successfully", "success")
        return redirect(url_for("main.patient_dashboard"))

    return render_template("book_appointment.html", doctor=doctor)
