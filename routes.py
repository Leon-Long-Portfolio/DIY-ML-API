from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Project, Image
from werkzeug.utils import secure_filename

main = Blueprint('main', __name__)

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

@main.route('/projects/<int:project_id>/upload', methods=['POST'])
def upload_image(project_id):
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        new_image = Image(filename=filename, project_id=project_id)
        db.session.add(new_image)
        db.session.commit()
        return jsonify({'message': 'Image uploaded successfully'}), 201

@main.route('/projects/<int:project_id>/images', methods=['GET'])
def get_images(project_id):
    images = Image.query.filter_by(project_id=project_id).all()
    images_data = [{'id': img.id, 'filename': img.filename} for img in images]
    return jsonify(images_data), 200
