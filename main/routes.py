from random import random, randrange, choice
import secrets
from main import db, app, bcrypt
from main.models import *
from main.forms import CreatePassword
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, login_user, logout_user, current_user


# ROTAS GERAIS

@app.route("/")
def home():
    """ Página inicial do sistema """
    return render_template("home_new.html")


@app.route("/login", methods=['GET', 'POST'])
def logar():
    if request.method == 'POST':
        cpf = request.form.get('cpf')
        senha = request.form.get('senha')
        paciente = DimPaciente.query.filter(DimPaciente.cpf == cpf).first()
        if paciente:
            if paciente.senha:
                if bcrypt.check_password_hash(paciente.senha, senha):
                    login_user(paciente)
                    return redirect(url_for("menu_principal_paciente", id_usuario=paciente.id_paciente))
                else:
                    mensagem = "A senha digitada está errada."
                    return render_template("login.html", mensagem=mensagem)
            else:
                mensagem = ("Este usuário ainda não possui senha cadastrada. Crie sua senha utilizando a chave de acesso "
                            "fornecida pela unidade de saúde")
                return render_template("login.html", mensagem=mensagem)
        else:
            mensagem = "o CPF informado ainda não possui cadastro no sistema. Favor dirigir-se à unidade de saúde."
            return render_template("login.html", mensagem=mensagem)
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


# ROTAS PACIENTE

@app.route('/menu_paciente')
@login_required
def menu_principal_paciente():
    id_paciente = current_user.id_paciente
    paciente = DimPaciente.query.get(id_paciente)
    return render_template('menu_paciente.html', paciente=paciente)


@app.route("/criar_senha", methods=['GET', 'POST'])
def criar_senha():
    """ Criação de senha de acesso após pré-cadastro na unidade de saúde """
    form_senha = CreatePassword()
    if form_senha.validate_on_submit():
        cpf = str(form_senha.cpf.data)
        print(cpf)
        access_key = form_senha.access_key.data
        print(access_key)
        senha = bcrypt.generate_password_hash(form_senha.password.data)
        usuario = DimPaciente.query.filter(DimPaciente.cpf == cpf).first()
        if usuario:
            if not usuario.senha:
                print(access_key)
                if usuario.access_key == access_key:
                    usuario.senha = senha
                    db.session.commit()
                    return render_template("home_new.html", confirmacao=1)
                else:
                    mensagem = "A chave de acesso inserida não confere, favor verificar e tentar novamente."
                    return render_template("criar_senha.html", form=form_senha, mensagem=mensagem)
            else:
                mensagem = "Esse usuário (CPF) já possui senha cadastrada, favor realizar seu login."
                return render_template("criar_senha.html", form=form_senha, mensagem=mensagem)
    return render_template("criar_senha.html", form=form_senha)


@app.route('/encaminhamentos', methods=['GET', 'POST'])
@login_required
def listar_encaminhamentos_pendentes():
    id_paciente = current_user.id_paciente
    paciente = DimPaciente.query.get(id_paciente)
    encaminhamentos = (DimEncaminhamento.query
                       .filter(DimEncaminhamento.fk_id_paciente == id_paciente)
                       .filter(DimEncaminhamento.protocolo_agendamento == None)
                       .all()
                       )
    titulo = "Lista de encaminhamentos pendentes"
    return render_template("listar_encaminhamentos.html",
                           # exames=exames,
                           # consultas=consultas,
                           paciente=paciente,
                           encaminhamentos=encaminhamentos,
                           titulo=titulo
                           )


@app.route('/minha_agenda', methods=['GET', 'POST'])
@login_required
def mostrar_agenda_paciente():
    id_paciente = current_user.id_paciente
    paciente = DimPaciente.query.get(id_paciente)
    consultas_agendadas = (db.session.query(FatoAgendaConsulta)
                           .join(FatoAgendaConsulta.disponibilidade_consulta)
                           .order_by(DimDisponibilidadeConsultas.data_disponivel)
                           .order_by(DimDisponibilidadeConsultas.hora_disponivel)
                           .filter(FatoAgendaConsulta.fk_id_paciente == id_paciente)
                           .all()
                           )
    exames_agendados = (db.session.query(FatoAgendaExame)
                        .join(FatoAgendaExame.disponibilidade_exame)
                        .order_by(DimDisponibilidadeExames.data_disponivel)
                        .order_by(DimDisponibilidadeExames.hora_disponivel)
                        .filter(FatoAgendaExame.fk_id_paciente == id_paciente)
                        .all()
                        )
    return render_template("agenda_paciente.html",
                           paciente=paciente,
                           consultas=consultas_agendadas,
                           exames=exames_agendados
                           )


