from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Define User table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)
    set_status = db.relationship("UserStatus")


# Define UserStatus table
class UserStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    urconst = db.Column(db.String(8), nullable=False)
    status = db.Column(db.String(150), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    setting_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    setting_user_name = db.Column(db.String(20), nullable=False)
