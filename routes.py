from datetime import datetime
import json
from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from models import db, User, Project, Image, Label, TrainingConfig, Iteration, Deployment

main = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

@main.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'User already exists'}), 409
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@main.route('/projects', methods=['POST'])
def create_project():
    user_id = request.json.get('user_id')
    name = request.json.get('name')
    description = request.json.get('description')
    new_project = Project(name=name, description=description, user_id=user_id)
    db.session.add(new_project)
    db.session.commit()
    return jsonify({'message': 'Project created successfully'}), 201

@main.route('/projects/<int:user_id>', methods=['GET'])
def get_projects(user_id):
    projects = Project.query.filter_by(user_id=user_id).all()
    projects_data = [{'id': p.id, 'name': p.name, 'description': p.description} for p in projects]
    return jsonify(projects_data), 200

@main.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return jsonify({'message': 'Project deleted successfully'}), 200

@main.route('/projects/<int:project_id>/upload_image', methods=['POST'])
def upload_image(project_id):
    file = request.files['image']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        new_image = Image(filename=filename, project_id=project_id)
        db.session.add(new_image)
        db.session.commit()
        return jsonify({'message': 'Image uploaded successfully', 'image_id': new_image.id}), 201

@main.route('/images/<int:image_id>/upload_label', methods=['POST'])
def upload_label(image_id):
    label_data = request.json.get('label_data')
    new_label = Label(image_id=image_id, label_data=label_data)
    db.session.add(new_label)
    db.session.commit()
    return jsonify({'message': 'Label uploaded successfully'}), 201

@main.route('/projects/<int:project_id>/images', methods=['GET'])
def get_images(project_id):
    images = Image.query.filter_by(project_id=project_id).all()
    images_data = [{'id': img.id, 'filename': img.filename} for img in images]
    return jsonify(images_data), 200

@main.route('/projects/<int:project_id>/analyze', methods=['GET'])
def analyze_data(project_id):
    images = Image.query.filter_by(project_id=project_id).all()
    analysis_results = {'total_images': len(images), 'details': []}
    for image in images:
        labels = Label.query.filter_by(image_id=image.id).all()
        analysis_results['details'].append({
            'image_id': image.id,
            'filename': image.filename,
            'labels': [label.label_data for label in labels]
        })
    return jsonify(analysis_results), 200

def save_training_configuration(project_id, config):
    existing_config = TrainingConfig.query.filter_by(project_id=project_id).first()
    if existing_config:
        existing_config.config = config  # Update the existing configuration
    else:
        new_config = TrainingConfig(project_id=project_id, config=config)
        db.session.add(new_config)
    db.session.commit()

@main.route('/projects/<int:project_id>/configure_training', methods=['POST'])
def configure_training(project_id):
    training_params = request.json.get('config')
    save_training_configuration(project_id, training_params)
    return jsonify({'message': 'Training configured successfully'}), 201

@main.route('/projects/<int:project_id>/start_iteration', methods=['POST'])
def start_iteration(project_id):
    iteration = Iteration(project_id=project_id, status='running', result='')
    db.session.add(iteration)
    db.session.commit()
    return jsonify({'message': 'Iteration started', 'iteration_id': iteration.id}), 201

@main.route('/projects/<int:project_id>/iterations/<int:iteration_id>', methods=['GET'])
def get_iteration(project_id, iteration_id):
    iteration = Iteration.query.get_or_404(iteration_id)
    return jsonify({'iteration_id': iteration.id, 'status': iteration.status, 'result': iteration.result}), 200

@main.route('/projects/<int:project_id>/deploy_model', methods=['POST'])
def deploy_model(project_id):
    iteration_id = request.json.get('iteration_id')
    api_key = 'api_' + str(datetime.utcnow().timestamp()).replace('.', '')
    deployment = Deployment(project_id=project_id, iteration_id=iteration_id, api_key=api_key, active=True)
    db.session.add(deployment)
    db.session.commit()
    return jsonify({'message': 'Model deployed', 'api_key': deployment.api_key}), 201

@main.route('/inference', methods=['POST'])
def run_inference():
    api_key = request.headers.get('API-Key')
    if not api_key:
        return jsonify({'error': 'API Key required'}), 401
    deployment = Deployment.query.filter_by(api_key=api_key, active=True).first()
    if not deployment:
        return jsonify({'error': 'Invalid API Key'}), 404
    # Simulate inference process
    image_data = request.files['image']
    if image_data and allowed_file(image_data.filename):
        return jsonify({'result': 'inference result'}), 200
    return jsonify({'error': 'Invalid image format'}), 400