@app.route('/agendar_clinico')
@login_required
def agendar_clinico():
    """ Listar disponibilidade para agendamento de consulta com clínico geral """
    id_paciente = current_user.id_paciente
    paciente = DimPaciente.query.get(id_paciente)
    disponibilidade_clinico = (DimDisponibilidadeConsultas.query
                               .filter(DimDisponibilidadeConsultas.fk_id_medico == app.config["ID_CLINICO_GERAL"])
                               .filter(DimDisponibilidadeConsultas.status == None)
                               .order_by(DimDisponibilidadeConsultas.data_disponivel)
                               .order_by(DimDisponibilidadeConsultas.hora_disponivel)
                               )  # .filter() não aceita "is None"
    medico = DimMedico.query.get(app.config["ID_CLINICO_GERAL"])
    titulo = "Disponbilidade para consulta com"

    return render_template("agendar_consulta.html",
                           disponibilidade_clinico=disponibilidade_clinico,
                           medico=medico,
                           paciente=paciente,
                           titulo=titulo
                           )


@app.route('/agendamento', methods=['GET'])
@login_required
def agendamento_clinico():
    """ Agendamento de consulta com Clínico Geral, não necessita de encaminhamento """
    id_disponibilidade = request.args.get("disponibilidade")
    id_paciente = current_user.id_paciente
    paciente = DimPaciente.query.get(id_paciente)
    id_medico = app.config["ID_CLINICO_GERAL"]
    medico = DimMedico.query.get(id_medico)
    protocolo = gerar_protocolo('consulta')

    agendamento = FatoAgendaConsulta(
        fk_id_medico=id_medico,
        fk_id_paciente=id_paciente,
        fk_id_disponibilidade_consulta=id_disponibilidade,
        protocolo_consulta=protocolo,
        medico=medico,
        status="Pendente"
    )

    disponibilidade = DimDisponibilidadeConsultas.query.get(id_disponibilidade)
    disponibilidade.status = "indisponivel"

    db.session.add(agendamento)
    db.session.commit()

    return render_template("menu_paciente.html",
                           confirmacao=1,
                           protocolo=protocolo,
                           medico=medico,
                           paciente=paciente,
                           disponibilidade=disponibilidade
                           )


@app.route('/selecionar_disponibilidade', methods=['GET', 'POST'])
@login_required
def selecionar_disponibilidade():
    """ Listar a disponibilidade para agendamento de um encaminhamento """
    if request.method == 'POST':
        id_encaminhamento = request.form.get("id_encaminhamento")
        encaminhamento = DimEncaminhamento.query.get(id_encaminhamento)
        id_medico = encaminhamento.fk_id_medico
        id_exame = encaminhamento.fk_id_exame
        id_paciente = current_user.id_paciente
        paciente = DimPaciente.query.get(id_paciente)

        if id_medico is not None:
            disponibilidades_consultas = (DimDisponibilidadeConsultas.query
                                          .filter(DimDisponibilidadeConsultas.fk_id_medico == id_medico)
                                          .order_by(DimDisponibilidadeConsultas.data_disponivel)
                                          .order_by(DimDisponibilidadeConsultas.hora_disponivel)
                                          )
            medico = DimMedico.query.get(id_medico)
            titulo = f"Disponbilidade para consulta com {medico.especialidade}"
            return render_template('selecionar_disponibilidade_encaminhamento.html',
                                   disponibilidades_consultas=disponibilidades_consultas,
                                   medico=medico,
                                   titulo=titulo,
                                   paciente=paciente,
                                   id_encaminhamento=id_encaminhamento
                                   )

        if id_exame is not None:
            disponibilidades_exames = (DimDisponibilidadeExames.query
                                       .filter(DimDisponibilidadeExames.fk_id_exame == id_exame)
                                       .order_by(DimDisponibilidadeExames.data_disponivel)
                                       .order_by(DimDisponibilidadeExames.hora_disponivel)
                                       )
            exame = DimTipoExame.query.get(id_exame)
            titulo = f"Disponbilidade para realizar o exame de {exame.tipo_exame}"
            return render_template('selecionar_disponibilidade_encaminhamento.html',
                                   disponibilidades_exames=disponibilidades_exames,
                                   exame=exame,
                                   titulo=titulo,
                                   paciente=paciente,
                                   id_encaminhamento=id_encaminhamento
                                   )

    return ("<h2 style='margin-top:40px; margin-left:20px;'>ERRO!<br><br>Esta página deve ser acessada exclusivamente "
            "a partir do menu de encaminhamentos pendentes.</h2>")


