from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, Project, Image, Label, TrainingConfig, Iteration, Deployment
import os
import json
import tensorflow as tf
import datetime
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
from tensorflow.keras.layers import TFSMLayer
from PIL import Image as PILImage


main = Blueprint('main', __name__)

# Load pre-trained MobileNetV2 model
default_model = tf.keras.applications.MobileNetV2(weights='imagenet', include_top=True)
default_model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

user_model = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

@main.route('/')
def home():
    print("Is authenticated:", current_user.is_authenticated)
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('home.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route('/dashboard')
@login_required
def dashboard():
    projects = Project.query.filter_by(user_id=current_user.id).all()
    projects_details = []
    for project in projects:
        analysis = analyze_project(project.id)
        projects_details.append({
            'id': project.id,
            'name': project.name,
            'description': getattr(project, 'description', 'No description provided'),
            'analysis': analysis
        })
    return render_template('dashboard.html', projects=projects, projects_details=projects_details)

@main.route('/upload_model', methods=['POST'])
@login_required
def upload_model():
    file = request.files.get('model')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        global user_model
        user_model = tf.keras.models.load_model(filepath)
        flash('Model uploaded successfully.')
    else:
        flash('Failed to upload model or file type not allowed.')
    return redirect(url_for('main.dashboard'))

@main.route('/projects/<int:project_id>/predict', methods=['GET', 'POST'])
@login_required
def predict(project_id):
    if request.method == 'POST':
        image_id = request.form.get('image_id')
        image_record = Image.query.get_or_404(image_id)  # Ensure the image ID exists in the database
        img_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_record.filename)

        try:
            img = load_img(img_path, target_size=(224, 224))
            x = img_to_array(img)
            x = np.expand_dims(x, axis=0)
            x = preprocess_input(x)

            deployment = Deployment.query.filter_by(project_id=project_id, active=True).first()
            if not deployment:
                flash('No active deployment found for this project.')
                return redirect(url_for('main.manage_project', project_id=project_id))

            model_path = deployment.iteration.model_path if deployment.iteration_id else 'path/to/default_model'
            if model_path.endswith('.h5'):
                model_to_use = tf.keras.models.load_model(model_path)
            else:
                model_to_use = default_model  # Fallback to default model if no custom model is loaded

            predictions = model_to_use.predict(x)  # Use predict method
            predicted_classes = decode_predictions(predictions, top=3)[0]  # Ensure to decode predictions
            return render_template('results.html', predictions=predicted_classes, project_id=project_id)
        except Exception as e:
            flash(f'Error in prediction: {str(e)}')
            return redirect(url_for('main.manage_project', project_id=project_id))

    elif request.method == 'GET':
        images = Image.query.filter_by(project_id=project_id).all()
        return render_template('predict.html', project_id=project_id, images=images)

    return jsonify({'error': 'Method not supported'}), 405

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            return redirect(url_for('main.dashboard'))  # Redirect to dashboard
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('main.register'))
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)  # Log in user immediately after registration
        return redirect(url_for('main.dashboard'))
    return render_template('register.html')

@main.route('/projects/create', methods=['GET', 'POST'])
@login_required
def create_project():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        project_type = request.form['project_type']
        new_project = Project(name=name, description=description, project_type=project_type, user_id=current_user.id)
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for('main.dashboard'))
    return render_template('create_project.html')

@main.route('/projects/<int:project_id>/manage', methods=['GET'])
@login_required
def manage_project(project_id):
    project = Project.query.get_or_404(project_id)
    images = Image.query.filter_by(project_id=project_id).all()
    return render_template('manage_project.html', project=project, images=images)

