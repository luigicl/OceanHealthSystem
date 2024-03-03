""" ESTRTUTRA DO BANCO DE DADOS """

from main import db
from datetime import datetime


# Cada classe representa uma tabela no BD

# Modelo para Paciente
class Paciente(db.Model):
    _tablename_ = 'paciente'
    id_paciente = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    nomeCompleto = db.Column(db.String(100), nullable=False)
    dataNascimento = db.Column(db.Date, nullable=True)
    celular = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    senhaHashPaciente = db.Column(db.String(255), nullable=True)
    logradouro = db.Column(db.String(100), nullable=True)
    numero = db.Column(db.String(20), nullable=True)
    complemento = db.Column(db.String(100), nullable=True)
    privilegio = db.Column(db.String(50), nullable=True)
    bairro = db.Column(db.String(100), nullable=True)
    cidade = db.Column(db.String(100), nullable=True)
    estado = db.Column(db.String(2), nullable=True)
    cep = db.Column(db.String(9), nullable=True)
    tokenUBS = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"Paciente: CPF {self.cpf}, {self.nomeCompleto}"


# Modelo para Médico
class Medico(db.Model):
    _tablename_ = 'medico'
    id_medico = db.Column(db.Integer, primary_key=True)
    nomeCompleto = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    CRM = db.Column(db.String(20), unique=True, nullable=False)
    privilegio = db.Column(db.String(50), nullable=True)
    senhaHashMedico = db.Column(db.String(255), nullable=True)
    nomeEspecialidade = db.Column(db.String(100), nullable=False)


# Modelo para Tipo de Exame
class TipoExame(db.Model):
    _tablename_ = 'tipo_exame'
    id_exame = db.Column(db.Integer, primary_key=True)
    tipoExame = db.Column(db.String(100), nullable=False)


class TipoEncaminhamento(db.Model):
    _tablename_ = 'tipo_encaminhamento'
    id_tipo_encaminhamento = db.Column(db.Integer, primary_key=True)
    tipoEncaminhamento = db.Column(db.String(100), nullable=False)


# Modelo para Encaminhamento
class Encaminhamento(db.Model):
    _tablename_ = 'encaminhamento'
    id_encaminhamento = db.Column(db.Integer, primary_key=True)
    id_tipo_encaminhamento = db.Column(db.String, db.ForeignKey('tipo_encaminhamento.id_tipo_encaminhamento'), nullable=False)
    id_paciente = db.Column(db.Integer, db.ForeignKey('paciente.id_paciente'), nullable=False)
    id_medico = db.Column(db.Integer, db.ForeignKey('medico.id_medico'), nullable=True)
    id_exame = db.Column(db.Integer, db.ForeignKey('tipo_exame.id_exame'), nullable=True)
    paciente = db.relationship('Paciente', backref=db.backref('encaminhamentos', lazy=True))
    medico = db.relationship('Medico', backref=db.backref('encaminhamentos', lazy=True))
    exame = db.relationship('TipoExame', backref=db.backref('encaminhamentos', lazy=True))


# Modelo para Disponibilidade de Exames
class DisponibilidadeExame(db.Model):
    _tablename_ = 'disponibilidade_exame'
    id_disponibilidade_exame = db.Column(db.Integer, primary_key=True)
    id_exame = db.Column(db.Integer, db.ForeignKey('tipo_exame.id_exame'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    exame = db.relationship('TipoExame', backref=db.backref('disponibilidades', lazy=True))


# Modelo para Agendamento de Exame
class AgendamentoExame(db.Model):
    _tablename_ = 'agendamento_exame'
    id_agendamento_exame = db.Column(db.Integer, primary_key=True)
    id_encaminhamento = db.Column(db.Integer, db.ForeignKey('encaminhamento.id_encaminhamento'), nullable=False)
    id_exame = db.Column(db.Integer, db.ForeignKey('tipo_exame.id_exame'), nullable=False)
    id_paciente = db.Column(db.Integer, db.ForeignKey('paciente.id_paciente'), nullable=False)
    id_medico = db.Column(db.Integer, db.ForeignKey('medico.id_medico'), nullable=False)
    id_disponibilidade_exame = db.Column(db.Integer, db.ForeignKey('disponibilidade_exame.id_disponibilidade_exame'), nullable=False)
    encaminhamento = db.relationship('Encaminhamento', backref=db.backref('agendamentos_exame', lazy=True))
    exame = db.relationship('TipoExame')
    paciente = db.relationship('Paciente')
    medico = db.relationship('Medico')
    disponibilidade_exame = db.relationship('DisponibilidadeExame', backref=db.backref('agendamentos_exame', lazy=True))


# Modelo para Disponibilidade de Consultas
class DisponibilidadeConsulta(db.Model):
    _tablename_ = 'disponibilidade_consulta'
    id_disponibilidade_consultas = db.Column(db.Integer, primary_key=True)
    id_medico = db.Column(db.Integer, db.ForeignKey('medico.id_medico'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    medico = db.relationship('Medico', backref=db.backref('disponibilidades_consulta', lazy=True))


# Modelo para Agendamento de Consulta
class AgendamentoConsulta(db.Model):
    _tablename_ = 'agendamento_consulta'
    id_agendamento_consulta = db.Column(db.Integer, primary_key=True)
    id_encaminhamento = db.Column(db.Integer, db.ForeignKey('encaminhamento.id_encaminhamento'), nullable=True)
    id_medico = db.Column(db.Integer, db.ForeignKey('medico.id_medico'), nullable=False)
    id_paciente = db.Column(db.Integer, db.ForeignKey('paciente.id_paciente'), nullable=False)
    id_disponibilidade_consultas = db.Column(db.Integer, db.ForeignKey('disponibilidade_consulta.id_disponibilidade_consultas'), nullable=False)
    encaminhamento = db.relationship('Encaminhamento', backref=db.backref('agendamentos_consulta', lazy='dynamic'))
    medico = db.relationship('Medico')
    paciente = db.relationship('Paciente')
    disponibilidade_consulta = db.relationship('DisponibilidadeConsulta', backref=db.backref('agendamentos_consulta', lazy=True))