@app.route('/reagendar', methods=['GET', 'POST'])
@login_required
def reagendar():
    """ Reverter um agendamento, disponibilizando o encaminhamento para remarcação """
    if request.method == 'POST':
        id_agendamento = request.form.get('id_agendamento')
        tipo_agendamento = request.form.get('tipo_agendamento')

        id_paciente = current_user.id_paciente
        paciente = DimPaciente.query.get(id_paciente)

        if tipo_agendamento == "consulta":
            agendamento = FatoAgendaConsulta.query.get(id_agendamento)

            if agendamento.fk_id_encaminhamento:
                encaminhamento = DimEncaminhamento.query.get(agendamento.fk_id_encaminhamento)
                encaminhamento.protocolo_agendamento = None
                id_disponibilidade = agendamento.fk_id_disponibilidade_consulta
                disponibilidade = DimDisponibilidadeConsultas.query.get(id_disponibilidade)
                disponibilidade.status = None
                db.session.delete(agendamento)
                db.session.commit()

                return render_template('menu_paciente.html',
                                       paciente=paciente,
                                       reagendamento=1
                                       )
            else:
                id_disponibilidade = agendamento.fk_id_disponibilidade_consulta
                disponibilidade = DimDisponibilidadeConsultas.query.get(id_disponibilidade)
                disponibilidade.status = None
                db.session.delete(agendamento)
                db.session.commit()

                # return redirect(url_for('mostrar_agenda_paciente', reagendamento=1))
                return render_template('menu_paciente.html',
                                       paciente=paciente,
                                       reagendamento=1
                                       )
        if tipo_agendamento == "exame":
            agendamento = FatoAgendaExame.query.get(id_agendamento)
            encaminhamento = DimEncaminhamento.query.get(agendamento.fk_id_encaminhamento)
            encaminhamento.protocolo_agendamento = None
            id_disponibilidade = agendamento.fk_id_disponibilidade_exame
            disponibilidade = DimDisponibilidadeExames.query.get(id_disponibilidade)
            disponibilidade.status = None
            db.session.delete(agendamento)
            db.session.commit()

            return render_template('menu_paciente.html',
                                   paciente=paciente,
                                   reagendamento=1
                                   )

    return ("<h2 style='margin-top:40px; margin-left:20px;'>ERRO!<br><br>Esta página deve ser acessada exclusivamente "
            "a partir do menu de encaminhamentos pendentes.</h2>")


