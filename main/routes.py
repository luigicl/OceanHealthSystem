from datetime import datetime
from main import db, app
from main.models import *
from main.forms import ConsultaForm
from flask import Flask, render_template, request, redirect, url_for, jsonify


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

        # Validar o CPF digitado - ******* REVISAR, POIS O MODELS FOI ALTERADO ********
        # if validar_cpf(cpf):
        #     # VERIFICAR SE JÁ EXISTE CADASTRO COM O CPF INFORMADO
        #     if Usuarios.query.filter(Usuarios.cpf == cpf).first():
        #         mensagem = f"CPF ({cpf}) já cadastrado. Verifique o número digitado ou faça login."
        #         return render_template("cadastrar.html", mensagem=mensagem)
        #     elif validar_data_nascimento(data_nascimento):
        #         usuario = Usuarios(
        #             nome=nome,
        #             cpf=cpf,
        #             data_nascimento=data_nascimento,
        #             celular=celular,
        #             email=email,
        #             data_cadastro=data_cadastro,
        #             paciente=True
        #         )
        #         db.session.add(usuario)
        #         db.session.commit()
        #         return render_template("confirmacao_cadastro.html", dados_usuario=dados_usuario)
        #     else:
        #         mensagem = f"Verifique a data de nascimento inserida."
        #         return render_template("cadastrar.html", mensagem=mensagem)
        # else:
        #     mensagem = f"Verifique o CPF digitado ({cpf}) e tente novamente."
        #     return render_template("cadastrar.html", mensagem=mensagem)
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


# TESTE CALENDÁRIO
@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    form = ConsultaForm()
    if form.validate_on_submit():
        nova_consulta = Consulta(titulo=form.titulo.data, inicio=form.inicio.data, fim=form.fim.data, url=form.url.data)
        db.session.add(nova_consulta)
        db.session.commit()
        return redirect(url_for('calendario'))
    return render_template('agendar.html', form=form)


# TESTE CALENDÁRIO
@app.route('/api/eventos')
def eventos():
    consultas = Consulta.query.all()
    eventos = []
    for consulta in consultas:
        eventos.append({
            "title": consulta.titulo,
            "start": consulta.inicio.strftime("%Y-%m-%dT%H:%M:%S"),
            "end": consulta.fim.strftime("%Y-%m-%dT%H:%M:%S"),
            "url": consulta.url
        })
    return jsonify(eventos)


# TESTE CALENDÁRIO
@app.route('/calendario')
def calendario():
    return render_template('calendario.html')


@app.route('/menu')
def menu_principal():
    return render_template('menu.html')


@app.route('/consulta')
def consulta():
    return render_template("agendamento_consulta.html")


# TESTE
@app.route('/gerar_encaminhamento', methods=['GET', 'POST'])
def teste_gerar_encaminhamento():
    exames = TipoExame.query.all()
    medicos = Medico.query.all()
    pacientes = Paciente.query.order_by(Paciente.nomeCompleto).all()
    if request.method == 'POST':
        tipo_encaminhamento = request.form.get('rb_tipo_encaminhamento')
        exame = request.form.get('input_tipo_exame')
        medico = request.form.get('input_especialidade')
        paciente = request.form.get('input_paciente')
        encaminhamento = Encaminhamento(
                                        id_tipo_encaminhamento=tipo_encaminhamento,
                                        id_paciente=paciente,
                                        id_medico=medico,
                                        id_exame=exame
                                        )
        db.session.add(encaminhamento)
        db.session.commit()
        if tipo_encaminhamento == "1":
            encaminhamento_gerado = {
                                    "tipo": TipoEncaminhamento.query.get(tipo_encaminhamento).tipoEncaminhamento,
                                    "nome_paciente": Paciente.query.get(paciente).nomeCompleto,
                                    "cpf_paciente": Paciente.query.get(paciente).cpf,
                                    "nome_medico": Medico.query.get(medico).nomeCompleto,
                                    "especialidade": Medico.query.get(medico).nomeEspecialidade
                                    }
            return render_template("teste_confirmacao_encaminhamento.html",
                                   encaminhamento=encaminhamento_gerado
                                   )

        if tipo_encaminhamento == "2":
            encaminhamento_gerado = {
                                    "tipo": TipoEncaminhamento.query.get(tipo_encaminhamento).tipoEncaminhamento,
                                    "nome_paciente": Paciente.query.get(paciente).nomeCompleto,
                                    "cpf_paciente": Paciente.query.get(paciente).cpf,
                                    "exame": TipoExame.query.get(exame).tipoExame,
                                    }
            return render_template("teste_confirmacao_encaminhamento.html",
                                   encaminhamento=encaminhamento_gerado
                                   )

    return render_template("teste_gerar_encaminhamento.html",
                           exames=exames,
                           medicos=medicos,
                           pacientes=pacientes
                           )


# TESTE
@app.route('/listar_encaminhamentos', methods=['GET', 'POST'])
def teste_listar_encaminhamentos():
    pacientes = Paciente.query.order_by(Paciente.nomeCompleto).all()
    if request.method == 'POST':
        id_paciente = request.form.get('input_paciente')
        paciente = Paciente.query.get(id_paciente)
        exames = Encaminhamento.query.filter(Encaminhamento.id_paciente == id_paciente).filter(Encaminhamento.id_exame != "...").all()
        consultas = Encaminhamento.query.filter(Encaminhamento.id_paciente == id_paciente).filter(Encaminhamento.id_medico != "...").all()
        return render_template("teste_listar_encaminhamentos.html", pacientes=pacientes, exames=exames, consultas=consultas, paciente=paciente)
    return render_template("teste_listar_encaminhamentos.html", pacientes=pacientes)
