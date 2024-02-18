from flask import Flask
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ohs.db"
# app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')
app.config['TEMPLATES_AUTO_RELOAD'] = True

database = SQLAlchemy(app)

app.app_context().push()

from main import routes