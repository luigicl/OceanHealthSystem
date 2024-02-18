""" ESTRTUTRA DO BANCO DE DADOS """

from main import database
from datetime import datetime


class Usuarios(database.Model):
    # id = database.Column(database.Integer, autoincrement=True)
    cpf = database.Column(database.String, primary_key=True)
    nome = database.Column(database.String, nullable=False)
    data_nascimento = database.Column(database.String, nullable=False)
    celular = database.Column(database.String, nullable=False)
    email = database.Column(database.String, nullable=False)
    data_cadastro = database.Column(database.String, nullable=False)
    admin = database.Column(database.Boolean, default=False, nullable=False)
    medico = database.Column(database.Boolean, default=False, nullable=False)
    paciente = database.Column(database.Boolean, default=False, nullable=False)
