from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    projects = db.relationship('Project', backref='user', lazy=True)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    project_type = db.Column(db.String(50), nullable=False)  # 'classification' or 'detection'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(128), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    labels = db.relationship('Label', backref='image', lazy=True)

class Label(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    label_data = db.Column(db.Text, nullable=False)

class TrainingConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    config = db.Column(db.Text)  # JSON formatted string
    project = db.relationship('Project', backref=db.backref('training_config', uselist=False))

class Iteration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    status = db.Column(db.String(20), nullable=False)  # e.g., 'pending', 'running', 'completed'
    result = db.Column(db.Text)  # JSON formatted string with results/stats

class Deployment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    iteration_id = db.Column(db.Integer, db.ForeignKey('iteration.id'))
    api_key = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True)
    iteration = db.relationship('Iteration', backref=db.backref('deployment', uselist=False))
