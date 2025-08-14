from flask import Flask, render_template, session, redirect, flash, jsonify
from flask import request
import mysql.connector
from datetime import timedelta, datetime
import datetime
import base64
from datetime import date
from enviar_email import *
import os
from werkzeug.utils import secure_filename
import random
import string

database_db = {
    'user': 'panch01111',
    'password': 'Ladas2015@',
    'host': 'vps59715.publiccloud.com.br',
    'database': 'sql10751878'
}

app = Flask(__name__)
app.secret_key = "@sd2¨21%d2$#rd1ed12&21@"
app.permanent_session_lifetime = timedelta(days=365)


def format_brl(value):
    from babel.numbers import format_currency
    return format_currency(value, 'BRL', locale='pt_BR')


app.jinja_env.filters['format_brl'] = format_brl


def format_date_brl(value):
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            return value
    return value.strftime('%d/%m/%Y')


app.jinja_env.filters['format_date_brl'] = format_date_brl


@app.route('/', methods=['GET', 'POST'])
def index():
    if "user" in session:
        user = session["user"]
        banco = mysql.connector.connect(**database_db)
        cursor = banco.cursor()

        sql = 'SELECT * FROM usuarios WHERE usuario = %s'
        val = (user,)
        cursor.execute(sql, val)
        dados = cursor.fetchall()

        return render_template(
            "index.html", dados=dados)
    else:
        return redirect('/login')


@app.route('/alterar_status/<codigo>', methods=['POST'])
def alterar_status(codigo):
    if "user" in session:
        user = session["user"]

        banco = mysql.connector.connect(**database_db)
        cursor = banco.cursor()

        sql = "SELECT nome FROM usuarios WHERE usuario = %s"
        val = (user,)
        cursor.execute(sql, val)
        nome = cursor.fetchall()[0][0]

        try:
            if request.method == 'POST':
                status = request.form['status']
                agora = datetime.datetime.now()

                sql = "UPDATE tarefas SET status = %s WHERE id = %s"
                val = (status, codigo)
                cursor.execute(sql, val)

                data_hora_formatada = agora.strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("INSERT INTO chat (codigo, usuario, mensagem, data_hora) VALUES (%s, %s, %s, %s)",
                               (codigo, 'Sistema',
                                f'<strong>{nome}</strong>Alterou o status dessa tarefa para: <strong>{status}</strong>',
                                data_hora_formatada))

                banco.commit()
                return "Status atualizado com sucesso."
        finally:
            cursor.close()
            banco.close()

    return "Você não pertence a este setor!", 403


@app.route('/mensagens/', methods=['GET', 'POST'])
def mensagens():
    if "user" in session:
        if request.method == 'GET':
            codigo = request.args.get('codigo')
        elif request.method == 'POST':
            data = request.json
            codigo = data.get('codigo')

        banco = mysql.connector.connect(**database_db)
        cursor = banco.cursor()

        try:
            sql = "SELECT * FROM chat WHERE codigo = %s ORDER BY data_hora DESC"
            val = (codigo,)
            cursor.execute(sql, val)
            conversa = cursor.fetchall()

            return jsonify(conversa)
        finally:
            cursor.close()
            banco.close()


@app.route('/enviar_mensagem', methods=['GET', 'POST'])
def enviar_mensagem():
    if "user" in session:
        user = session["user"]

        agora = datetime.datetime.now()
        data_hora_formatada = agora.strftime("%Y-%m-%d %H:%M:%S")
        mensagem = request.json.get('mensagem')

        if not mensagem:
            return jsonify({'error': 'Mensagem invalida'}), 401

        data = request.json
        codigo = data.get('codigo')

        banco = mysql.connector.connect(**database_db)
        cursor = banco.cursor()

        try:
            sql = "SELECT nome FROM usuarios WHERE usuario = %s"
            val = (user,)
            cursor.execute(sql, val)
            nome_usuario = cursor.fetchall()[0][0]

            sql = "INSERT INTO chat (codigo, usuario, mensagem, data_hora) VALUES (%s, %s,%s, %s)"
            val = (codigo, nome_usuario, mensagem, data_hora_formatada)
            cursor.execute(sql, val)
            banco.commit()

            return jsonify({'status': 'Mensagem enviada com sucesso'})
        finally:
            cursor.close()
            banco.close()
    return jsonify({'error': 'Usuário não autenticado'}), 401


