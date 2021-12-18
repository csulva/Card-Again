from flask import Flask
from config import config
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_moment import Moment
from flask_mail import Mail

bootstrap = Bootstrap()
db = SQLAlchemy()
login = LoginManager()
login.login_view = 'auth.login'
moment = Moment()
mail = Mail()


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)

    bootstrap.init_app(app)
    login.init_app(app)
    moment.init_app(app)
    mail.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app