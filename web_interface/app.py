from flask import Flask, render_template, request, redirect, url_for, session
import socket
import json

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

SERVER_IP = '127.0.0.1'
SERVER_PORT = 8080

def conectar_servidor():
    try:
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente.connect((SERVER_IP, SERVER_PORT))
        return cliente
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        return None

def enviar_comando(cliente, dados):
    cliente.send(json.dumps(dados).encode())
    return json.loads(cliente.recv(1024).decode())

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('inbox'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cliente = conectar_servidor()
        if cliente:
            dados = {
                'comando': 'autenticar',
                'username': request.form['username'],
                'senha': request.form['password']
            }
            resposta = enviar_comando(cliente, dados)
            if resposta['status'] == 'sucesso':
                session['username'] = request.form['username']
                return redirect(url_for('inbox'))
            else:
                return render_template('login.html', error=resposta['mensagem'])
        else:
            return render_template('login.html', error="Erro ao conectar ao servidor.")
    return render_template('login.html')

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        cliente = conectar_servidor()
        if cliente:
            dados = {
                'comando': 'cadastrar',
                'nome': request.form['nome'],
                'username': request.form['username'],
                'senha': request.form['password']
            }
            resposta = enviar_comando(cliente, dados)
            return render_template('registrar.html', message=resposta['mensagem'])
        else:
            return render_template('registrar.html', error="Erro ao conectar ao servidor.")
    return render_template('registrar.html')

@app.route('/inbox')
def inbox():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    cliente = conectar_servidor()
    if cliente:
        dados = {
            'comando': 'receber_emails',
            'username': session['username']
        }
        resposta = enviar_comando(cliente, dados)
        if resposta['status'] == 'sucesso':
            # Armazena os e-mails na sessão
            session['emails'] = resposta['emails']
            return render_template('inbox.html', emails=resposta['emails'])
        else:
            return render_template('inbox.html', error=resposta['mensagem'])
    else:
        return render_template('inbox.html', error="Erro ao conectar ao servidor.")

@app.route('/enviar_email', methods=['GET', 'POST'])
def enviar_email():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        cliente = conectar_servidor()
        if cliente:
            dados = {
                'comando': 'enviar_email',
                'remetente': session['username'],
                'destinatario': request.form['destinatario'],
                'assunto': request.form['assunto'],
                'corpo': request.form['corpo']
            }
            resposta = enviar_comando(cliente, dados)
            return render_template('enviar_email.html', message=resposta['mensagem'])
        else:
            return render_template('enviar_email.html', error="Erro ao conectar ao servidor.")
    return render_template('enviar_email.html')

@app.route('/ler_email/<int:email_index>')
def ler_email(email_index):
    if 'username' not in session or 'emails' not in session:
        return redirect(url_for('login'))
    
    # Obtém o e-mail selecionado
    emails = session.get('emails', [])
    if 0 <= email_index < len(emails):
        email = emails[email_index]
        return render_template('ler_email.html', email=email)
    else:
        return render_template('inbox.html', error="E-mail não encontrado.")

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('emails', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)