@app.route('/agendar_encaminhamento', methods=['GET', 'POST'])
@login_required
def agendar_encaminhamento():
    """ Realiza a gravação do agendamento de um encaminhamento no BD e exibe a confirmação para o usuário """
    id_encaminhamento = request.form.get("id_encaminhamento")
    id_disponibilidade = request.form.get("id_disponibilidade")
    tipo_agendamento = request.form.get("tipo_agendamento")
    id_paciente = current_user.id_paciente
    paciente = DimPaciente.query.get(id_paciente)

    if tipo_agendamento == "consulta":
        protocolo = gerar_protocolo('consulta')
        id_medico = DimDisponibilidadeConsultas.query.get(id_disponibilidade).fk_id_medico
        agendamento = FatoAgendaConsulta(
            fk_id_encaminhamento=id_encaminhamento,
            fk_id_medico=id_medico,
            fk_id_paciente=id_paciente,
            fk_id_disponibilidade_consulta=id_disponibilidade,
            protocolo_consulta=protocolo,
            status="Pendente"
        )

        disponibilidade = DimDisponibilidadeConsultas.query.get(id_disponibilidade)
        disponibilidade.status = "indisponivel"

        medico = DimMedico.query.get(id_medico)

        encaminhamento = DimEncaminhamento.query.get(id_encaminhamento)
        encaminhamento.protocolo_agendamento = protocolo

        db.session.add(agendamento)
        db.session.commit()

        # GERAR TELA DE CONFIRMAÇÃO

        return render_template("menu_paciente.html",
                               confirmacao=1,
                               protocolo=protocolo,
                               medico=medico,
                               paciente=paciente,
                               disponibilidade=disponibilidade
                               )

    if tipo_agendamento == "exame":
        protocolo = gerar_protocolo('exame')
        id_exame = DimDisponibilidadeExames.query.get(id_disponibilidade).fk_id_exame
        agendamento = FatoAgendaExame(
            fk_id_encaminhamento=id_encaminhamento,
            fk_id_exame=id_exame,
            fk_id_paciente=id_paciente,
            fk_id_disponibilidade_exame=id_disponibilidade,
            protocolo_exame=protocolo,
            status="Pendente"
        )

        exame = DimTipoExame.query.get(id_exame).tipo_exame

        disponibilidade = DimDisponibilidadeExames.query.get(id_disponibilidade)
        disponibilidade.status = "indisponivel"

        encaminhamento = DimEncaminhamento.query.get(id_encaminhamento)
        encaminhamento.protocolo_agendamento = protocolo

        db.session.add(agendamento)
        db.session.commit()

        return render_template("menu_paciente.html",
                               confirmacao=1,
                               protocolo=protocolo,
                               exame=exame,
                               paciente=paciente,
                               disponibilidade=disponibilidade

                               )

    return redirect(url_for("agendar_clinico"))


@app.route('/cancelar_agendamento', methods=['GET', 'POST'])
@login_required
def cancelar_agendamento():
    """ Cancela o agendamento, deixando o encaminhamento disponível para remarcação;
        para consulta com clínico, o agendamento é apenas excluído"""
    if request.method == 'POST':
        id_agendamento = request.form.get('id_agendamento')
        tipo_agendamento = request.form.get('tipo_agendamento')

        id_paciente = current_user.id_paciente
        paciente = DimPaciente.query.get(id_paciente)

        if tipo_agendamento == "consulta":
            agendamento = FatoAgendaConsulta.query.get(id_agendamento)

            if agendamento.fk_id_encaminhamento:
                encaminhamento = DimEncaminhamento.query.get(agendamento.fk_id_encaminhamento)
                id_disponibilidade = agendamento.fk_id_disponibilidade_consulta
                disponibilidade = DimDisponibilidadeConsultas.query.get(id_disponibilidade)
                disponibilidade.status = None
                db.session.delete(agendamento)
                db.session.delete(encaminhamento)
                db.session.commit()
            else:
                id_disponibilidade = agendamento.fk_id_disponibilidade_consulta
                disponibilidade = DimDisponibilidadeConsultas.query.get(id_disponibilidade)
                disponibilidade.status = None
                db.session.delete(agendamento)
                db.session.commit()

            return render_template('menu_paciente.html',
                                   paciente=paciente,
                                   cancelamento=1
                                   )

        if tipo_agendamento == "exame":
            agendamento = FatoAgendaExame.query.get(id_agendamento)
            encaminhamento = DimEncaminhamento.query.get(agendamento.fk_id_encaminhamento)
            id_disponibilidade = agendamento.fk_id_disponibilidade_exame
            disponibilidade = DimDisponibilidadeExames.query.get(id_disponibilidade)
            disponibilidade.status = None
            db.session.delete(agendamento)
            db.session.delete(encaminhamento)
            db.session.commit()

            return render_template('menu_paciente.html',
                                   paciente=paciente,
                                   cancelamento=1
                                   )

    return ("<h2 style='margin-top:40px; margin-left:20px;'>ERRO!<br><br>Esta página deve ser acessada exclusivamente "
            "a partir da agenda do paciente.</h2>")


# ROTAS MÉDICO

