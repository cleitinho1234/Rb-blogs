from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json

app = Flask(__name__)
app.secret_key = 'chave_mestre_do_negocio'

# Caminho do arquivo de usuários
USERS_FILE = 'usuarios.json'

# SEU EMAIL DE ADMIN (Corrigido sem espaços invisíveis)
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
    # Verifica se você é o dono do site
    e_admin = (user_email == ADMIN_EMAIL)
    
    # Se não for admin e não tiver pago, mostra tela de pagamento
    if not e_admin and not user_info.get('acesso'):
        return render_template('pagamento.html')
    
    # Se for admin, envia a lista completa para o HTML
    lista_para_exibir = usuarios if e_admin else None
    
    return render_template('index.html', 
                           user=user_email, 
                           user_info=user_info, 
                           e_admin=e_admin, 
                           lista_usuarios=lista_para_exibir)

@app.route('/liberar/<email>')
def liberar_acesso(email):
    usuarios = carregar_usuarios()
    if session.get('user') != ADMIN_EMAIL:
        return "Acesso Negado", 403
    
    if email in usuarios:
        usuarios[email]['acesso'] = True
        salvar_usuarios(usuarios)
    return redirect(url_for('index'))

@app.route('/remover/<email>')
def remover_usuario(email):
    usuarios = carregar_usuarios()
    if session.get('user') != ADMIN_EMAIL:
        return "Acesso Negado", 403
    
    if email in usuarios:
        usuarios[email]['acesso'] = False 
        salvar_usuarios(usuarios)
    return redirect(url_for('index'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    usuarios = carregar_usuarios()
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        senha = request.form.get('senha')
        
        if email and email not in usuarios:
            usuarios[email] = {
                'senha': generate_password_hash(senha),
                'senha_limpa': senha,
                'acesso': False
            }
            salvar_usuarios(usuarios)
            session['user'] = email
            return redirect(url_for('index'))
    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    usuarios = carregar_usuarios()
    if request.method == 'POST':
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
