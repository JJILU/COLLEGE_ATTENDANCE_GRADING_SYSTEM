from app.extensions import db
from datetime import datetime

# Pre-made list of valid IDs
VALID_STUDENT_IDS = ["S1001", "S1002", "S1003"]
VALID_LECTURER_IDS = ["L2001", "L2002"]

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False)  # StudentID or LecturerID
    role = db.Column(db.String(10), nullable=False)  # "student" or "lecturer"
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(200), nullable=False)

    attendances = db.relationship('Attendance', backref='student', lazy=True)
    grades = db.relationship('Grade', backref='student', lazy=True)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(10), nullable=False)  # Present or Absent
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_name = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Float, nullable=False)
    grade = db.Column(db.String(5), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