@main.route('/projects/<int:project_id>/upload_image', methods=['GET', 'POST'])
@login_required
def upload_image(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            new_image = Image(filename=filename, project_id=project_id)
            db.session.add(new_image)
            db.session.commit()
            flash('Image uploaded successfully')
        return redirect(url_for('main.manage_project', project_id=project_id))
    return render_template('upload_image.html', project=project, project_id=project_id)


@main.route('/projects/<int:user_id>', methods=['GET'])
def get_projects(user_id):
    projects = Project.query.filter_by(user_id=user_id).all()
    projects_data = [{'id': p.id, 'name': p.name, 'description': p.description} for p in projects]
    return jsonify(projects_data), 200

@main.route('/projects/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash("You do not have permission to delete this project.")
        return redirect(url_for('main.dashboard'))

    if request.form.get('_method') == 'DELETE':
        db.session.delete(project)
        db.session.commit()
        flash('Project deleted successfully')
        return redirect(url_for('main.dashboard'))

    flash('Invalid request method')
    return redirect(url_for('main.manage_project', project_id=project_id))

@main.route('/projects/<int:project_id>/images', methods=['GET'])
@login_required
def get_images(project_id):
    images = Image.query.filter_by(project_id=project_id).all()
    images_data = [{'id': img.id, 'filename': img.filename} for img in images]
    return jsonify(images_data), 200

@main.route('/projects/<int:project_id>/analyze', methods=['GET'])
@login_required
def analyze_project(project_id):
    project = Project.query.get_or_404(project_id)
    images = Image.query.filter_by(project_id=project_id).all()
    analysis_results = {'total_images': len(images), 'details': []}
    for image in images:
        labels = Label.query.filter_by(image_id=image.id).all()
        analysis_results['details'].append({
            'image_id': image.id,
            'filename': image.filename,
            'labels': [label.label_data for label in labels]
        })
    return analysis_results

@main.route('/projects/<int:project_id>/configure_training', methods=['GET', 'POST'])
@login_required
def configure_training(project_id):
    if request.method == 'POST':
        if request.is_json:  # Changed from request.content_type
            training_params = request.get_json()
            config = TrainingConfig(project_id=project_id, config=json.dumps(training_params))
            db.session.add(config)
            db.session.commit()
            return jsonify({'message': 'Training configured successfully', 'config': training_params}), 201
        else:
            return jsonify({'error': 'Unsupported Media Type, please use JSON'}), 415
    else:
        return render_template('configure_training.html', project_id=project_id)

@main.route('/projects/<int:project_id>/start_iteration', methods=['POST', 'GET'])
@login_required
def start_iteration(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'GET':
        iterations = Iteration.query.filter_by(project_id=project_id).all()
        return render_template('start_iteration.html', project=project, iterations=iterations)
    elif request.method == 'POST':
        # Simulate starting a new training iteration
        iteration = Iteration(project_id=project_id, status='running', result='')
        db.session.add(iteration)
        db.session.commit()
        
        iteration.status = 'completed'
        iteration.result = 'Training completed successfully'
        db.session.commit()
        
        return jsonify({'message': 'Iteration started and completed', 'iteration_id': iteration.id}), 201

@main.route('/projects/<int:project_id>/iterations/<int:iteration_id>', methods=['GET'])
@login_required
def get_iteration(project_id, iteration_id):
    iteration = Iteration.query.get_or_404(iteration_id)
    return jsonify({'iteration_id': iteration.id, 'status': iteration.status, 'result': iteration.result}), 200

@main.route('/projects/<int:project_id>/deploy_model', methods=['POST', 'GET'])
@login_required
def deploy_model(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'GET':
        iterations = Iteration.query.filter_by(project_id=project_id).all()
        return render_template('deploy_model.html', project=project, iterations=iterations, default_model_id=-1)
    elif request.method == 'POST':
        model_choice = request.form.get('model_choice')
        if model_choice == 'default':
            model_to_deploy = default_model
        else:
            selected_iteration = Iteration.query.get_or_404(model_choice)
            model_to_deploy = tf.keras.models.load_model(selected_iteration.model_path)

        api_key = 'api_' + str(datetime.datetime.utcnow().timestamp()).replace('.', '')
        deployment = Deployment(project_id=project_id, iteration_id=(None if model_choice == 'default' else model_choice), api_key=api_key, active=True)
        db.session.add(deployment)
        db.session.commit()
        flash('Model deployed successfully. API Key: ' + api_key)

        return redirect(url_for('main.predict', project_id=project_id))

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
        filename = secure_filename(image_data.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        image_data.save(filepath)

        # Here you might perform some actual inference using the deployed model
        return jsonify({'result': 'inference result'}), 200
    return jsonify({'error': 'Invalid image format'}), 400

@main.route('/images/<int:image_id>/delete', methods=['POST'])
@login_required
def delete_image(image_id):
    image = Image.query.get_or_404(image_id)
    project = Project.query.get_or_404(image.project_id)  # Corrected this line
    if project.user_id != current_user.id:
        flash("You do not have permission to delete this image.")
        return redirect(url_for('main.manage_project', project_id=project.id))

    db.session.delete(image)
    db.session.commit()
    flash('Image deleted successfully')
    return redirect(url_for('main.manage_project', project_id=project.id))

@main.route('/projects/<int:project_id>/iterations/<int:iteration_id>/delete', methods=['POST'])
@login_required
def delete_iteration(project_id, iteration_id):
    project = Project.query.get_or_404(project_id)  # Fetch the project first
    iteration = Iteration.query.get_or_404(iteration_id)
    if iteration.project_id != project_id or project.user_id != current_user.id:
        flash("You do not have permission to delete this iteration.")
        return redirect(url_for('main.manage_project', project_id=project_id))

    db.session.delete(iteration)
    db.session.commit()
    flash('Iteration deleted successfully')
    return redirect(url_for('main.manage_project', project_id=project_id))
