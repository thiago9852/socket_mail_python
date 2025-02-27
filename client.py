import os
import socket
import json


def conectar_servidor(ip, porta):
    try:
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente.connect((ip, porta))
        print("Conectado ao servidor.")
        return cliente
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        return None

def enviar_comando(cliente, dados):
    cliente.send(json.dumps(dados).encode())
    return json.loads(cliente.recv(1024).decode())

def cadastrar_usuario(cliente):
    dados = {
        'comando': 'cadastrar',
        'nome': input("Nome completo: "),
        'username': input("Username: "),
        'senha': input("Senha: ")
    }
    print(enviar_comando(cliente, dados)['mensagem'])

def autenticar_usuario(cliente):
    dados = {
        'comando': 'autenticar',
        'username': input("Username: "),
        'senha': input("Senha: ")
    }
    resposta = enviar_comando(cliente, dados)
    if resposta['status'] == 'sucesso':
        print(f"Bem-vindo, {resposta['nome']}!")
        return dados['username']
    print(resposta['mensagem'])
    return None

def enviar_email(cliente, remetente):
    dados = {
        'comando': 'enviar_email',
        'remetente': remetente,
        'destinatario': input("Destinatário: "),
        'assunto': input("Assunto: "),
        'corpo': input("Corpo do e-mail: ")
    }
    print(enviar_comando(cliente, dados)['mensagem'])

def receber_emails(cliente, username):
    resposta = enviar_comando(cliente, {'comando': 'receber_emails', 'username': username})
    if resposta['status'] == 'sucesso':
        for i, email in enumerate(resposta['emails']):
            print(f"[{i+1}] {email['remetente']}: {email['assunto']}")
        if resposta['emails']:
            escolha = int(input("Qual e-mail deseja ler? ")) - 1
            email = resposta['emails'][escolha]
            print(f"\nDe: {email['remetente']}\nAssunto: {email['assunto']}\nData: {email['data']}\n{email['corpo']}\n")
    else:
        print("Nenhum e-mail recebido.")

def menu_principal():
    print("1) Conectar ao Servidor")
    print("2) Cadastrar Conta")
    print("3) Acessar E-mail")
    return input("Escolha uma opção: ")

def menu_email(cliente, username):
    while True:
        print("\n4) Enviar E-mail\n5) Receber E-mails\n6) Logout")
        opcao = input("Escolha uma opção: ")
        if opcao == '4':
            enviar_email(cliente, username)
        elif opcao == '5':
            receber_emails(cliente, username)
        elif opcao == '6':
            break

def cliente_iniciar():
    cliente = None
    while True:
        opcao = menu_principal()
        if opcao == '1':
            cliente = conectar_servidor(input("IP: "), int(input("Porta: ")))
        elif opcao == '2' and cliente:
            cadastrar_usuario(cliente)
        elif opcao == '3' and cliente:
            if username := autenticar_usuario(cliente):
                menu_email(cliente, username)
        else:
            print("Conecte-se ao servidor primeiro.")


cliente_iniciar()
