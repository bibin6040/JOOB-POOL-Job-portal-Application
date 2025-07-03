# 🧑‍💼 Job Portal Web Application

A Django-based job portal allowing users to register, apply for jobs, and employers/admins to manage listings and applications. Includes external job API integration.

---

## 🚀 Features

- User registration and login (User, Employer, Admin)
- Employers can:
  - Post, edit, delete job listings
  - View applications for their jobs
- Users can:
  - Browse and apply for jobs
  - View their applications
- Admin panel to manage:
  - Users, employers, jobs, applications
- 📡 External job listings via job API
- File upload support (resume)
- Status tracking (Pending, Under Review, Accepted, etc.)

---

## 🧑‍💻 Technologies Used

- Python 3.12
- Django 5.x
- SQLite (default) or PostgreSQL (optional)
- Bootstrap 5 (for UI)
- Chart.js (for admin dashboard stats)
- Job API via `requests`

---

## 📦 Setup Instructions

### 1️⃣ Clone the Repository


git clone https://github.com/your-username/job-portal.git
cd job-portal
2️⃣ Set up Virtual Environment

python -m venv env
source env/bin/activate  # on Windows use: env\Scripts\activate
3️⃣ Install Dependencies

pip install -r requirements.txt
4️⃣ Migrate the Database

python manage.py makemigrations
python manage.py migrate
5️⃣ Create Superuser (Admin)

python manage.py createsuperuser
6️⃣ Run the Server

python manage.py runserver
Then go to: http://127.0.0.1:8000/

🌐 External Job API
This project uses job APIs to fetch real job listings. Example:

Remotive API

[RapidAPI - CareerJet, Adzuna, etc.]

You can configure your API key in views.py or use .env file to store keys securely.

📁 Folder Structure

jobportal/
├── job/                    # Django app
├── templates/              # HTML templates
├── static/                 # CSS, JS, images
├── media/                  # Uploaded resumes
├── requirements.txt
├── README.md
└── manage.py
✅ To Do
Add email notifications

Pagination and filtering for jobs

Add Docker support

📄 License
MIT License. Free to use and modify.

