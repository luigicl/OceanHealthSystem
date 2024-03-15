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
