# test_app.py
import os
import tempfile
import pytest
from flask import template_rendered
from contextlib import contextmanager
from werkzeug.security import generate_password_hash
from app import create_app
from models import db, User, Project, Image

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'UPLOAD_FOLDER': tempfile.mkdtemp(),
    })

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def runner(client):
    return client.application.test_cli_runner()

def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

@pytest.fixture
def auth(client):
    user = User(username='test', password_hash=generate_password_hash('test'))
    db.session.add(user)
    db.session.commit()

    return user

def test_register(client):
    # Test that view works
    assert client.get('/register').status_code == 200
    # Test that successful registration redirects to the dashboard
    response = client.post('/register', data={'username': 'a', 'password': 'a'}, follow_redirects=True)
    assert b'Redirecting' in response.data

def test_login_logout(client, auth):
    # Test logging in with valid credentials
    response = login(client, 'test', 'test')
    assert b'dashboard' in response.data

    # Test logging out
    response = logout(client)
    assert b'home' in response.data

    # Test that logging in with invalid credentials gives an error
    response = login(client, 'wrong', 'wrong')
    assert b'Invalid username or password' in response.data

def test_dashboard_access(client, auth):
    # Test access without login
    response = client.get('/dashboard')
    assert response.headers['Location'] == 'http://localhost/login'

    # Test access with login
    login(client, 'test', 'test')
    response = client.get('/dashboard')
    assert b'Your Projects' in response.data 

def test_project_creation(client, auth):
    # Ensure authentication
    login(client, 'test', 'test')
    
    # Test valid project creation
    response = client.post('/projects/create', data={
        'name': 'New Project',
        'description': 'A test project',
        'project_type': 'Type1'
    }, follow_redirects=True)
    assert b'Project created successfully' in response.data 

    # Test invalid project creation (e.g., missing name)
    response = client.post('/projects/create', data={
        'description': 'A test project',
        'project_type': 'Type1'
    }, follow_redirects=True)
    assert b'Error: Name is required' in response.data 

