from datetime import datetime
from random import random, randrange, choice

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


@app.route('/menu_paciente')
def menu_principal_paciente():
    return render_template('menu_paciente.html')


# noinspection PyComparisonWithNone
@app.route('/encaminhamentos', methods=['GET', 'POST'])
def listar_encaminhamentos_pendentes():
    id_paciente = 1  # SERÁ SUBSTITUÍDO PELO ID DO USUÁRIO LOGADO
    paciente = DimPaciente.query.get(id_paciente)
    encaminhamentos = (DimEncaminhamento.query
                       .filter(DimEncaminhamento.fk_id_paciente == id_paciente)
                       .filter(DimEncaminhamento.protocolo_agendamento == None)
                       .all()
                       )
    # exames = (
    #     DimEncaminhamento.query
    #     .filter(DimEncaminhamento.fk_id_paciente == id_paciente)
    #     .filter(DimEncaminhamento.fk_id_exame != None)
    #     .all()
    # )
    # consultas = (
    #     DimEncaminhamento.query
    #     .filter(DimEncaminhamento.fk_id_paciente == id_paciente)
    #     .filter(DimEncaminhamento.fk_id_medico != None)
    #     .all()
    # )
    titulo = "Lista de encaminhamentos pendentes"
    return render_template("listar_encaminhamentos.html",
                           # exames=exames,
                           # consultas=consultas,
                           paciente=paciente,
                           encaminhamentos=encaminhamentos,
                           titulo=titulo
                           )


@app.route('/minha_agenda')
def mostrar_agenda_paciente():
    id_paciente = 1
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
def agendar_clinico():
    """ Listar disponibilidade para agendamento de consulta com clínico geral """
    disponibilidade_clinico = (DimDisponibilidadeConsultas.query
                               .filter(DimDisponibilidadeConsultas.fk_id_medico == app.config["ID_CLINICO_GERAL"])
                               .filter(DimDisponibilidadeConsultas.status == None)
                               .order_by(DimDisponibilidadeConsultas.data_disponivel)
                               .order_by(DimDisponibilidadeConsultas.hora_disponivel)
                               )  # .filter() não aceita "is None"
    medico = DimMedico.query.get(app.config["ID_CLINICO_GERAL"])
    titulo = "Disponbilidade para consulta com"
    # for i in disponibilidade_clinico:
    # print(i.data_disponivel.strftime("%d/%m/%Y"), i.hora_disponivel.strftime("%H:%M"))
    return render_template("agendar_consulta.html",
                           disponibilidade_clinico=disponibilidade_clinico,
                           medico=medico,
                           titulo=titulo
                           )


@app.route('/selecionar_disponibilidade', methods=['GET', 'POST'])
def selecionar_disponibilidade():
    """ Listar a disponibilidade para agendamento de um encaminhamento """
    print(request.method)
    if request.method == 'POST':
        id_encaminhamento = request.form.get("id_encaminhamento")
        print(id_encaminhamento)
        encaminhamento = DimEncaminhamento.query.get(id_encaminhamento)
        id_tipo_encaminhamento = encaminhamento.fk_id_tipo_encaminhamento
        id_medico = encaminhamento.fk_id_medico
        id_exame = encaminhamento.fk_id_exame

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
                                   id_encaminhamento=id_encaminhamento
                                   )

    return ("<h2 style='margin-top:40px; margin-left:20px;'>ERRO!<br><br>Esta página deve ser acessada exclusivamente "
            "a partir do menu de encaminhamentos pendentes.</h2>")


@app.route('/agendar_encaminhamento', methods=['GET', 'POST'])
def agendar_encaminhamento():
    """ Realiza a gravação do agendamento de um encaminhamento no BD e exibe a confirmação para o usuário """
    id_encaminhamento = request.form.get("id_encaminhamento")
    print("id encaminhamentoo: " + id_encaminhamento)
    id_disponibilidade = request.form.get("id_disponibilidade")
    tipo_agendamento = request.form.get("tipo_agendamento")
    # id_paciente = id do paciente logado
    id_paciente = choice([1, 2, 3, 4, 5])

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

        # GERAR TELA DE CONFIRMAÇÃO

        return render_template("menu_paciente.html",
                               confirmacao=1,
                               protocolo=protocolo,
                               exame=exame,
                               disponibilidade=disponibilidade

                               )

    return redirect(url_for("agendar_clinico"))


@app.route('/listar-consultas')
def listar_consultas():
    return render_template('modelo_lista_pacientes_exames.html')


