from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateTimeField
from wtforms.validators import DataRequired


# TESTE CALENDÁRIO
class ConsultaForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired()])
    inicio = DateTimeField('Início', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    fim = DateTimeField('Fim', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired()])
    submit = SubmitField('Agendar')


# class CriarEncaminhamento(FlaskForm):
#     titulo = StringField('Título', validators=[DataRequired()])
#     inicio = DateTimeField('Início', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
#     fim = DateTimeField('Fim', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
#     url = StringField('URL', validators=[DataRequired()])
#     submit = SubmitField('Agendar')