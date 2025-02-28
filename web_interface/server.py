import socket
import threading
import bcrypt
import json
from datetime import datetime

usuarios = {}
emails = {}

ENDPOINT = ('127.0.0.1', 8080)

def tratar_cliente(conn, addr):
    print(f"Conexão estabelecida com {addr}")
    
    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break

            dados = json.loads(data)
            resposta = processar_comando(dados)
            conn.send(resposta.encode())
    
    except Exception as e:
        print(f"Erro com {addr}: {e}")
    
    finally:
        conn.close()
        print(f"Conexão encerrada com {addr}")

def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(ENDPOINT)
    servidor.listen()

    print("Servidor iniciado. Aguardando conexões...")

    while True:
        conn, addr = servidor.accept()
        thread = threading.Thread(target=tratar_cliente, args=(conn, addr), daemon=True)
        thread.start()

def processar_comando(dados):
    entrada = dados.get('comando')

    if entrada == 'cadastrar':
        return json.dumps({"mensagem": cadastrar_usuario(dados['nome'], dados['username'], dados['senha'])})
    elif entrada == 'autenticar':
        return autenticar_usuario(dados['username'], dados['senha'])
    elif entrada == 'enviar_email':
        return json.dumps(enviar_email(dados['remetente'], dados['destinatario'], dados['assunto'], dados['corpo']))
    elif entrada == 'receber_emails':
        return json.dumps(receber_emails(dados['username']))
    else:
        return json.dumps({"mensagem": "Erro: Comando inválido."})

#cadastra users
def cadastrar_usuario(nome, username, senha):
    if username in usuarios:
        return "Erro: username já existe."
    hashed = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())
    usuarios[username] = {'nome': nome, 'senha': hashed}
    return "Sucesso: usuário cadastrado."

def autenticar_usuario(username, senha):
    if username in usuarios and bcrypt.checkpw(senha.encode(), usuarios[username]['senha']):
        return json.dumps({"status": "sucesso", "mensagem": "Autenticação bem-sucedida.", "nome": usuarios[username]["nome"]})
    return json.dumps({"status": "erro", "mensagem": "Username ou senha incorretos."})

# envia os emails
def enviar_email(remetente, destinatario, assunto, corpo):
    if destinatario not in usuarios:
        return {"status": "erro", "mensagem": "Destinatário inexistente."}
    email_id = len(emails) + 1
    emails[email_id] = {
        'id': email_id,
        'remetente': remetente,
        'destinatario': destinatario,
        'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'assunto': assunto,
        'corpo': corpo
    }
    return {"status": "sucesso", "mensagem": "E-mail enviado com sucesso."}

# Recebe os emails
def receber_emails(username):
    recebidos = [email for email in emails.values() if email['destinatario'] == username]
    
    for email_id in list(emails.keys()):
        if emails[email_id]['destinatario'] == username:
            del emails[email_id]
    
    return {"status": "sucesso", "emails": recebidos}


iniciar_servidor()
