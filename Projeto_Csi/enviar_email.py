import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# CONFIGURAÇÕES SMTP (EXEMPLO: ROUNDcube/hostinger/locaweb etc.)
SMTP_SERVER = 'mail.csigovernamental.com'
SMTP_PORT = 465  # 465 para SSL, 587 para STARTTLS
USERNAME = 'contato@csigovernamental.com'  # <- ALTERE AQUI
PASSWORD = 'QB2{M3adliM!'  # <- ALTERE AQUI

def enviar_email(destinatario, assunto, corpo):
    msg = MIMEMultipart()
    msg['From'] = USERNAME
    msg['To'] = destinatario
    msg['Subject'] = assunto
    msg.attach(MIMEText(corpo, 'html'))

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(USERNAME, PASSWORD)
            server.send_message(msg)
            print(f"E-mail enviado para {destinatario} com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

def enviar_email_criacao_conta(destinatario, nome, usuario, senha):
    assunto = "Bem-vindo à nossa plataforma!"
    corpo = f"""
    <html>
    <body>
        <h2>Olá {nome},</h2>
        <p>Sua conta foi criada com sucesso pelo nosso sistema!</p>
        <h4>Aqui estão os seus dados de login:</h4>
        <ul>
            <li><strong>Usuário:</strong> {usuario}</li>
            <li><strong>Senha:</strong> {senha}</li>
        </ul>
        <h4 style="color: red;">Recomendação de Segurança:</h4>
        <p>Altere sua senha ao fazer login.</p>
        <h4>Acesse sua conta:</h4>
        <p><a href="www.academycsi.com">www.academycsi.com</a></p>
        <p>Atenciosamente,<br>Equipe CSI Governamental.</p>
    </body>
    </html>
    """
    enviar_email(destinatario, assunto, corpo)

def enviar_email_aviso_lembrete(destinatario, lembrete):
    assunto = "Lembrete: Ação Necessária"
    corpo = f"""
    <html>
    <body>
        <h2>Olá,</h2>
        <p>Este é um lembrete sobre a seguinte ação:</p>
        <blockquote style="border-left: 2px solid #ccc; padding-left: 10px;">
            <strong>{lembrete}</strong>
        </blockquote>
        <p>Atenciosamente,<br>Equipe de Suporte</p>
    </body>
    </html>
    """
    enviar_email(destinatario, assunto, corpo)

def enviar_email_anexo(destinatario, assunto, solicitante, setor, descricao, prioridade, file_path):
    msg = MIMEMultipart()
    msg['From'] = USERNAME
    msg['To'] = destinatario
    msg['Subject'] = assunto

    corpo = f"""
    <html>
    <body>
        <h2>{assunto}</h2>
        <p><strong>Solicitante:</strong> {solicitante}</p>
        <p><strong>Setor:</strong> {setor}</p>
        <p><strong>Descrição:</strong> {descricao}</p>
        <p><strong>Prioridade:</strong> {prioridade}</p>
        <p>Atenciosamente,<br><strong>Equipe CSI Governamental</strong></p>
    </body>
    </html>
    """
    msg.attach(MIMEText(corpo, 'html'))

    if file_path and os.path.exists(file_path):
        part = MIMEBase('application', 'octet-stream')
        with open(file_path, 'rb') as f:
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
        msg.attach(part)

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(USERNAME, PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

def responder_chamado(email_usuario, assunto, descricao, file_path, setor):
    msg = MIMEMultipart()
    msg['From'] = USERNAME
    msg['To'] = email_usuario
    msg['Subject'] = "Chamado finalizado."

    corpo = f"""
    <html>
    <body>
        <h2>Chamado Finalizado</h2>
        <p><strong>Código do chamado:</strong> {assunto}</p>
        <p><strong>Setor:</strong> {setor}</p>
        <p><strong>Descrição:</strong> {descricao}</p>
        <p>Atenciosamente,<br><strong>Equipe CSI Governamental</strong></p>
    </body>
    </html>
    """
    msg.attach(MIMEText(corpo, 'html'))

    if file_path and os.path.exists(file_path):
        part = MIMEBase('application', 'octet-stream')
        with open(file_path, 'rb') as f:
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
        msg.attach(part)

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(USERNAME, PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
