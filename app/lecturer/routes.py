import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User, Attendance, Grade, VALID_LECTURER_IDS

lecturer_bp = Blueprint('lecturer', __name__, template_folder='templates')


# ---------- Sign Up ----------
@lecturer_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        lecturer_id = request.form.get("lecturer_id")
        username = request.form.get("username")
        password = request.form.get("password")

        if lecturer_id not in VALID_LECTURER_IDS:
            flash("Invalid lecturer ID!")
            return redirect(url_for('lecturer.signup'))

        if User.query.filter_by(user_id=lecturer_id).first():
            flash("Account already exists!")
            return redirect(url_for('lecturer.signup'))

        hashed_pw = generate_password_hash(password)
        new_lecturer = User(user_id=lecturer_id, role="lecturer", username=username, password=hashed_pw)
        db.session.add(new_lecturer)
        db.session.commit()

        flash("Signup successful! Please login.")
        return redirect(url_for('lecturer.login'))

    return render_template("lecturer/signup.html")


# ---------- Login ----------
@lecturer_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        lecturer_id = request.form.get("lecturer_id")
        password = request.form.get("password")

        lecturer = User.query.filter_by(user_id=lecturer_id, role="lecturer").first()
        if lecturer and check_password_hash(lecturer.password, password):
            # Use JSON-string identity
            identity_str = json.dumps({"id": lecturer.id, "role": lecturer.role})
            access_token = create_access_token(identity=identity_str)
            refresh_token = create_refresh_token(identity=identity_str)

            # Set tokens in cookies
            resp = make_response(redirect(url_for('lecturer.dashboard')))
            resp.set_cookie("access_token_cookie", access_token)
            resp.set_cookie("refresh_token_cookie", refresh_token)
            flash("Login successful!")
            return resp

        flash("Invalid login credentials!")
    return render_template("lecturer/login.html")


# ---------- Logout ----------
@lecturer_bp.route("/logout")
def logout():
    resp = make_response(redirect(url_for('lecturer.login')))
    resp.delete_cookie("access_token_cookie")
    resp.delete_cookie("refresh_token_cookie")
    flash("Logged out successfully!")
    return resp


# ---------- Refresh Token ----------
@lecturer_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity_str = get_jwt_identity()
    access_token = create_access_token(identity=identity_str)
    resp = make_response({"msg": "Access token refreshed"})
    resp.set_cookie("access_token_cookie", access_token)
    return resp


# ---------- Dashboard ----------
@lecturer_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    identity_str = get_jwt_identity()
    identity = json.loads(identity_str)
    lecturer_id = identity["id"]

    page = request.args.get('page', 1, type=int)
    students = User.query.filter_by(role="student").paginate(page=page, per_page=5)
    return render_template("lecturer/dashboard.html", students=students)


# ---------- Mark Attendance ----------
@lecturer_bp.route("/attendance/<int:student_id>", methods=["POST"])
@jwt_required()
def mark_attendance(student_id):
    identity_str = get_jwt_identity()
    identity = json.loads(identity_str)

    status = request.form.get("status")
    new_attendance = Attendance(student_id=student_id, status=status)
    db.session.add(new_attendance)
    db.session.commit()
    flash("Attendance marked successfully!")
    return redirect(url_for('lecturer.dashboard'))


# ---------- Assign or Update Grade ----------
@lecturer_bp.route("/grade/<int:student_id>", methods=["POST"])
@jwt_required()
def assign_grade(student_id):
    identity_str = get_jwt_identity()
    identity = json.loads(identity_str)

    exam_name = request.form.get("exam_name")
    score = float(request.form.get("score"))
    grade = request.form.get("grade")

    existing_grade = Grade.query.filter_by(student_id=student_id, exam_name=exam_name).first()
    if existing_grade:
        existing_grade.score = score
        existing_grade.grade = grade
    else:
        new_grade = Grade(student_id=student_id, exam_name=exam_name, score=score, grade=grade)
        db.session.add(new_grade)

    db.session.commit()
    flash("Grade saved successfully!")
    return redirect(url_for('lecturer.dashboard'))
