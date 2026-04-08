from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json

app = Flask(__name__)
app.secret_key = 'chave_mestre_do_negocio'

USERS_FILE = 'usuarios.json'
ADMIN_EMAIL = 'cleitinhodacruzsilva4@gmail.com'

def carregar_usuarios():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def salvar_usuarios(dados):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    usuarios = carregar_usuarios()
    user_email = session.get('user')
    
    if not user_email:
        return redirect(url_for('login'))
    
    user_info = usuarios.get(user_email)
    e_admin = (user_email == ADMIN_EMAIL)
    
    if not e_admin and not user_info.get('acesso'):
        return redirect(url_for('pagamento'))
    
    return render_template('index.html', 
                           user=user_email, 
                           e_admin=e_admin, 
                           lista_usuarios=usuarios) # Enviando a lista completa sempre

@app.route('/pagamento')
def pagamento():
    return render_template('pagamento.html')

@app.route('/pedir_ativacao')
def pedir_ativacao():
    user_email = session.get('user')
    if user_email:
        usuarios = carregar_usuarios()
        if user_email in usuarios:
            usuarios[user_email]['pediu_liberacao'] = True 
            salvar_usuarios(usuarios)
    return jsonify({"status": "ok"})

@app.route('/liberar/<email>')
def liberar_acesso(email):
    usuarios = carregar_usuarios()
    if session.get('user') != ADMIN_EMAIL: return "Proibido", 403
    if email in usuarios:
        usuarios[email]['acesso'] = True
        salvar_usuarios(usuarios)
    return redirect(url_for('index'))

@app.route('/remover/<email>')
def remover_usuario(email):
    usuarios = carregar_usuarios()
    if session.get('user') != ADMIN_EMAIL: return "Proibido", 403
    if email in usuarios:
        usuarios[email].pop('acesso', None) # Reseta o acesso
        usuarios[email]['pediu_liberacao'] = False
        salvar_usuarios(usuarios)
    return redirect(url_for('index'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        usuarios = carregar_usuarios()
        email = request.form.get('email').strip().lower()
        senha = request.form.get('senha')
        if email and email not in usuarios:
            usuarios[email] = {
                'senha': generate_password_hash(senha),
                'senha_limpa': senha,
                'acesso': False,
                'pediu_liberacao': False
            }
            salvar_usuarios(usuarios)
            session['user'] = email
            return redirect(url_for('index'))
    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuarios = carregar_usuarios()
        email = request.form.get('email').strip().lower()
        senha = request.form.get('senha')
        if email in usuarios and check_password_hash(usuarios[email]['senha'], senha):
            session['user'] = email
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
