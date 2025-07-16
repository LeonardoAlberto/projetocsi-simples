import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# Configurações do servidor SMTP
SMTP_SERVER = 'smtp.gmail.com'  # Substitua pelo servidor SMTP
SMTP_PORT = 587  # Porta do servidor SMTP
USERNAME = 'contato.csigovernamental@gmail.com'
PASSWORD = 'hfro ddqi nycu fsvk'


def enviar_email(destinatario, assunto, corpo):
    # Criação do objeto de mensagem
    msg = MIMEMultipart()
    msg['From'] = USERNAME
    msg['To'] = destinatario
    msg['Subject'] = assunto

    # Anexa o corpo da mensagem como HTML
    msg.attach(MIMEText(corpo, 'html'))

    try:
        # Conexão com o servidor SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Habilita a conexão segura
        server.login(USERNAME, PASSWORD)
        server.send_message(msg)
        print(f"E-mail enviado para {destinatario} com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
    finally:
        server.quit()


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
        <p>Para garantir a segurança da sua conta, sugerimos que você altere sua senha assim que fizer o login.</p>

        <p>Por favor, mantenha sua nova senha em um local seguro e não compartilhe com ninguém.</p>

        <h4>Acesse sua conta:</h4>
        <p><a href="www.csigovernamental.com">www.csigovernamental.com</a></p>

        <p>Agradecemos por se inscrever! Se você tiver alguma dúvida, não hesite em nos contatar.</p>

        <p>Atenciosamente,<br>
        equipe CSI Governamental.</p>
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
        <p>Atenciosamente,<br>
        Equipe de Suporte</p>
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
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email</title>
    </head>
    <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4;">
        <div style="max-width: 600px; margin: auto; background: #fff; border-radius: 8px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); padding: 20px;">
            <h2 style="color: #333; border-bottom: 2px solid #007BFF; padding-bottom: 10px;">{assunto}</h2>
            <p style="color: #555; line-height: 1.5;">
                <br><strong>Solicitante:</strong> {solicitante}<br>
                <br><strong>Setor:</strong> {setor}<br>
                <br><strong>Descrição:</strong> {descricao}<br>
                <br><strong>Prioridade:</strong> {prioridade}
            </p>
            <p style="color: #555; line-height: 1.5;">
                Atenciosamente,<br>
                <strong>Equipe CSI Governamental</strong>
            </p>
        </div>
    </body>
    </html>

    """
    msg.attach(MIMEText(corpo, 'html'))

    # Anexar o arquivo, se fornecido
    if file_path:
        part = MIMEBase('application', 'octet-stream')
        with open(file_path, 'rb') as f:
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
        msg.attach(part)

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(USERNAME, PASSWORD)
        server.send_message(msg)
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
    finally:
        server.quit()


def responder_chamado(email_usuario, assunto, descricao, file_path, setor):
    msg = MIMEMultipart()
    msg['From'] = USERNAME
    msg['To'] = email_usuario
    msg['Subject'] = "Chamado finalizado."

    corpo = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email</title>
    </head>
    <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; margin: 0; padding: 20px; background-color: #f1f1f1;">
        <div style="max-width: 600px; margin: auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1); padding: 20px;">
            <h2 style="color: #0056b3; padding-bottom: 0px; margin-bottom: 0px; font-weight: normal; font-size: 24px;">Chamado Finalizado</h2>
            <p style="color: #0056b3; border-bottom: 3px solid #004494; padding-bottom: 15px; margin-bottom: 20px; font-weight: normal; font-size: 18px;">Codigo do chamado: {assunto}</p>
            <p style="color: #555; line-height: 1.6; margin-bottom: 15px; font-size: 16px;">
                <strong>Setor:</strong> {setor}
            </p>
            <p style="color: #555; line-height: 1.6; margin-bottom: 20px; font-size: 16px;">
                <strong>Descrição:</strong> {descricao}
            </p>
            <div style="margin-top: 20px; font-size: 14px; color: #777; text-align: right;">
                Atenciosamente,<br>
                <strong>Equipe CSI Governamental</strong>
            </div>
        </div>
    
    </body>
    </html>

    """
    msg.attach(MIMEText(corpo, 'html'))

    # Anexar o arquivo, se fornecido
    if file_path:
        part = MIMEBase('application', 'octet-stream')
        with open(file_path, 'rb') as f:
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
        msg.attach(part)

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(USERNAME, PASSWORD)
        server.send_message(msg)
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
    finally:
        server.quit()
