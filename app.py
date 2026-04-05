from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import uuid
import json

app = Flask(__name__)
app.secret_key = 'chave_super_secreta_do_cleitinho'

# Configurações de Upload
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Arquivos de banco de dados simples
POSTS_FILE = 'postagens.json'
ADMINS = ['robertdcg1999@gmail.com', 'cleitinhodacruzsilva4@gmail.com']
usuarios = {} 

# Função para carregar posts do arquivo
def carregar_posts():
    if os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Função para salvar posts no arquivo
def salvar_posts(posts):
    with open(POSTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)

postagens = carregar_posts()

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
            usuarios[email] = {'senha': generate_password_hash(senha), 'nome': email.split('@')[0]}
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
    if not user_email or not novo_nome: return redirect(url_for('index'))
    usuarios[user_email]['nome'] = novo_nome
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
        
        nova_postagem = {'id': str(uuid.uuid4()), 'arquivo': filename, 'desc': desc, 'tipo': tipo, 'likes': [], 'comentarios': []}
        postagens.insert(0, nova_postagem)
        salvar_posts(postagens) # Salva no arquivo JSON
        return redirect(url_for('index'))
    return render_template('postar.html')

@app.route('/curtir/<id_post>')
def curtir(id_post):
    user = session.get('user')
    if not user: return jsonify({"erro": "login"}), 401
    for p in postagens:
        if p['id'] == id_post:
            if user not in p['likes']: p['likes'].append(user)
            else: p['likes'].remove(user)
            salvar_posts(postagens)
            return jsonify({"novo_total": len(p['likes'])})
    return jsonify({"erro": "404"}), 404

@app.route('/comentar/<id_post>', methods=['POST'])
def comentar(id_post):
    user_email = session.get('user')
    if not user_email: return jsonify({"erro": "login"}), 401
    dados = request.get_json()
    texto = dados.get('conteudo', '').strip()
    parent_id = dados.get('parent_id')
    nome_usuario = usuarios.get(user_email, {}).get('nome', 'Usuário')

    if not texto: return jsonify({"erro": "vazio"}), 400

    novo_coment = {'id': str(uuid.uuid4()), 'autor': nome_usuario, 'texto': texto, 'respostas': []}
    for p in postagens:
        if p['id'] == id_post:
            if not parent_id:
                p['comentarios'].append(novo_coment)
            else:
                for c in p['comentarios']:
                    if c['id'] == parent_id:
                        novo_coment['texto'] = f"@{c['autor']} {texto}"
                        c['respostas'].append(novo_coment)
            salvar_posts(postagens) # Salva comentário no arquivo
            return jsonify({"status": "sucesso"})
    return jsonify({"erro": "404"}), 404

@app.route('/deletar/<id_post>')
def deletar(id_post):
    if session.get('user') not in ADMINS: return "Negado", 403
    global postagens
    postagens = [p for p in postagens if p['id'] != id_post]
    salvar_posts(postagens)
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