@app.route("/menu_medico")
def menu_principal_medico():
    id_medico = 1
    medico = DimMedico.query.get(id_medico)
    return render_template("menu_medico.html", medico=medico)


@app.route('/gerar_encaminhamento', methods=['GET', 'POST'])
def gerar_encaminhamento():
    """ Gera encaminhamento para uma consulta com especialista ou realização de exame """
    exames = DimTipoExame.query.all()
    medicos = DimMedico.query.filter(DimMedico.especialidade != "Clínico Geral").all()
    pacientes = DimPaciente.query.order_by(DimPaciente.nome).all()

    id_medico = 1
    medico = DimMedico.query.get(id_medico)

    if request.method == 'POST':
        tipo_encaminhamento = request.form.get('rb_tipo_encaminhamento')
        exame = request.form.get('input_tipo_exame')
        id_medico = request.form.get('input_especialidade')
        id_paciente = request.form.get('input_paciente')
        protocolo = gerar_protocolo('encaminhamento')
        if tipo_encaminhamento == app.config["ID_ENCAMINHAMENTO_CONSULTA"]:
            encaminhamento = DimEncaminhamento(
                fk_id_tipo_encaminhamento=tipo_encaminhamento,
                fk_id_paciente=id_paciente,
                fk_id_medico=id_medico,
                protocolo_encaminhamento=protocolo
            )
            db.session.add(encaminhamento)
            db.session.commit()

            tipo = DimTipoEncaminhamento.query.get(tipo_encaminhamento).tipo_encaminhamento
            paciente = DimPaciente.query.get(id_paciente)
            medico = DimMedico.query.get(id_medico)
            protocolo = protocolo

            return render_template("menu_medico.html",
                                   confirmacao=1,
                                   tipo=tipo,
                                   paciente=paciente,
                                   medico=medico,
                                   protocolo=protocolo
                                   )

        if tipo_encaminhamento == app.config["ID_ENCAMINHAMENTO_EXAME"]:
            encaminhamento = DimEncaminhamento(
                fk_id_tipo_encaminhamento=tipo_encaminhamento,
                fk_id_paciente=id_paciente,
                fk_id_exame=exame,
                protocolo_encaminhamento=protocolo
            )
            db.session.add(encaminhamento)
            db.session.commit()

            tipo = DimTipoEncaminhamento.query.get(tipo_encaminhamento).tipo_encaminhamento
            paciente = DimPaciente.query.get(id_paciente)
            exame = DimTipoExame.query.get(exame).tipo_exame
            protocolo = protocolo

            return render_template("menu_medico.html",
                                   confirmacao=1,
                                   tipo=tipo,
                                   paciente=paciente,
                                   exame=exame,
                                   medico=medico,
                                   protocolo=protocolo
                                   )

    return render_template("gerar_encaminhamento_paciente.html",
                           exames=exames,
                           medicos=medicos,
                           pacientes=pacientes,
                           medico=medico
                           )


@app.route('/listar_pacientes', methods=['GET', 'POST'])
def listar_pacientes():
    """ Lista os pacientes agendados com determinado médico """
    id_medico = 1
    pacientes_agendados = (db.session.query(FatoAgendaConsulta)
                           .join(FatoAgendaConsulta.disponibilidade_consulta)
                           .order_by(DimDisponibilidadeConsultas.data_disponivel)
                           .order_by(DimDisponibilidadeConsultas.hora_disponivel)
                           .filter(FatoAgendaConsulta.fk_id_medico == id_medico)
                           .all())
    medico = DimMedico.query.get(id_medico)
    titulo = "Meus pacientes agendados"

    return render_template("listar_pacientes.html",
                           agendamentos=pacientes_agendados,
                           titulo=titulo,
                           medico=medico
                           )


# ROTAS UNIDADE DE SAÚDE

@app.route('/menu_unidade')
def menu_principal_unidade():
    return render_template('menu_admin.html')


