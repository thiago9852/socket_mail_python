import socket
import bcrypt
import json
from datetime import datetime

usuarios = {}
emails = {}

ENDPOINT = ('127.0.0.1', 8080)

# Função principal do servidor
def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(ENDPOINT)
    servidor.listen()
    print(f"Servidor iniciado. Aguardando conexões...")

    while True:
        conn, addr = servidor.accept()
        print(f"Conexão estabelecida com {addr}")
        while True:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    break  # Sai do loop se não houver dados

                dados = json.loads(data)
                entrada = dados.get('comando')

                if entrada == 'cadastrar':
                    resposta = json.dumps(
                        {"mensagem": cadastrar_usuario(dados['nome'], dados['username'], dados['senha'])})
                elif entrada == 'autenticar':
                    resposta = autenticar_usuario(dados['username'], dados['senha'])
                elif entrada == 'enviar_email':
                    resposta = json.dumps(
                        enviar_email(dados['remetente'], dados['destinatario'], dados['assunto'], dados['corpo']))
                elif entrada == 'receber_emails':
                    resposta = json.dumps(receber_emails(dados['username']))
                else:
                    resposta = json.dumps({"mensagem": "Erro: Comando inválido."})

                conn.send(resposta.encode())

            except Exception as e:
                print(f"Erro: {e}")
                break

        conn.close()
        print(f"Conexão encerrada com {addr}")

# 02 cadastrar usuário
def cadastrar_usuario(nome, username, senha):
    if username in usuarios:
        return "Erro: username já existe."
    hashed = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())
    usuarios[username] = {'nome': nome, 'senha': hashed}
    return "Sucesso: usuário cadastrado."

# 03 Acessar E-mail
def autenticar_usuario(username, senha):
    if username in usuarios and bcrypt.checkpw(senha.encode(), usuarios[username]['senha']):
        return json.dumps(
            {"status": "sucesso", "mensagem": "Autenticação bem-sucedida.", "nome": usuarios[username]["nome"]})
    return json.dumps({"status": "erro", "mensagem": "Username ou senha incorretos."})

def enviar_email(remetente, destinatario, assunto, corpo):
    if destinatario not in usuarios:
        return {"status": "erro", "mensagem": "Destinatário inexistente."}
    email_id = len(emails) + 1
    emails[email_id] = {
        'remetente': remetente,
        'destinatario': destinatario,
        'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'assunto': assunto,
        'corpo': corpo
    }
    return {"status": "sucesso", "mensagem": "E-mail enviado com sucesso."}

def receber_emails(username):
    recebidos = [email for email in emails.values() if email['destinatario'] == username]
    for email_id in list(emails.keys()):
        if emails[email_id]['destinatario'] == username:
            del emails[email_id]
    return {"status": "sucesso", "emails": recebidos}

iniciar_servidor()