""" ESTRTUTRA DO BANCO DE DADOS """

from main import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy.schema import Sequence

# função obrigatória qdo se cria estrutura de login com flask_login/LoginManager
@login_manager.user_loader
def load_user(id_usuario):
    return DimPaciente.query.get(int(id_usuario))


# Cada classe representa uma tabela no BD
class DimPaciente(db.Model, UserMixin):
    _tablename_ = 'dim_paciente'
    id_paciente = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    senha = db.Column(db.String(255), nullable=True)
    access_key = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(10), default='paciente')

    def __repr__(self):
        return f"Paciente: {self.nome} - CPF {self.cpf}"

    # Função necessária para sobrescrever a padrão, pois utilizamos "id_paciente" ao invés de somente "id"
    def get_id(self):
        return self.id_paciente


class DimEnderecoPaciente(db.Model):
    _tablename_ = 'dim_endereco_paciente'
    id_endereco_paciente = db.Column(db.Integer, primary_key=True)
    fk_id_paciente = db.Column(db.Integer, db.ForeignKey('dim_paciente.id_paciente'), nullable=False)
    logradouro = db.Column(db.String(100), nullable=True)
    numero = db.Column(db.String(20), nullable=True)
    complemento = db.Column(db.String(100), nullable=True)
    bairro = db.Column(db.String(100), nullable=True)
    cidade = db.Column(db.String(100), nullable=True)
    estado = db.Column(db.String(2), nullable=True)
    cep = db.Column(db.String(9), nullable=True)
    paciente = db.relationship('DimPaciente', backref=db.backref('endereco', lazy=True))


