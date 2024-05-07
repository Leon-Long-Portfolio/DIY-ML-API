# DIY Machine Learning API Application

## Project Overview

Welcome to Flask ML Project Manager! This application provides a platform for managing machine learning projects, allowing users to log in, create and manage projects, upload images for classification or object detection, and even upload their own models for training and deployment within the application.

## Video Demonstration



https://github.com/Leon-Long-Portfolio/DIY-ML-API/assets/153784947/dd7eab49-3a06-4782-94c5-1781930b4278



## Features

- **User Authentication**: Users can register, log in, and log out securely.
- **Project Management**: Users can create, view, update, and delete their machine learning projects.
- **Image Upload**: Users can upload images for classification or object detection tasks within their projects.
- **Model Upload and Deployment**: Users can upload their own machine learning models for training and deployment within the application.

## Technologies Used

- **Flask**: Flask is used as the web framework for building the application.
- **SQLAlchemy**: SQLAlchemy is used as the ORM (Object-Relational Mapping) tool for database interactions.
- **SQLite**: SQLite is used as the database system for storing user data, project information, and uploaded images/models.
- **TensorFlow/Keras**: TensorFlow and Keras are used for machine learning model training and deployment.
- **HTML/CSS/JavaScript**: Frontend components are built using these web technologies.

## Installation

1. Clone the repository: `git clone https://github.com/Leon-Long-Portfolio/DIY-ML-API`
2. Navigate to Project Directory: `cd DIY-ML-API`
3. Build Docker Image: `docker build -t my-python-app .`
4. Run the Docker Container: `docker run -p 5001:5000 my-python-app`
5. Access the application in your web browser at `http://localhost:5000`.

## Usage

1. Register or log in to your account.
2. Create a new project or select an existing project.
3. Upload images for classification or object detection tasks.
4. Optionally, upload your own machine learning model for training and deployment.
5. View project details, manage projects, and deploy models as needed.

## Project Design

### RESTFUL API Definitions

### Authentication and User Management

- `POST /login`: Authenticate and log in a user.
- `POST /register`: Register a new user.
- `POST /logout`: Log out the current user.

### Project Management

- `GET /dashboard`: Display the dashboard with user projects and analyses.
- `POST /projects/create`: Create a new project.
- `GET /projects/<int:project_id>/manage`: Manage a specific project.
- `POST /projects/<int:project_id>`: Delete a specific project.

### Image Management

- `POST /projects/<int:project_id>/upload_image`: Upload an image to a project.
- `GET /projects/<int:project_id>/images`: Retrieve all images associated with a project.
- `POST /images/<int:image_id>/delete`: Delete a specific image.

### Model Operations

- `POST /upload_model`: Upload a custom ML model.
- `GET /projects/<int:project_id>/predict`: Display the prediction form.
- `POST /projects/<int:project_id>/predict`: Perform predictions using the deployed model.
- `POST /projects/<int:project_id>/deploy_model`: Deploy a model for a project.

### Training and Iterations

- `POST /projects/<int:project_id>/start_iteration`: Start a new training iteration for a project.
- `GET /projects/<int:project_id>/iterations/<int:iteration_id>`: Retrieve specific iteration details.
- `POST /projects/<int:project_id>/iterations/<int:iteration_id>/delete`: Delete a specific iteration.

### Miscellaneous

- `POST /inference`: Perform inference using an API key.
- `GET /projects/<int:user_id>`: Retrieve all projects for a specific user.

### SQL Database Design

#### `User`
- `id`: Integer, primary key
- `username`: String(64), unique
- `password_hash`: String(128)
- Relationships: One-to-many with `Project`

#### `Project`
- `id`: Integer, primary key
- `name`: String(128), not nullable
- `project_type`: String(50), not nullable
- `description`: Text, nullable
- `user_id`: Integer, foreign key to `User`
- Relationships: One-to-many with `Image`, `TrainingConfig`, `Iteration`, `Deployment`

#### `Image`
- `id`: Integer, primary key
- `filename`: String(128), not nullable
- `project_id`: Integer, foreign key to `Project`
- Relationships: One-to-many with `Label`

#### `Label`
- `id`: Integer, primary key
- `image_id`: Integer, foreign key to `Image`
- `label_data`: Text, not nullable

#### `TrainingConfig`
- `id`: Integer, primary key
- `project_id`: Integer, foreign key to `Project`
- `config`: Text

#### `Iteration`
- `id`: Integer, primary key
- `project_id`: Integer, foreign key to `Project`
- `status`: String(20), not nullable
- `result`: Text