@app.route('/login', methods=['GET', 'POST'])
def login():
    banco = mysql.connector.connect(**database_db)
    cursor = banco.cursor()

    if request.method == "POST":
        nome = request.form["usuario"]
        senha_inserida = request.form["senha"]

        try:
            sql = 'SELECT senha FROM usuarios WHERE usuario = %s'
            val = (nome,)
            cursor.execute(sql, val)
            senha_correta_hash = cursor.fetchall()[0][0]

            if senha_correta_hash == senha_inserida:
                session["user"] = nome.lower()
                return redirect('/')
            else:
                flash(u'Sua senha está incorreta!.', 'Erro')
        except:
            flash(u'Usuário não encontrado.', 'Erro')
        finally:
            cursor.close()
            banco.close()
    return render_template("login.html")


@app.route('/criar_tarefa', methods=['GET', 'POST'])
def criar_tarefa():
    if "user" in session:
        user = session["user"]

        banco = mysql.connector.connect(**database_db)
        cursor = banco.cursor()

        try:
            sql = "SELECT * FROM usuarios WHERE usuario = %s"
            val = (user,)
            cursor.execute(sql, val)
            dados = cursor.fetchall()

            setor = dados[0][4]

            cursor.execute("SELECT nome FROM usuarios")
            usuarios = cursor.fetchall()

            if setor == "administrador":
                if request.method == "POST":
                    objetivo_geral = request.form["objetivo_geral"]
                    acoes_oque = request.form["acoes_oque"]
                    porque = request.form["porque"]
                    responsaveis = request.form.getlist('responsaveis')
                    responsavel = ','.join(responsaveis)
                    prazo_final = request.form["prazo_final"]
                    custo = request.form["custo"]
                    politica = request.form["politica"]

                    agora = datetime.datetime.now()
                    data_hora_formatada = agora.strftime("%Y-%m-%d %H:%M:%S")

                    sql = "INSERT INTO tarefas (remetente, objetivo, acoes_oque, por_que, responsavel, status, data_inicio, prazo_final, custo, politica) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    val = ((user, objetivo_geral, acoes_oque, porque, responsavel, 'nao_iniciada', data_hora_formatada,
                            prazo_final, custo, politica))
                    cursor.execute(sql, val)
                    banco.commit()

                    flash(u'Sua tarefa foi criada com sucesso!', 'Sucesso')
                    return render_template("criar_tarefa.html", dados=dados, usuarios=usuarios)
                else:
                    return render_template("criar_tarefa.html", dados=dados, usuarios=usuarios)
            else:
                flash(u'Apenas administradores podem lançar tarefas!', 'Erro')
                return redirect('/')
        finally:
            cursor.close()
            banco.close()
    else:
        return redirect('/login')


