from flask import Flask
from config import Config
from app.extensions import db, migrate, jwt

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]  # JWT stored in cookies
    app.config["JWT_ACCESS_COOKIE_PATH"] = "/"
    app.config["JWT_REFRESH_COOKIE_PATH"] = "/refresh"
    app.config["JWT_COOKIE_SECURE"] = False  # True if using HTTPS
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # Optional for simplicity

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Make app aware of models existance
    from .models import User, Attendance, Grade

    # Import blueprints
    from app.student.routes import student_bp
    from app.lecturer.routes import lecturer_bp
    

    app.register_blueprint(student_bp, url_prefix="/student")
    app.register_blueprint(lecturer_bp, url_prefix="/lecturer")

    return app
