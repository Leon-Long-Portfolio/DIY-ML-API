import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from models import db, User, Project, Image
from config import TestingConfig

class TestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_configurations(self):
        # Ensure testing config is loaded
        self.assertTrue(self.app.config['TESTING'])
        self.assertEqual(self.app.config['SQLALCHEMY_DATABASE_URI'], 'sqlite:///test.db')

    def test_user_creation(self):
        user = User(username='testuser', password_hash='testpass')
        db.session.add(user)
        db.session.commit()
        self.assertIsNotNone(user.id)

    def test_user_authentication(self):
        user = User(username='testuser')
        user.set_password('test')
        db.session.add(user)
        db.session.commit()
        self.assertTrue(user.check_password('test'))
        self.assertFalse(user.check_password('wrongpassword'))

    def test_project_management(self):
        user = User(username='testuser')
        db.session.add(user)
        project = Project(name='Test Project', description='Test Description', user=user)
        db.session.add(project)
        db.session.commit()
        self.assertEqual(len(user.projects), 1)

    def test_endpoints(self):
        # Test registration endpoint
        response = self.client.post('/register', json={'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(response.status_code, 201)
        
        # Test image upload endpoint
        # You will need to mock file upload functionality
        # Additional tests will check response codes and data integrity for other endpoints

if __name__ == '__main__':
    unittest.main()