@app.route("/cadastrar", methods=['GET', 'POST'])
def cadastrar():
    """ Criação de pré-cadastro na unidade de saúde e geração de código de acesso """
    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        data_nascimento = request.form.get('data_nascimento')
        telefone = request.form.get('telefone')
        email = request.form.get('email')
        logradouro = request.form.get('logradouro')
        numero = request.form.get('numero')
        complemento = request.form.get('complemento')
        bairro = request.form.get('bairro')
        cidade = request.form.get('cidade')
        estado = request.form.get('estado')
        cep = request.form.get('cep')
        access_key = gerar_access_key()

        data_nascimento_objeto = datetime.strptime(data_nascimento, '%Y-%m-%d').date()

        # Validar o CPF digitado
        # *** ATIVAR SOMENTE EM PRODUÇÃO, PARA EVITAR DE TER QUE UTILIZAR CPF VÁLIDOS EM AMBIENTE DE DESENVOLVIMENTO ***
        # if validar_cpf(cpf):

        if DimPaciente.query.filter(DimPaciente.cpf == cpf).first():
            mensagem = f"CPF ({cpf}) já cadastrado. Verifique o número digitado ou faça login."
            return render_template("cadastrar_new.html", mensagem=mensagem)
        elif validar_data_nascimento(data_nascimento):
            paciente = DimPaciente(
                cpf=cpf,
                nome=nome,
                data_nascimento=data_nascimento_objeto,
                telefone=telefone,
                email=email,
                access_key=access_key
            )
            db.session.add(paciente)
            db.session.commit()

            id_novo_paciente = paciente.id_paciente

            endereco = DimEnderecoPaciente(
                fk_id_paciente=id_novo_paciente,
                logradouro=logradouro,
                numero=numero,
                complemento=complemento,
                bairro=bairro,
                cidade=cidade,
                estado=estado,
                cep=cep
            )

            db.session.add(endereco)
            db.session.commit()

            return render_template("menu_admin.html",
                                   sucesso=1,
                                   nome=nome,
                                   cpf=cpf,
                                   access_key=access_key
                                   )
        else:
            mensagem = f"Verifique a data de nascimento inserida."
            return render_template("cadastrar_new.html", mensagem=mensagem)

        # *** ATIVAR SOMENTE EM PRODUÇÃO, PARA EVITAR DE TER QUE UTILIZAR CPF VÁLIDOS EM AMBIENTE DE DESENVOLVIMENTO ***
        # else:
        #     mensagem = f"Verifique o CPF digitado ({cpf}) e tente novamente."
        #     return render_template("cadastrar.html", mensagem=mensagem)

    return render_template("cadastrar_new.html")


# FUNÇÕES AUXILIARES

def gerar_protocolo(tipo):
    """ Gera número de protocolo para tipo de evento """
    def gerar_numero():
        numero = randrange(111111111, 999999999)
        return numero

    if tipo == 'encaminhamento':
        numero = gerar_numero()
        while DimEncaminhamento.query.filter(DimEncaminhamento.protocolo_encaminhamento == numero).first():
            numero = gerar_numero()
        protocolo = "E" + str(numero)
        return protocolo

    if tipo == 'consulta':
        numero = gerar_numero()
        while FatoAgendaConsulta.query.filter(FatoAgendaConsulta.protocolo_consulta == numero).first():
            numero = gerar_numero()
        protocolo = "C" + str(numero)
        return protocolo

    if tipo == 'exame':
        numero = gerar_numero()
        while FatoAgendaExame.query.filter(FatoAgendaExame.protocolo_exame == numero).first():
            numero = gerar_numero()
        protocolo = "X" + str(numero)
        return protocolo


def gerar_access_key(length=4):
    """ Gera chave de acesso para o paciente se autenticar e criar sua senha de login """
    return secrets.token_hex(length)


def validar_cpf(cpf):
    """ Verifica se o CPF digitado é válido """
    # Verificando o comprimento do CPF ou se todos os digitos são iguais (e.g. 111.111.111-11)
    if len(cpf) != 11 or len(set(cpf)) == 1:
        return False
    try:
        digitos = list(map(int, cpf))
    except ValueError:
        return False

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
    """ Verifica se a data informada não é uma data futura ou muito antiga """
    data_nascimento_objeto = datetime.strptime(data_nascimento, "%Y-%m-%d").date()
    hoje = datetime.now().date()
    dias = (hoje - data_nascimento_objeto).days
    if (120 * 365) > dias > 0:
        return True
    else:
        return False
