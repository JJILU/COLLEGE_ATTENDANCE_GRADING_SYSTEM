import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity,set_access_cookies, set_refresh_cookies
from app.extensions import db
from app.models import User, Attendance, Grade, VALID_STUDENT_IDS
from datetime import datetime
import json

student_bp = Blueprint('student', __name__, template_folder='templates')


# ---------- Sign Up ----------
@student_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        student_id = request.form.get("student_id")
        username = request.form.get("username")
        password = request.form.get("password")

        if student_id not in VALID_STUDENT_IDS:
            flash("Invalid student ID!")
            return redirect(url_for('student.signup'))

        if User.query.filter_by(user_id=student_id).first():
            flash("Account already exists!")
            return redirect(url_for('student.signup'))

        hashed_pw = generate_password_hash(password)
        new_student = User(user_id=student_id, role="student", username=username, password=hashed_pw)
        db.session.add(new_student)
        db.session.commit()

        flash("Signup successful! Please login.")
        return redirect(url_for('student.login'))

    return render_template("student/signup.html")


# ---------- Login ----------
@student_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        student_id = request.form.get("student_id")
        password = request.form.get("password")

        student = User.query.filter_by(user_id=student_id, role="student").first()
        if student and check_password_hash(student.password, password):
            identity_str = json.dumps({"id": student.id, "role": student.role})
            access_token = create_access_token(identity=identity_str)
            refresh_token = create_refresh_token(identity=identity_str)

            resp = make_response(redirect(url_for('student.dashboard')))
            set_access_cookies(resp, access_token)
            set_refresh_cookies(resp, refresh_token)
            flash("Login successful!")
            return resp

        flash("Invalid login credentials!")
    return render_template("student/login.html")

# ---------- Logout ----------
@student_bp.route("/logout")
def logout():
    resp = make_response(redirect(url_for('student.login')))
    resp.delete_cookie("access_token_cookie")
    resp.delete_cookie("refresh_token_cookie")
    flash("Logged out successfully!")
    return resp


# ---------- Refresh Token ----------
@student_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    # Get identity from refresh token
    identity_str = get_jwt_identity()
    
    # Create new access token
    access_token = create_access_token(identity=identity_str)
    
    # Create response
    resp = make_response({"msg": "Access token refreshed"})
    
    # Set access token in cookie
    set_access_cookies(resp, access_token)
    
    return resp

# ---------- Dashboard: View Attendance and Grades ----------
@student_bp.route("/dashboard")
@jwt_required()
def dashboard():
    identity_str = get_jwt_identity()
    identity = json.loads(identity_str)
    student_id = identity["id"]
    role = identity["role"]  # Pass this

    student = User.query.get(student_id)
    attendances = Attendance.query.filter_by(student_id=student.id).all()
    grades = Grade.query.filter_by(student_id=student.id).all()

    return render_template(
        "student/dashboard.html",
        student=student,
        attendances=attendances,
        grades=grades,
        current_user_role=role  # <-- pass role
    )



@student_bp.route("/attendance")
@jwt_required()
def student_attendance():
    identity = json.loads(get_jwt_identity())
    if identity["role"] != "student":
        flash("Access denied!")
        return redirect(url_for("lecturer.dashboard"))

    attendances = Attendance.query.filter_by(student_id=identity["id"]).all()
    return render_template("student/attendance.html", attendances=attendances)


@student_bp.route("/grades")
@jwt_required()
def student_grades():
    identity = json.loads(get_jwt_identity())
    if identity["role"] != "student":
        flash("Access denied!")
        return redirect(url_for("lecturer.dashboard"))

    grades = Grade.query.filter_by(student_id=identity["id"]).all()
    return render_template("student/grades.html", grades=grades)
