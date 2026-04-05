from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import uuid
import json

app = Flask(__name__)
app.secret_key = 'chave_super_secreta_do_cleitinho'

# Configurações de Pastas
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Arquivos de "Banco de Dados"
POSTS_FILE = 'postagens.json'
USERS_FILE = 'usuarios.json'
ADMINS = ['robertdcg1999@gmail.com', 'cleitinhodacruzsilva4@gmail.com']

# --- FUNÇÕES DE PERSISTÊNCIA ---

def carregar_dados(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    return [] if arquivo == POSTS_FILE else {}

def salvar_dados(arquivo, dados):
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

postagens = carregar_dados(POSTS_FILE)
usuarios = carregar_dados(USERS_FILE)

# --- UTILITÁRIOS ---

@app.context_processor
def utility_processor():
    def get_nome_atual(email):
        user = usuarios.get(email)
        return user.get('nome') if user else email.split('@')[0]
    return dict(get_nome_atual=get_nome_atual)

# --- ROTAS ---

@app.route('/')
def index():
    user_email = session.get('user')
    user_info = usuarios.get(user_email) if user_email else None
    e_admin = user_email in ADMINS
    return render_template('index.html', posts=postagens, user=user_email, user_info=user_info, e_admin=e_admin)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        senha = request.form.get('senha')
        if email and email not in usuarios:
            usuarios[email] = {
                'senha': generate_password_hash(senha), 
                'nome': email.split('@')[0]
            }
            salvar_dados(USERS_FILE, usuarios)
            session['user'] = email
            return redirect(url_for('index'))
    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        senha = request.form.get('senha')
        if email in usuarios and check_password_hash(usuarios[email]['senha'], senha):
            session['user'] = email
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/salvar_nome', methods=['POST'])
def salvar_nome():
    user_email = session.get('user')
    novo_nome = request.form.get('novo_nome', '').strip()
    if user_email and novo_nome:
        usuarios[user_email]['nome'] = novo_nome
        salvar_dados(USERS_FILE, usuarios)
    return redirect(url_for('index'))

@app.route('/postar', methods=['GET', 'POST'])
def postar():
    if session.get('user') not in ADMINS: return "Acesso negado", 403
    if request.method == 'POST':
        arquivo = request.files.get('arquivo')
        desc = request.form.get('descricao')
        filename = secure_filename(arquivo.filename) if arquivo and arquivo.filename != '' else None
        tipo = 'texto'
        if filename:
            arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            ext = os.path.splitext(filename)[1].lower()
            tipo = 'video' if ext in ['.mp4', '.webm', '.mov', '.avi'] else 'foto'
        
        postagens.insert(0, {
            'id': str(uuid.uuid4()), 
            'arquivo': filename, 
            'desc': desc, 
            'tipo': tipo, 
            'likes': [], 
            'comentarios': []
        })
        salvar_dados(POSTS_FILE, postagens)
        return redirect(url_for('index'))
    return render_template('postar.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
