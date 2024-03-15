from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField
from wtforms.validators import DataRequired, EqualTo, Length, Regexp


class CreatePassword(FlaskForm):
    cpf = IntegerField('CPF:',
                       validators=[
                           DataRequired(message='É necessário informar o seu CPF.'),
                       ])
    access_key = StringField('Código de acesso:', validators=[
        DataRequired(message='É necessário informar o código de acesso fornecido pela unidade de saúde.')])
    password = PasswordField('Nova senha:',
                             validators=[
                                 DataRequired(message='É necessário digitar uma senha.')
                             ])
    confirmation = PasswordField('Confirme a senha:',
                                 validators=[
                                     DataRequired(message='É necessário digitar novamente a senha.'),
                                     EqualTo('password', message='As senhas devem ser iguais'),
                                 ])
    submit = SubmitField('Registrar')

# TESTE CALENDÁRIO
# class ConsultaForm(FlaskForm):
#     titulo = StringField('Título', validators=[DataRequired()])
#     inicio = DateTimeField('Início', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
#     fim = DateTimeField('Fim', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
#     url = StringField('URL', validators=[DataRequired()])
#     submit = SubmitField('Agendar')


# class CriarEncaminhamento(FlaskForm):
#     titulo = StringField('Título', validators=[DataRequired()])
#     inicio = DateTimeField('Início', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
#     fim = DateTimeField('Fim', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
#     url = StringField('URL', validators=[DataRequired()])
#     submit = SubmitField('Agendar')
