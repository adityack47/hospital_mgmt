# 🏥 Hospital Management System

A web-based Hospital Management System developed using **Flask** that enables efficient hospital operations by managing doctors, patients, appointments, and medical records. The system provides role-based access with dedicated dashboards for **Admin**, **Doctor**, and **Patient** users.

---

## ✨ Features Overview

### 🔑 User Roles

#### 👨‍💼 Admin
- Add, update, and manage doctors
- Create and manage medical departments
- Search patients, doctors, and specializations
- View all appointments in the system
- Activate or deactivate doctor and patient accounts

#### 👨‍⚕️ Doctor
- View daily and weekly appointments
- Update availability for the next 7 days
- Complete appointments by adding diagnosis and prescriptions
- Access patient treatment history

#### 🧑‍⚕️ Patient
- Self register and login
- Browse doctors by specialization and availability
- Book, reschedule, or cancel appointments
- View appointment and treatment history
- Update personal profile details

---

## ⚙️ Technologies Used

- **Backend:** Flask (Python)
- **Frontend:** HTML, Bootstrap, Jinja2
- **Database:** SQLite (SQLAlchemy ORM)
- **Authentication:** Flask-Login

---

## 📁 Project Structure

hospital_mgmt/
│
├── app/
│ ├── init.py
│ ├── models.py
│ ├── routes.py
│ ├── templates/
│ └── static/
│
├── config.py
├── run.py
└── README.md


---

## 🗄 Database Design (Overview)

- **User:** Stores admin, doctor, and patient details
- **Department:** Stores medical specializations
- **DoctorProfile:** Links doctors to departments and availability
- **Appointment:** Handles booking and appointment status
- **Treatment:** Stores diagnosis, prescriptions, and notes

✔ The schema ensures that no doctor has multiple appointments at the same date and time.

---

## 🚀 Running the Application Locally

1️⃣ Install Dependencies
```
pip install -r requirements.txt
```

2️⃣ Start the Application
```
python run.py
```

3️⃣ Open in Browser
http://127.0.0.1:5000

🔐 Default Admin Credentials

These credentials are created automatically on the first run:

- Email: admin@hospital.com

- Password: admin123

✅ Core Functionalities Implemented

- Role-based authentication and dashboards

- Appointment booking with conflict prevention

- Dynamic appointment status updates

- Treatment history storage and access

- Search functionality across users and departments