#### `Deployment`
- `id`: Integer, primary key
- `project_id`: Integer, foreign key to `Project`
- `iteration_id`: Integer, foreign key to `Iteration`, nullable
- `api_key`: String(128), unique, not nullable
- `active`: Boolean, default true
- Relationships: One-to-one with `Iteration`

## Project Development

### Project Requirements

1. RESTFUL APIs for DIY ML API App includes User Management, Project Management, Image Uploader, Training Configuration, and Training Analysis.
2. Each module is tested utilizing the test_app.
3. Database: Implemented relational-based SQL
4. Queueing and Multi-threading capacity for asynchronous activity

### Phase 1 - Software Development: REST APIs and Modularity

#### Phase 1.1

Data Upload Module:
- API user should be able to upload data (images) for training in a project
- API user should be able to upload label or class data for images in a project

Training Module:
- API user should be able to add or remove training points
- API user should be able to configure training parameters
- API user should be able to run and track iterations of training
- API user should be able to analyze data before training

#### Phase 1.2

User Module (Authentication and Authorization):
- A project is associated with a user

Project Module:
- API user should be able to create a ML image classification or Object detection project for Training and Inference

Data Analysis Module:
- API user should be able when the training is completed to get training stats

Test Model Module:
- API user should be able to test a model using new dataset and get results

Model Module:
- API user should be able to deploy a model to be used for inference and should be able to get a unique API to use for a project-iteration combination
- ALL APIs should be independent of the ML model and data

Inference Module:
- API user should be able to use inference API to run and get results on an image

### Phase 2 - Database Implementation: Relational-Base SQL and Possible MongoDB Schema Implementation

Base on the requirements, the following preliminary schema shows the various tables with their respective relationships. The SQL schema consists of multiple tables including User, Project, Image, TrainingConfig, TrainingResult, and InferenceResult. Each table is designed to efficiently store and manage different aspects of machine learning training processes.

#### User
id: Primary key, integer
username: String, unique, non-nullable
password_hash: String

Relationships:
projects: One-to-many with Project

#### Project
id: Primary key, integer
user_id: Foreign key from User, non-nullable, cascades on delete
project_type: String, non-nullable
name: String, nullable

Relationships:
images: One-to-many with Image
training_config: One-to-one with TrainingConfig

#### Image
id: Primary key, integer
filename: String, non-nullable
label: String, nullable
feature_size: Float, nullable
project_id: Foreign key from Project, non-nullable, cascades on delete

#### TrainingConfig
id: Primary key, integer
project_id: Foreign key from Project, non-nullable, cascades on delete
learning_rate: Float, non-nullable, default 0.001
epochs: Integer, non-nullable, default 10
batch_size: Integer, non-nullable, default 32

Relationships:
project: Back-populates from Project

### MongoDB Schema Possible Implementation

Based on the application's requirements, here's a possible MongoDB schema:

#### User Collection
username: String, unique
password_hash: String
projects: Array of references to Project documents

#### Project Document
user_id: Reference to User document
project_type: String
name: String
images: Array of references to Image documents
training_config: Embedded document (TrainingConfig)

#### Image Document
filename: String
label: String
feature_size: Float
project_id: Reference to Project document

#### TrainingConfig Embedded Document
learning_rate: Float
epochs: Integer
batch_size: Integer

This MongoDB schema uses both embedded documents and references. The training_config in the Projects collection is embedded directly within each project document because its life cycle depends on the existence of the project. Images, training results, and inference results are stored in separate collections and linked by references to maintain flexibility.

### Justification for Using SQL

#### 1. Structured Query Language (SQL):
SQL databases use a query language that allows for complex queries and data manipulation. This is particularly useful for the application as it requires comprehensive data retrieval capabilities, especially for the trainig results.

#### 2. Data Integrity: 
SQL databases support ACID (Atomicity, Consistency, Isolation, Durability) properties which ensure reliable handling of data. This is important for the project as data integrity and transactions are crucial for correct model analysis.

#### 3. Relationships and Normalization: 
SQL databases are effective at handling relationships between data entities, a property that is makes the backbone of the relational database used. The normalization process helps eliminate redundancy and dependency, which ensures data consistency.

#### Summary:
SQL databases provide greater support for structured data handling, complex queries and transactions, ensuring data integrity and consistency. The properties of SQL are important for managing the relational structure of the data in the project.

### Phase 3 - Queue Implementation

### Phase 4 - Data Protection

## Contributors

- [Leon Long](https://github.com/Leon-Long-Portfolio)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

