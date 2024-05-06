from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import DevelopmentConfig
from routes import main as main_routes
from models import db, User

login_manager = LoginManager()

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SECRET_KEY'] = 'your-secret-key'

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    app.register_blueprint(main_routes)

    # Setup Flask-Migrate
    migrate = Migrate(app, db)  # Initialize Flask-Migrate

    with app.app_context():
        db.create_all()

    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
