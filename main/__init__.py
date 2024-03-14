from flask import Flask
from dotenv import load_dotenv
import os
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ohs.db"
app.secret_key = "5accdb11b2c10a78d7c92c5fa102ea77fcd50c2058b00f6e"
# app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')
app.config["ID_CLINICO_GERAL"] = 1
app.config["ID_ENCAMINHAMENTO_CONSULTA"] = "1"
app.config["ID_ENCAMINHAMENTO_EXAME"] = "2"
app.config['TEMPLATES_AUTO_RELOAD'] = True

db = SQLAlchemy(app)
# migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "logar"  # em qual pagina será executado o login

app.app_context().push()

from main import routes