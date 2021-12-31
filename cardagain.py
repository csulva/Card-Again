from app import create_app, db
import os
from flask_migrate import Migrate, upgrade
from app.models import Role, User, Card

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

migrate = Migrate(app, db, render_as_batch=True)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Card=Card, Role=Role)

@app.cli.command()
def deploy():
    """ Run deployment tasks """
    # migrate database
    upgrade()

    Role.insert_roles()

    User.add_self_follows()

    Card.insert_cards()