# Modelo para Médico
class DimMedico(db.Model):
    _tablename_ = 'dim_medico'
    id_medico = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    pronome_tratamento = db.Column(db.String(10), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    crm = db.Column(db.String(20), unique=True, nullable=False)
    data_nascimento = db.Column(db.Date, nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    senha = db.Column(db.String(255), nullable=True)
    access_key = db.Column(db.String(255), nullable=True)
    especialidade = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(10), default='medico')

    def __repr__(self):
        return f"<Medico>: {self.nome} - CPF {self.crm}"


class DimEnderecoMedico(db.Model):
    _tablename_ = 'dim_endereco_medico'
    id_endereco_medico = db.Column(db.Integer, primary_key=True)
    fk_id_medico = db.Column(db.Integer, db.ForeignKey('dim_medico.id_medico'), nullable=False)
    logradouro = db.Column(db.String(100), nullable=True)
    numero = db.Column(db.String(20), nullable=True)
    complemento = db.Column(db.String(100), nullable=True)
    bairro = db.Column(db.String(100), nullable=True)
    cidade = db.Column(db.String(100), nullable=True)
    estado = db.Column(db.String(2), nullable=True)
    cep = db.Column(db.String(9), nullable=True)
    medico = db.relationship('DimMedico', backref=db.backref('endereco', lazy=True))


# Modelo para Tipo de Exame
class DimTipoExame(db.Model):
    _tablename_ = 'dim_tipo_exame'
    id_exame = db.Column(db.Integer, primary_key=True)
    tipo_exame = db.Column(db.String(100), nullable=False)


class DimTipoEncaminhamento(db.Model):
    _tablename_ = 'dim_tipo_encaminhamento'
    id_tipo_encaminhamento = db.Column(db.Integer, primary_key=True)
    tipo_encaminhamento = db.Column(db.String(100), nullable=False)


# Modelo para Encaminhamento
class DimEncaminhamento(db.Model):
    _tablename_ = 'dim_encaminhamento'
    id_encaminhamento = db.Column(db.Integer, primary_key=True)
    fk_id_tipo_encaminhamento = db.Column(db.String, db.ForeignKey('dim_tipo_encaminhamento.id_tipo_encaminhamento'), nullable=False)
    fk_id_paciente = db.Column(db.Integer, db.ForeignKey('dim_paciente.id_paciente'), nullable=False)
    fk_id_medico = db.Column(db.Integer, db.ForeignKey('dim_medico.id_medico'), nullable=True)
    fk_id_exame = db.Column(db.Integer, db.ForeignKey('dim_tipo_exame.id_exame'), nullable=True)
    protocolo_encaminhamento = db.Column(db.String, nullable=True)
    protocolo_agendamento = db.Column(db.String, nullable=True)
    paciente = db.relationship('DimPaciente', backref=db.backref('encaminhamentos', lazy=True))
    medico = db.relationship('DimMedico', backref=db.backref('encaminhamentos', lazy=True))
    exame = db.relationship('DimTipoExame', backref=db.backref('encaminhamentos', lazy=True))
    tipo = db.relationship('DimTipoEncaminhamento', backref=db.backref('tipo', lazy=True))

    def __repr__(self):
        return f"Encaminhamento {self.id_encaminhamento} - {DimTipoEncaminhamento.query.filter(DimTipoEncaminhamento.id_tipo_encaminhamento == self.fk_id_tipo_encaminhamento).first().tipo_encaminhamento} - Paciente {DimPaciente.query.filter(DimPaciente.id_paciente == self.fk_id_paciente).first().nome}"


# Modelo para Disponibilidade de Exames
class DimDisponibilidadeExames(db.Model):
    _tablename_ = 'dim_disponibilidade_exames'
    id_disponibilidade_exame = db.Column(db.Integer, primary_key=True)
    fk_id_exame = db.Column(db.Integer, db.ForeignKey('dim_tipo_exame.id_exame'), nullable=False)
    data_disponivel = db.Column(db.Date, nullable=False)
    dia_semana = db.Column(db.String(20), nullable=False)
    hora_disponivel = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    exame = db.relationship('DimTipoExame', backref=db.backref('disponibilidades', lazy=True))


# Modelo para Agendamento de Exame
class FatoAgendaExame(db.Model):
    _tablename_ = 'fato_agenda_exame'
    id_agenda_exame = db.Column(db.Integer, primary_key=True)
    fk_id_encaminhamento = db.Column(db.Integer, db.ForeignKey('dim_encaminhamento.id_encaminhamento'), nullable=False)
    fk_id_exame = db.Column(db.Integer, db.ForeignKey('dim_tipo_exame.id_exame'), nullable=False)
    fk_id_paciente = db.Column(db.Integer, db.ForeignKey('dim_paciente.id_paciente'), nullable=False)
    fk_id_medico = db.Column(db.Integer, db.ForeignKey('dim_medico.id_medico'), nullable=True)
    fk_id_disponibilidade_exame = db.Column(db.Integer, db.ForeignKey('dim_disponibilidade_exames.id_disponibilidade_exame'), nullable=False)
    protocolo_exame = db.Column(db.String, nullable=True)
    status = db.Column(db.String(20), nullable=False)
    encaminhamento = db.relationship('DimEncaminhamento', backref=db.backref('agendamentos_exame', lazy=True))
    exame = db.relationship('DimTipoExame')
    paciente = db.relationship('DimPaciente', backref=db.backref('exames_agendados', lazy=True))
    medico = db.relationship('DimMedico')
    disponibilidade_exame = db.relationship('DimDisponibilidadeExames', backref=db.backref('disponibilidade_exame', lazy=True))


# Modelo para Disponibilidade de Consultas
class DimDisponibilidadeConsultas(db.Model):
    _tablename_ = 'dim_disponibilidade_consultas'
    id_disponibilidade_consulta = db.Column(db.Integer, primary_key=True)
    fk_id_medico = db.Column(db.Integer, db.ForeignKey('dim_medico.id_medico'), nullable=False)
    data_disponivel = db.Column(db.Date, nullable=False)
    dia_semana = db.Column(db.String(20), nullable=False)
    hora_disponivel = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    medico = db.relationship('DimMedico', backref=db.backref('disponibilidades_consulta', lazy=True))


# Modelo para Agendamento de Consulta
class FatoAgendaConsulta(db.Model):
    _tablename_ = 'agendamento_consulta'
    id_agendamento_consulta = db.Column(db.Integer, primary_key=True)
    fk_id_encaminhamento = db.Column(db.Integer, db.ForeignKey('dim_encaminhamento.id_encaminhamento'), nullable=True)
    fk_id_medico = db.Column(db.Integer, db.ForeignKey('dim_medico.id_medico'), nullable=False)
    fk_id_paciente = db.Column(db.Integer, db.ForeignKey('dim_paciente.id_paciente'), nullable=False)
    fk_id_disponibilidade_consulta = db.Column(db.Integer, db.ForeignKey('dim_disponibilidade_consultas.id_disponibilidade_consulta'), nullable=False)
    protocolo_consulta = db.Column(db.String, nullable=True)
    status = db.Column(db.String(20), nullable=False)
    encaminhamento = db.relationship('DimEncaminhamento', backref=db.backref('consulta_agendada', lazy=True))
    medico = db.relationship('DimMedico', backref=db.backref('consultas_agendadas', lazy=True))
    paciente = db.relationship('DimPaciente', backref=db.backref('consultas_agendadas', lazy=True))
    disponibilidade_consulta = db.relationship('DimDisponibilidadeConsultas', backref=db.backref('disponibilidade_consulta', lazy=True))

