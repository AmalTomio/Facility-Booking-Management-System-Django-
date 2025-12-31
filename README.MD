# 🏢 Facility Booking System

A Flask-based facility booking system with **Admin** and **Staff** roles.

Staff can request facility bookings, while Admins manage facilities and approve/reject bookings.

---

## ✨ Features

### 👤 Authentication

- Login & Register
- Role-based access (Admin / Staff)

### 🏢 Facilities

- Admin: Add, edit, delete facilities
- Image upload for facilities
- Active / inactive status

### 📅 Bookings

- Staff: Create booking requests
- Admin: Approve / reject bookings
- Staff: View booking history & upcoming bookings

### 📊 Dashboard

- Admin statistics
- Staff personal booking stats

---

## 🧰 Tech Stack

- **Backend:** Flask 3
- **Frontend:** Bootstrap 5
- **Database:** MySQL / MariaDB
- **Auth:** Flask-Login
- **Forms:** Flask-WTF
- **Password Hashing:** Flask-Bcrypt

---

## 📂 Project Structure

booking-system/
│
├── app.py
├── models.py
├── forms.py
├── database.py
├── config.py
├── requirements.txt
│
├── templates/
│ ├── layouts/
│ ├── components/
│ ├── admin/
│ ├── staff/
│ └── auth.html
│
├── static/
│ ├── css/
│ ├── js/
│ └── uploads/ (ignored by git)
│
└── .gitignore

yaml
Copy code

---

## 🚀 Getting Started (For Contributors)

### 1️⃣ Clone the Repository

````bash
git clone https://github.com/YOUR_USERNAME/booking-system.git
cd booking-system
2️⃣ Create Virtual Environment
Windows
bash
Copy code
python -m venv venv
venv\Scripts\activate
macOS / Linux
bash
Copy code
python3 -m venv venv
source venv/bin/activate
3️⃣ Install Dependencies
bash
Copy code
pip install -r requirements.txt
4️⃣ Configure Environment Variables
Create a .env file in the project root:

env
Copy code
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_db_password
DB_NAME=booking_system
⚠️ Important:
.env is ignored by Git. Do NOT commit it.

5️⃣ Setup Database
Create the database manually in MySQL:

sql
Copy code
CREATE DATABASE booking_system;
Make sure your MySQL server is running.

The app will automatically initialize required tables on first run.

6️⃣ Run the Application
bash
Copy code
flask run
or

bash
Copy code
python app.py
7️⃣ Access the App
🌐 App URL:
👉 http://127.0.0.1:5000

👥 User Roles
🛠 Admin
Manage facilities

Approve / reject bookings

View system statistics

👨‍💼 Staff
Browse facilities

Request bookings

View booking history

🤝 Contribution Guide
🔀 Branching
Always create a new branch:

bash
Copy code
git checkout -b feature-your-feature-name
💾 Commit Changes
bash
Copy code
git add .
git commit -m "Describe your changes"
git push origin feature-your-feature-name
🔁 Pull Request
Open a Pull Request on GitHub

Wait for review before merging

❌ Do NOT push directly to main

🛑 Git Rules
❌ Do not commit:

venv/

.env

static/uploads/

Database credentials

🧪 Default Admin Account (Optional)
You can manually insert an admin user in MySQL:

sql
Copy code
INSERT INTO users (name, email, password, role)
VALUES ('Admin', 'admin@example.com', '<hashed_password>', 'admin');
Or register via UI and update role to admin.

📌 Notes
This project is for educational purposes

Feel free to refactor, improve UI, or add features

🧑‍💻 Author
Developed by Amal & contributors ❤️

yaml
Copy code

---

# ✅ FINAL STEP — COMMIT README

```powershell
git add README.md
git commit -m "Add setup guide to README"
git push
````
