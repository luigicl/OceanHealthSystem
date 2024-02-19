from datetime import datetime
from main import database
from main.models import Usuarios
from flask import Flask, render_template, request
from main import app


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/cadastrar", methods=['GET', 'POST'])
def cadastrar():
    # Apertado o botão de enviar cadastro
    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        data_nascimento = request.form.get('dataNascimento')
        print(data_nascimento)
        celular = request.form.get('celular')
        email = request.form.get('email')
        data_cadastro = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        # Para a tela de confirmação
        dados_usuario = {
            'nome': nome,
            'cpf': cpf,
            'data_nascimento': data_nascimento,
            'celular': celular,
            'email': email,
            'data': data_cadastro
        }

        # Validar o CPF digitado
        if validar_cpf(cpf):
            # VERIFICAR SE JÁ EXISTE CADASTRO COM O CPF INFORMADO
            if Usuarios.query.filter(Usuarios.cpf == cpf).first():
                mensagem = f"CPF ({cpf}) já cadastrado. Verifique o número digitado ou faça login."
                return render_template("cadastrar.html", mensagem=mensagem)
            elif validar_data_nascimento(data_nascimento):
                usuario = Usuarios(
                    nome=nome,
                    cpf=cpf,
                    data_nascimento=data_nascimento,
                    celular=celular,
                    email=email,
                    data_cadastro=data_cadastro,
                    paciente=True
                )
                database.session.add(usuario)
                database.session.commit()
                return render_template("confirmacao_cadastro.html", dados_usuario=dados_usuario)
            else:
                mensagem = f"Verifique a data de nascimento inserida."
                return render_template("cadastrar.html", mensagem=mensagem)
        else:
            mensagem = f"Verifique o CPF digitado ({cpf}) e tente novamente."
            return render_template("cadastrar.html", mensagem=mensagem)
    return render_template("cadastrar.html")


def validar_cpf(cpf):
    """ **** COMENTADO APENAS PARA FACILITAR OS TESTE, PARA PRODUÇÃO REATIVAR ESTE TRECHO **** """
    # # Verificando o comprimento do CPF ou se todos os digitos são iguais (e.g. 111.111.111-11)
    # if len(cpf) != 11 or len(set(cpf)) == 1:
    #     return False
    # try:
    #     digitos = list(map(int, cpf))
    # except ValueError:
    #     return False

    # ***** AO REATIVAR O TRECHO ACIMA, EXCLUIR AS TRÊS LINHAS ABAIXO  ******
    if len(cpf) != 11:
        return False
    digitos = list(map(int, cpf))

    def calcular_digito(multiplicador):
        total = 0
        for d in digitos:
            if multiplicador >= 2:
                total += d * multiplicador
                multiplicador -= 1
            else:
                break
        resto = total % 11
        if resto < 2:
            return 0
        else:
            return 11 - resto

    # Verificando o primeiro dígito
    if digitos[9] != calcular_digito(10):
        return False

    # Verificando o segundo dígito
    if digitos[10] != calcular_digito(11):
        return False

    return True

def validar_data_nascimento(data_nascimento):
    data_nascimento_objeto = datetime.strptime(data_nascimento, "%Y-%m-%d").date()
    hoje = datetime.now().date()
    dias = (hoje - data_nascimento_objeto).days
    if (120 * 365) > dias > 0:
        return True
    else:
        return False
    

@app.route('/menu')
def menu_principal():
    
    return render_template("menu.html")