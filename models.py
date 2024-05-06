from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    projects = db.relationship('Project', backref='user', lazy=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    project_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)  # Adding description field
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
    config = db.Column(db.Text)

class Iteration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    status = db.Column(db.String(20), nullable=False)
    result = db.Column(db.Text)

class Deployment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    iteration_id = db.Column(db.Integer, db.ForeignKey('iteration.id'))
    api_key = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True)
    iteration = db.relationship('Iteration', backref='deployment', uselist=False)
