import unittest
import os
import tempfile
import json
import io
from flask_testing import TestCase
from werkzeug.security import generate_password_hash
from models import db, User, Project, Image, Label, TrainingConfig, Iteration, Deployment
from app import create_app

class TestAPI(TestCase):
    def create_app(self):
        # Configure the app for testing with a temporary database
        self.db_fd, self.db_path = tempfile.mkstemp()
        config = {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///" + self.db_path,
            "UPLOAD_FOLDER": tempfile.mkdtemp()
        }
        app = create_app(config)
        return app

    def setUp(self):
        db.create_all()
        user = User(username='testuser', password=generate_password_hash('testpass'))
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        os.close(self.db_fd)
        os.unlink(self.db_path)
        os.rmdir(self.app.config['UPLOAD_FOLDER'])

    def test_register_user(self):
        response = self.client.post('/register', data=json.dumps({
            'username': 'newuser',
            'password': 'newpass'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('User registered successfully', response.json['message'])

    def test_create_project(self):
        response = self.client.post('/projects', data=json.dumps({
            'user_id': 1,
            'name': 'New Project',
            'description': 'A test project'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('Project created successfully', response.json['message'])

    def test_upload_image(self):
        # Assuming test_create_project has already run and created a project with id 1
        data = {
            'image': (io.BytesIO(b"fake image data"), 'test.jpg'),
        }
        response = self.client.post('/projects/1/upload_image', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 201)
        self.assertIn('Image uploaded successfully', response.json['message'])

    def test_upload_label(self):
        # Assuming test_upload_image has already run and uploaded an image with id 1
        label_data = json.dumps({'label_data': 'test label'})
        response = self.client.post('/images/1/upload_label', data=label_data, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('Label uploaded successfully', response.json['message'])

    def test_get_projects(self):
        response = self.client.get('/projects/1')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('New Project' in response.data.decode())

    def test_analyze_data(self):
        response = self.client.get('/projects/1/analyze')
        self.assertEqual(response.status_code, 200)
        self.assertIn('details', response.json)

    def test_configure_training(self):
        config_data = json.dumps({'config': 'test configuration'})
        response = self.client.post('/projects/1/configure_training', data=config_data, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('Training configured successfully', response.json['message'])

    def test_start_iteration(self):
        response = self.client.post('/projects/1/start_iteration')
        self.assertEqual(response.status_code, 201)
        self.assertIn('Iteration started', response.json['message'])

    def test_get_iteration(self):
        # Assuming test_start_iteration has already run and created an iteration with id 1
        response = self.client.get('/projects/1/iterations/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Iteration', response.data.decode())

    def test_deploy_model(self):
        # Assuming test_start_iteration has already run and created an iteration with id 1
        deploy_data = json.dumps({'iteration_id': 1})
        response = self.client.post('/projects/1/deploy_model', data=deploy_data, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('Model deployed', response.json['message'])

    def test_run_inference(self):
        # Assuming test_deploy_model has deployed a model and returned an API key
        api_key = 'test_api_key'
        data = {
            'image': (io.BytesIO(b"fake image data for inference"), 'test.jpg'),
        }
        response = self.client.post('/inference', headers={'API-Key': api_key}, data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        self.assertIn('inference result', response.json['result'])

if __name__ == '__main__':
    unittest.main()
