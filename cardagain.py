from app import create_app, db
import os
from flask_migrate import Migrate, upgrade
from app.models import Follow, Role, User, Card
import logging

# Create app from FLASK_CONFIG environment variable config or default config
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

migrate = Migrate(app, db, render_as_batch=True)

@app.shell_context_processor
def make_shell_context():
    """Provides database tables/classes for flask shell sessions
    so they do not need to be called every time
    """
    return dict(db=db, User=User, Card=Card, Role=Role, Follow=Follow)

@app.cli.command()
def deploy():
    """Run deployment tasks for production"""
    # migrate database
    upgrade()

    Role.insert_roles()

    User.add_self_follows()