@app.route('/criar_usuario', methods=['GET', 'POST'])
def criar_usuario():
    if "user" in session:
        user = session["user"]

        banco = mysql.connector.connect(**database_db)
        cursor = banco.cursor()

        try:
            sql = "SELECT * FROM usuarios WHERE usuario = %s"
            val = (user,)
            cursor.execute(sql, val)
            dados = cursor.fetchall()

            if dados[0][0] == "vitoria.vieira":
                if request.method == "POST":
                    nome = request.form["nome"]
                    usuario = request.form["usuario"]
                    senha = request.form["senha"]
                    confirmar_senha = request.form["confirmar_senha"]
                    email = request.form["email"]
                    foto_user = request.files["foto_url"]
                    setor = request.form["setor"]

                    sql = "SELECT * FROM usuarios WHERE usuario = %s"
                    val = (usuario,)
                    cursor.execute(sql, val)
                    usuario_existe = cursor.fetchall()

                    if not usuario_existe:
                        if senha == confirmar_senha:
                            foto_user_binario = foto_user.read()
                            foto_user_base64 = base64.b64encode(foto_user_binario).decode('utf-8')

                            cursor.execute(
                                "INSERT INTO usuarios (nome, usuario, senha, email, foto_user, setor, responsavel) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                (nome, usuario, senha, email, foto_user_base64, setor, user))
                            banco.commit()
                            enviar_email_criacao_conta(email, nome, usuario, senha)
                            flash(
                                u'Usuário criado com sucesso! Notificamos o usuário via e-mail com as informações de login.',
                                'Sucesso')
                        else:
                            flash(u'As senhas são diferentes.', 'Erro')
                    else:
                        flash(u'Usuario ja existe no banco de dados.', 'Erro')
                    return render_template("criar_usuario.html", dados=dados)
                else:
                    return render_template("criar_usuario.html", dados=dados)
            else:
                flash(u'Apenas administradores podem criar usuários!', 'Erro')
                return redirect('/')
        finally:
            cursor.close()
            banco.close()

    else:
        return redirect('/login')


@app.route('/configuracao', methods=['GET', 'POST'])
def configuracao():
    if "user" in session:
        user = session["user"]

        banco = mysql.connector.connect(**database_db)
        cursor = banco.cursor()

        try:
            if request.method == "POST":
                email = request.form["email"]
                foto_url = request.files["foto_url"]
                foto_user_binario = foto_url.read()
                foto_user_base64 = base64.b64encode(foto_user_binario).decode('utf-8')

                sql = "UPDATE usuarios SET email = %s WHERE usuario = %s"
                val = (email, user)
                cursor.execute(sql, val)

                if foto_user_base64:
                    if foto_url.content_type in ["image/png", "image/jpeg"]:
                        sql = "UPDATE usuarios SET foto_user = %s WHERE usuario = %s"
                        val = (foto_user_base64, user)
                        cursor.execute(sql, val)
                    else:
                        flash("Apenas arquivos PNG e JPG são permitidos.", "Erro")
                        return redirect('/configuracao')

                banco.commit()

                flash(u'Seus dados foram alterados.', 'Sucesso')
                return redirect('/configuracao')
            else:
                sql = "SELECT * FROM usuarios WHERE usuario = %s"
                val = (user,)
                cursor.execute(sql, val)
                dados = cursor.fetchall()
                return render_template("configuracao.html", dados=dados)
        finally:
            cursor.close()
            banco.close()
    else:
        return redirect('/login')


@app.route('/alterar_senha', methods=['POST'])
def alterar_senha():
    if "user" in session:
        user = session["user"]
        banco = mysql.connector.connect(**database_db)
        cursor = banco.cursor()

        try:
            senha_atual = request.form["senha_atual"]
            senha = request.form["nova_senha"]
            senha_confirmar = request.form["senha_confirmar"]

            sql = "SELECT * FROM usuarios WHERE usuario = %s"
            val = (user,)
            cursor.execute(sql, val)

            dados = cursor.fetchall()[0]

            senha_correta = dados[1]
            email = dados[3]

            if senha_correta == senha_atual:
                if senha == senha_confirmar:
                    if (len(senha) >= 8 and
                            any(c.islower() for c in senha) and
                            any(c.isupper() for c in senha) and
                            any(c.isdigit() for c in senha) and
                            any(c in "!@#$%^&*" for c in senha)):
                        sql = "UPDATE usuarios SET senha = %s WHERE usuario = %s"
                        val = (senha, user)
                        cursor.execute(sql, val)

                        enviar_email_aviso_lembrete(email,
                                                    "A sua senha foi alterada com sucesso. Por razões de segurança, recomendamos que você não compartilhe sua nova senha com ninguém. Certifique-se de que sua nova senha seja forte e única. Se você não solicitou esta alteração, entre em contato com o suporte imediatamente")
                        flash(u'Senha alterada com sucesso.', 'Sucesso')
                        banco.commit()
                    else:
                        flash(u'Senha não atende aos requisitos:\n'
                              '- Mínimo de 8 caracteres\n'
                              '- Deve conter letras maiúsculas\n'
                              '- Deve conter letras minúsculas\n'
                              '- Deve incluir pelo menos um número\n'
                              '- Deve conter caracteres especiais (como !@#$%^&*)',
                              'Alerta')
                        return redirect('/configuracao')
                else:
                    flash(u'Senhas não coincidem.', 'Alerta')
                    return redirect('/configuracao')
            else:
                flash(u'Senha atual incorreta.', 'Erro')
                return redirect('/configuracao')

            return redirect('/configuracao')
        finally:
            cursor.close()
            banco.close()


@app.route('/usuarios', methods=['GET', 'POST'])
def usuarios():
    if "user" in session:
        user = session["user"]

        banco = mysql.connector.connect(**database_db)
        cursor = banco.cursor()

        try:
            sql = "SELECT * FROM usuarios WHERE usuario = %s"
            val = (user,)
            cursor.execute(sql, val)
            dados = cursor.fetchall()

            if dados[0][0] == "vitoria.vieira":
                cursor.execute("SELECT * FROM usuarios")
                dados_pessoas = cursor.fetchall()

                return render_template('usuarios.html', dados=dados,
                                       len_usuarios=len(dados_pessoas), dados_pessoas=dados_pessoas)
            else:
                flash(u'Apenas administradores podem visualizar os usuários!', 'Erro')
                return redirect('/')
        finally:
            cursor.close()
            banco.close()
    else:
        return redirect('/login')


@app.route('/revisao_politica', methods=['GET', 'POST'])
def revisao_politica():
    if "user" in session:
        user = session["user"]

        banco = mysql.connector.connect(**database_db)
        cursor = banco.cursor()

        try:
            cursor.execute("SELECT * FROM datas_politica")
            dados = cursor.fetchall()

            sql = "SELECT * FROM usuarios WHERE usuario = %s"
            val = (user,)
            cursor.execute(sql, val)
            dados_user = cursor.fetchall()

            data_atual = date.today()

            return render_template('revisao_politica.html', dados_user=dados_user, dados=dados, len_dados=len(dados),
                                   data_atual=data_atual)
        finally:
            cursor.close()
            banco.close()
    else:
        return redirect('/login')


@app.route('/tarefas_arquivadas', methods=['GET', 'POST'])
def tarefas_arquivadas():
    if "user" in session:
        user = session["user"]

        banco = mysql.connector.connect(**database_db)
        cursor = banco.cursor()

        try:
            sql = "SELECT * FROM usuarios WHERE usuario = %s"
            val = (user,)
            cursor.execute(sql, val)
            dados = cursor.fetchall()
            setor = dados[0][4]

            if setor == "administrador":
                cursor.execute("SELECT * FROM tarefas WHERE status = 'arquivada'")
                dados_tarefas = cursor.fetchall()

                return render_template('arquivadas.html', dados=dados, dados_tarefas=dados_tarefas,
                                       len_dados_tarefas=len(dados_tarefas))
            else:
                flash(u'Apenas administradores podem visualizar as tarefas arquivadas!', 'Erro')
                return redirect('/')
        finally:
            cursor.close()
            banco.close()
    else:
        return redirect('/login')


@app.route('/dashboard_tarefas', methods=['GET', 'POST'])
def dashboard_tarefas():
    if "user" in session:
        user = session["user"]

        banco = mysql.connector.connect(**database_db)
        cursor = banco.cursor(dictionary=True)

        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s", (user,))
        dados = cursor.fetchall()

        try:
            # Status das Tarefas
            cursor.execute("SELECT * FROM tarefas WHERE status = 'nao_iniciada'")
            nao_iniciada = len(cursor.fetchall())
            cursor.execute("SELECT * FROM tarefas WHERE status = 'em_andamento'")
            em_andamento = len(cursor.fetchall())
            cursor.execute("SELECT * FROM tarefas WHERE status = 'pausada'")
            pausada = len(cursor.fetchall())
            cursor.execute("SELECT * FROM tarefas WHERE status = 'pronta_para_revisao'")
            pronta_para_revisao = len(cursor.fetchall())
            cursor.execute("SELECT * FROM tarefas WHERE status = 'concluida'")
            concluida = len(cursor.fetchall())
            labels = ["Nao iniciada", "Em andamento", "Pausada", "Pronta para Revisao", "Concluida"]
            status_data = [nao_iniciada, em_andamento, pausada, pronta_para_revisao, concluida]

            cursor.execute("""
                        SELECT DATE(data_inicio) AS data_criacao, COUNT(*) AS quantidade
                        FROM tarefas
                        GROUP BY DATE(data_inicio)
                        ORDER BY DATE(data_inicio);
                    """)
            tarefas_data = cursor.fetchall()

            dates = [row['data_criacao'].strftime('%d/%m/%Y') for row in tarefas_data]
            counts = [row['quantidade'] for row in tarefas_data]

            ## Tarefas por usuário e concluídas
            query = """
                        SELECT u.nome,
                            COUNT(t.id) AS total_tarefas,
                            SUM(CASE WHEN t.status = 'concluida' THEN 1 ELSE 0 END) AS tarefas_concluidas
                        FROM usuarios u
                        JOIN tarefas t ON FIND_IN_SET(u.nome, t.responsavel) > 0
                        GROUP BY u.nome;
                    """
            cursor.execute(query)
            data = cursor.fetchall()

            user_names = [row['nome'] for row in data]
            task_counts = [row['total_tarefas'] for row in data]
            completed_tasks = [row['tarefas_concluidas'] for row in data]

            #####
            cursor.execute(
                "SELECT * FROM tarefas WHERE status NOT IN ('arquivada', 'concluida') ORDER BY prazo_final ASC LIMIT 10")

            dados_task = cursor.fetchall()

            return render_template('dashboard_tarefas.html',
                                   status_labels=labels,
                                   status_data=status_data,
                                   dados=dados, dates=dates, counts=counts,
                                   user_names=user_names, task_counts=task_counts,
                                   completed_tasks=completed_tasks, dados_task=dados_task,
                                   len_dados_task=len(dados_task))
        finally:
            cursor.close()
            banco.close()


@app.route('/academico', methods=['GET', 'POST'])
def academico():
    if "user" in session:
        user = session["user"]

        banco = mysql.connector.connect(**database_db)
        cursor = banco.cursor()

        try:
            sql = "SELECT * FROM usuarios WHERE usuario = %s"
            val = (user,)
            cursor.execute(sql, val)
            dados = cursor.fetchall()

            cursor.execute("SELECT * FROM cursos")
            cursos = cursor.fetchall()

            return render_template('academico.html', dados=dados, cursos=cursos, len_cursos=len(cursos))
        finally:
            cursor.close()
            banco.close()
    else:
        return redirect('/login')


@app.route('/academico/curso/<curso>', methods=['GET', 'POST'])
def aulas_disponivel(curso):
    if "user" in session:
        user = session["user"]

        banco = mysql.connector.connect(**database_db)
        cursor = banco.cursor()

        try:
            # Obtendo os dados do usuário
            sql = "SELECT * FROM usuarios WHERE usuario = %s"
            val = (user,)
            cursor.execute(sql, val)
            dados = cursor.fetchall()

            # Obtendo todas as aulas de um curso
            sql = "SELECT * FROM aulas WHERE curso_id = %s"
            val = (curso,)
            cursor.execute(sql, val)
            aulas = cursor.fetchall()

            sql = "SELECT * FROM avaliacoes_aula WHERE curso_id = %s AND usuario = %s"
            val = (curso, user)
            cursor.execute(sql, val)
            avaliacoes = cursor.fetchall()
        finally:
            cursor.close()
            banco.close()
        return render_template('aulas_disponivel.html', dados=dados, len_aulas=len(aulas), aulas=aulas,
                               avaliacoes=len(avaliacoes))
    else:
        return redirect('/login')


@app.route('/academico/curso/<curso>/<aula>', methods=['GET', 'POST'])
def assistir_aula(curso, aula):
    if "user" not in session:
        return redirect('/login')

    user = session["user"]
    banco = mysql.connector.connect(**database_db)
    cursor = banco.cursor(dictionary=True)

    try:
        # Obtendo os dados do usuário
        sql = "SELECT * FROM usuarios WHERE usuario = %s"
        val = (user,)
        cursor.execute(sql, val)
        dados = cursor.fetchall()

        # Aula atual
        cursor.execute("SELECT * FROM aulas WHERE curso_id = %s AND episodio = %s", (curso, aula))
        dados_aula = cursor.fetchall()

        video_link = dados_aula[0]['video_url']
        video_id = video_link.split("/")[-1].split("?")[0]

        # POST = aluno respondeu avaliação
        if request.method == 'POST':
            cursor.execute("SELECT * FROM avaliacoes_aula WHERE curso_id = %s AND aula = %s AND usuario = %s",
                           (curso, aula, user))
            ja_concluida = cursor.fetchall()

            if not ja_concluida:
                p1 = request.form.get('pergunta1')
                p2 = request.form.get('pergunta2')
                p3 = request.form.get('pergunta3')

                cursor.execute("""
                  INSERT INTO avaliacoes_aula (usuario, curso_id, aula, pergunta1, pergunta2, pergunta3)
                  VALUES (%s, %s, %s, %s, %s, %s)
                """, (user, curso, aula, p1, p2, p3))
                banco.commit()

            cursor.execute("SELECT * FROM aulas WHERE curso_id = %s AND episodio = %s", (curso, int(aula) + 1))
            proxima_aula = cursor.fetchone()

            if proxima_aula:
                proxima_url = f"/academico/curso/{curso}/{int(aula) + 1}"
            else:
                proxima_url = "/certificado_curso"

            return jsonify({"next": proxima_url})

        # Verifica próxima aula
        cursor.execute("SELECT * FROM aulas WHERE curso_id = %s AND episodio = %s", (curso, int(aula) + 1))
        proxima_aula = cursor.fetchone()

        if proxima_aula is not None:
            link_proxima = f"/academico/curso/{curso}/{int(aula) + 1}"
        else:
            link_proxima = "/certificado_curso"
    finally:
        cursor.close()
        banco.close()

    return render_template(
        'assistir_aula.html',
        dados=dados,
        dados_aula=dados_aula,
        video_id=video_id,
        link_proxima=link_proxima,
        proxima_aula=proxima_aula
    )


@app.route('/certificado_curso', methods=['GET', 'POST'])
def certificado_curso():
    if "user" in session:
        user = session["user"]
        return 'Parabens pela conclusao do seu curso!'
    else:
        return redirect("/")


@app.route('/organograma', methods=['GET', 'POST'])
def organograma():
    if "user" in session:
        user = session["user"]
        return render_template('organograma.html')
    else:
        return redirect("/")


@app.route('/enviar_chamado', methods=['GET', 'POST'])
def enviar_chamado():
    if "user" in session:
        user = session["user"]

        banco = mysql.connector.connect(**database_db)
        cursor = banco.cursor()

        try:
            sql = 'SELECT * FROM usuarios WHERE usuario = %s'
            val = (user,)
            cursor.execute(sql, val)
            dados = cursor.fetchall()
        finally:
            cursor.close()
            banco.close()
        return render_template('chamados_juridico.html', dados=dados)


ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'docx', 'xlsx'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/realizar_chamado/<assunto>/<setor_destinatario>', methods=['POST'])
def realizar_chamado(assunto, setor_destinatario):
    if "user" in session:
        user = session["user"]
        banco = mysql.connector.connect(**database_db)
        cursor = banco.cursor()

        caracteres = string.ascii_letters + string.digits
        codigo = ''.join(random.choices(caracteres, k=15))

        try:
            sql = 'SELECT * FROM usuarios WHERE usuario = %s'
            val = (user,)
            cursor.execute(sql, val)
            dados = cursor.fetchall()

            solicitante = dados[0][2]
            setor = dados[0][4]
            descricao = request.form['descricao']
            prioridade = request.form['prioridade']

            if 'arquivos' not in request.files or request.files['arquivos'].filename == '':
                return "Nenhum arquivo anexado", 400

            arquivo = request.files['arquivos']

            # Valida o tipo de arquivo
            if not allowed_file(arquivo.filename):
                return "Tipo de arquivo não permitido. Apenas arquivos PDF, JPG, PNG, DOCX, e XLSX são aceitos.", 400

            # Verifica o tamanho do arquivo
            arquivo.seek(0, os.SEEK_END)
            file_size = arquivo.tell()
            if file_size > 20 * 1024 * 1024:
                return "Arquivo muito grande. O tamanho máximo permitido é 20MB.", 400
            arquivo.seek(0)

            filename = secure_filename(arquivo.filename)
            file_path = os.path.join(app.root_path, 'static/uploads', filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            arquivo.save(file_path)

            sql = 'SELECT email FROM usuarios WHERE setor = %s'
            val = (setor_destinatario,)
            cursor.execute(sql, val)
            emails = cursor.fetchall()
            for email in emails:
                enviar_email_anexo(
                    destinatario=f'{email[0]}',
                    assunto=f"{assunto}",
                    solicitante=solicitante,
                    prioridade=prioridade,
                    setor=setor,
                    descricao=descricao,
                    file_path=file_path
                )

            sql = """
            INSERT INTO chamados (codigo,solicitante, setor_origem, setor_destinatario, descricao, prioridade, assunto, file_path, status,usuario) 
            VALUES (%s, %s, %s, %s, %s, %s, %s,%s,%s,%s)
            """
            val = (
                codigo, solicitante, setor, setor_destinatario, descricao, prioridade, assunto, filename, "Aberto",
                user)
            cursor.execute(sql, val)
            banco.commit()
            return "Chamado enviado e registrado com sucesso!"
        finally:
            cursor.close()
            banco.close()


@app.route('/listar_chamados')
def listar_chamados():
    if "user" in session:
        user = session["user"]
        banco = mysql.connector.connect(**database_db)
        cursor = banco.cursor(dictionary=True)
        try:
            sql = 'SELECT * FROM usuarios WHERE usuario = %s'
            val = (user,)
            cursor.execute(sql, val)
            dados_user = cursor.fetchall()

            sql = "SELECT * FROM chamados ORDER BY data_criacao DESC"
            cursor.execute(sql)
            chamados = cursor.fetchall()
        finally:
            cursor.close()
            banco.close()
        return render_template('chamados.html', len_chamados=len(chamados), dados_user=dados_user, dados=chamados)


@app.route('/alterar_status_chamado/<codigo>', methods=['POST'])
def alterar_status_chamado(codigo):
    if "user" in session:
        user = session["user"]
        banco = mysql.connector.connect(**database_db)
        cursor = banco.cursor()

        try:
            if request.method == 'POST':
                status = request.form['status']
                sql = "UPDATE chamados SET status = %s WHERE codigo = %s"
                val = (status, codigo)
                cursor.execute(sql, val)

                sql = "SELECT nome FROM usuarios WHERE usuario = %s"
                val = (user,)
                cursor.execute(sql, val)
                nome = cursor.fetchall()[0][0]
                agora = datetime.datetime.now()

                data_hora_formatada = agora.strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("INSERT INTO chat (codigo, usuario, mensagem, data_hora) VALUES (%s, %s, %s, %s)",
                               (codigo, 'Sistema',
                                f'<strong>{nome}</strong>Alterou o status dessa tarefa para: <strong>{status.title().replace("-", " ")}</strong>',
                                data_hora_formatada))

                banco.commit()
                return "Status atualizado com sucesso."
        finally:
            cursor.close()
            banco.close()
    return "Você não pertence a este setor!", 403


@app.route('/resposta_chamado/<codigo>', methods=['GET', 'POST'])
def resposta_chamado(codigo):
    if "user" in session:
        user = session["user"]
        banco = mysql.connector.connect(**database_db)
        cursor = banco.cursor()
        try:
            sql = 'SELECT * FROM usuarios WHERE usuario = %s'
            val = (user,)
            cursor.execute(sql, val)
            dados = cursor.fetchall()

            sql = 'SELECT * FROM chamados WHERE codigo = %s'
            val = (codigo,)
            cursor.execute(sql, val)
            dados_chamado = cursor.fetchall()

            if request.method == 'POST':
                descricao = request.form["descricao"]
                arquivo = request.files['arquivos']

                if not allowed_file(arquivo.filename) or arquivo.tell() > 20 * 1024 * 1024:
                    return "Tipo de arquivo não permitido ou arquivo muito grande.", 400

                filename = secure_filename(arquivo.filename)
                file_path = os.path.join(app.root_path, 'static/uploads', filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                arquivo.save(file_path)

                sql = 'SELECT email FROM usuarios WHERE usuario = %s'
                val = (dados_chamado[0][10],)
                cursor.execute(sql, val)
                email = cursor.fetchall()[0][0]
                responder_chamado(
                    email_usuario=email,
                    assunto=codigo,
                    descricao=descricao,
                    file_path=file_path,
                    setor=dados_chamado[0][3]
                )

                try:
                    os.remove(file_path)
                except OSError as e:
                    print(f"Erro ao deletar arquivo: {e}")

                return render_template('resposta_chamado.html', dados=dados, dados_chamado=dados_chamado)
            else:
                return render_template('resposta_chamado.html', dados=dados, dados_chamado=dados_chamado)
        finally:
            cursor.close()
            banco.close()
    else:
        return redirect('/login')


@app.route('/dashboard')
def dashboard():
    if "user" in session:
        user = session["user"]
        banco = mysql.connector.connect(**database_db)
        cursor = banco.cursor(dictionary=True)

        sql = 'SELECT * FROM usuarios WHERE usuario = %s'
        val = (user,)
        cursor.execute(sql, val)
        dados = cursor.fetchall()

        cursor.close()
        banco.close()
        lista_de_usuarios = [
            {
                "nome": "Ana Clara",
                "ultimo_login": "2025-07-28 09:15",
                "ultimo_video": "Ambiente Organizacional",
                "total_visualizacoes": 14,
                "media_nota": 8.7
            },
            {
                "nome": "Bruno Souza",
                "ultimo_login": "2025-07-29 08:30",
                "ultimo_video": "Ética Corporativa",
                "total_visualizacoes": 22,
                "media_nota": 9.1
            },
            {
                "nome": "Carlos Lima",
                "ultimo_login": "2025-07-25 15:42",
                "ultimo_video": "Gestão de Projetos",
                "total_visualizacoes": 10,
                "media_nota": 7.5
            },
            {
                "nome": "Daniela Rocha",
                "ultimo_login": "2025-07-28 18:05",
                "ultimo_video": "Governança Corporativa",
                "total_visualizacoes": 17,
                "media_nota": 8.3
            }
        ]

        return render_template("dashboard.html",
                               total_usuarios=len(lista_de_usuarios),
                               usuarios_online_hoje=2,
                               total_visualizacoes=sum(u["total_visualizacoes"] for u in lista_de_usuarios),
                               media_geral_notas=round(
                                   sum(u["media_nota"] for u in lista_de_usuarios) / len(lista_de_usuarios), 2),
                               usuarios=lista_de_usuarios,
                               dias_acessos=["Seg", "Ter", "Qua", "Qui", "Sex"],
                               acessos_diarios=[10, 20, 15, 30, 25],
                               cursos=["Gestão", "Planejamento", "Jurídico"],
                               notas_medias=[8.2, 7.9, 9.1],
                               dados=dados
                               )


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