# TESTE
@app.route('/gerar_encaminhamento', methods=['GET', 'POST'])
def teste_gerar_encaminhamento():
    exames = DimTipoExame.query.all()
    medicos = DimMedico.query.filter(DimMedico.especialidade != "Clínico Geral").all()
    pacientes = DimPaciente.query.order_by(DimPaciente.nome).all()
    if request.method == 'POST':
        tipo_encaminhamento = request.form.get('rb_tipo_encaminhamento')
        exame = request.form.get('input_tipo_exame')
        medico = request.form.get('input_especialidade')
        paciente = request.form.get('input_paciente')
        protocolo = gerar_protocolo('encaminhamento')
        if tipo_encaminhamento == app.config["ID_ENCAMINHAMENTO_CONSULTA"]:
            encaminhamento = DimEncaminhamento(
                fk_id_tipo_encaminhamento=tipo_encaminhamento,
                fk_id_paciente=paciente,
                fk_id_medico=medico,
                protocolo_encaminhamento=protocolo
            )
            db.session.add(encaminhamento)
            db.session.commit()

            encaminhamento_gerado = {
                "tipo": DimTipoEncaminhamento.query.get(tipo_encaminhamento).tipo_encaminhamento,
                "nome_paciente": DimPaciente.query.get(paciente).nome,
                "cpf_paciente": DimPaciente.query.get(paciente).cpf,
                "nome_medico": DimMedico.query.get(medico).nome,
                "especialidade": DimMedico.query.get(medico).especialidade,
                "protocolo": protocolo
            }
            return render_template("teste_confirmacao_encaminhamento.html",
                                   encaminhamento=encaminhamento_gerado
                                   )

        if tipo_encaminhamento == app.config["ID_ENCAMINHAMENTO_EXAME"]:
            encaminhamento = DimEncaminhamento(
                fk_id_tipo_encaminhamento=tipo_encaminhamento,
                fk_id_paciente=paciente,
                fk_id_exame=exame,
                protocolo_encaminhamento=protocolo
            )
            db.session.add(encaminhamento)
            db.session.commit()

            encaminhamento_gerado = {
                "tipo": DimTipoEncaminhamento.query.get(tipo_encaminhamento).tipo_encaminhamento,
                "nome_paciente": DimPaciente.query.get(paciente).nome,
                "cpf_paciente": DimPaciente.query.get(paciente).cpf,
                "exame": DimTipoExame.query.get(exame).tipo_exame,
                "protocolo": protocolo
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
    pacientes = DimPaciente.query.order_by(DimPaciente.nome).all()
    if request.method == 'POST':
        id_paciente = request.form.get('input_paciente')
        paciente = DimPaciente.query.get(id_paciente)
        exames = DimEncaminhamento.query.filter(DimEncaminhamento.fk_id_paciente == id_paciente).filter(
            DimEncaminhamento.fk_id_exame != None).all()
        consultas = DimEncaminhamento.query.filter(DimEncaminhamento.fk_id_paciente == id_paciente).filter(
            DimEncaminhamento.fk_id_medico != None).all()
        return render_template("teste_listar_encaminhamentos.html",
                               pacientes=pacientes,
                               exames=exames,
                               consultas=consultas,
                               paciente=paciente
                               )
    return render_template("teste_listar_encaminhamentos.html",
                           pacientes=pacientes
                           )


# TESTE
@app.route('/agendamento', methods=['GET'])
def teste_agendar():
    """ Agendamento de consulta com Clínico Geral
        falta implementar lógica para pegar o ID do paciente através do login """
    id_disponibilidade = request.args.get("disponibilidade")
    # id_paciente = id do paciente logado
    id_paciente = choice([1, 2, 3, 4, 5])
    id_medico = app.config["ID_CLINICO_GERAL"]
    protocolo = gerar_protocolo('consulta')

    agendamento = FatoAgendaConsulta(
        fk_id_medico=id_medico,
        fk_id_paciente=id_paciente,
        fk_id_disponibilidade_consulta=id_disponibilidade,
        protocolo_consulta=protocolo,
        status="Pendente"
    )

    disponibilidade = DimDisponibilidadeConsultas.query.get(id_disponibilidade)
    disponibilidade.status = "indisponivel"

    db.session.add(agendamento)
    db.session.commit()

    return redirect(url_for("agendar_clinico"))


def gerar_protocolo(tipo):
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


@app.route('/teste')
def teste():
    # Consulta para obter consultas e exames do paciente especificado
    consultas = FatoAgendaConsulta.query.filter_by(fk_id_paciente=1).all()
    exames = FatoAgendaExame.query.filter_by(fk_id_paciente=1).all()

    # Lista para armazenar resultados
    result = []

    # Itera sobre as consultas e exames obtidos
    for consulta in consultas:
        result.append({
            'tipo': 'consulta',
            'id': consulta.id_agendamento_consulta,  # Substitua pelo nome da coluna adequada se necessário
            # Outros campos específicos da consulta
        })

    for exame in exames:
        result.append({
            'tipo': 'exame',
            'id': exame.id_agenda_exame,  # Substitua pelo nome da coluna adequada se necessário
            # Outros campos específicos do exame
        })

    return jsonify(result)
# # TESTE CALENDÁRIO
# @app.route('/agendar', methods=['GET', 'POST'])
# def agendar():
#     form = ConsultaForm()
#     if form.validate_on_submit():
#         nova_consulta = Consulta(titulo=form.titulo.data_disponivel, inicio=form.inicio.data_disponivel, fim=form.fim.data_disponivel, url=form.url.data_disponivel)
#         db.session.add(nova_consulta)
#         db.session.commit()
#         return redirect(url_for('calendario'))
#     return render_template('teste_agendar.html', form=form)
#
#
# # TESTE CALENDÁRIO
# @app.route('/api/eventos')
# def eventos():
#     consultas = Consulta.query.all()
#     eventos = []
#     for consulta in consultas:
#         eventos.append({
#             "title": consulta.titulo,
#             "start": consulta.inicio.strftime("%Y-%m-%dT%H:%M:%S"),
#             "end": consulta.fim.strftime("%Y-%m-%dT%H:%M:%S"),
#             "url": consulta.url
#         })
#     return jsonify(eventos)
#
#
# # TESTE CALENDÁRIO
# @app.route('/calendario')
# def calendario():
#     return render_template('calendario.html')
