from main import database, app
from main.models import Usuarios

with app.app_context():  # as novas versões do flask exigem que o DB seja criado por um contexto (app) com with
    database.create_all()
