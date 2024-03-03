from main import db, app
from main.models import *

with app.app_context():  # as novas versões do flask exigem que o DB seja criado por um contexto (app) com with
    db.create_all()
