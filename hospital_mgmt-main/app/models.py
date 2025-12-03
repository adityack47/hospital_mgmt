from datetime import datetime
from app import db
from flask_login import UserMixin

# --------------------
# USER (Admin / Doctor / Patient)
# --------------------
class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False) 
    password_hash = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.id} | {self.role} | {self.email}>"


# --------------------
# DEPARTMENT / SPECIALIZATION
# --------------------
class Department(db.Model):
    __tablename__ = "department"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)

    def __repr__(self):
        return f"<Department {self.name}>"


# --------------------
# DOCTOR PROFILE
# --------------------
class DoctorProfile(db.Model):
    __tablename__ = "doctor_profile"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("department.id"), nullable=False)

    availability = db.Column(db.Text)

    user = db.relationship("User", backref="doctor_profile", lazy=True)
    department = db.relationship("Department", backref="doctors", lazy=True)

    def __repr__(self):
        return f"<DoctorProfile user_id={self.user_id} dept_id={self.department_id}>"


# --------------------
# APPOINTMENT
# --------------------
class Appointment(db.Model):
    __tablename__ = "appointment"

    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default="Booked") 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship(
        "User",
        foreign_keys=[patient_id],
        backref="appointments_as_patient"
    )
    doctor = db.relationship(
        "User",
        foreign_keys=[doctor_id],
        backref="appointments_as_doctor"
    )

    def __repr__(self):
        return f"<Appointment {self.id} {self.date} {self.time} ({self.status})>"


# --------------------
# TREATMENT RECORD
# --------------------
class Treatment(db.Model):
    __tablename__ = "treatment"

    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(
        db.Integer,
        db.ForeignKey("appointment.id"),
        nullable=False
    )
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)

    appointment = db.relationship(
        "Appointment",
        backref=db.backref("treatment", uselist=False)
    )

    def __repr__(self):
        return f"<Treatment appointment_id={self.appointment_id}>"
