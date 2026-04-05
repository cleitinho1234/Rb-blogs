from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import uuid

app = Flask(__name__)
app.secret_key = 'chave_super_secreta_do_cleitinho'

# --- FUNÇÃO PARA VÍDEOS GRANDES ---
# Define o limite máximo de upload para 100 Megabytes
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 

# Configuração de Uploads
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Lista de Administradores
ADMINS = ['robertdcg1999@gmail.com', 'cleitinhodacruzsilva4@gmail.com']

# Bancos de dados temporários
usuarios = {} # Estrutura: {email: {'senha': hash, 'nome': nome}}
postagens = [] 

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
        return "Erro no login! <a href='/login'>Tente novamente</a>"
    return render_template('login.html')

@app.route('/salvar_nome', methods=['POST'])
def salvar_nome():
    user_email = session.get('user')
    novo_nome = request.form.get('novo_nome', '').strip()
    
    if not user_email or not novo_nome: 
        return redirect(url_for('index'))
    
    for email, info in usuarios.items():
        if info.get('nome') == novo_nome and email != user_email:
            return "Este nome já está em uso por outro usuário! <a href='/'>Voltar</a>"
    
    usuarios[user_email]['nome'] = novo_nome
    return redirect(url_for('index'))

@app.route('/postar', methods=['GET', 'POST'])
def postar():
    if session.get('user') not in ADMINS: 
        return "Acesso negado", 403
        
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
        return redirect(url_for('index'))
    return render_template('postar.html')

@app.route('/curtir/<id_post>')
def curtir(id_post):
    user = session.get('user')
    if not user: 
        return jsonify({"erro": "login_obrigatorio"}), 401
        
    for p in postagens:
        if p['id'] == id_post:
            if user not in p['likes']:
                p['likes'].append(user)
            else:
                p['likes'].remove(user)
            return jsonify({"novo_total": len(p['likes'])})
            
    return jsonify({"erro": "postagem_nao_encontrada"}), 404

@app.route('/comentar/<id_post>', methods=['POST'])
def comentar(id_post):
    user_email = session.get('user')
    if not user_email: 
        return redirect(url_for('login'))
    
    texto = request.form.get('conteudo')
    parent_id = request.form.get('parent_id')
    nome_usuario = usuarios[user_email]['nome']
    
    novo_coment = {
        'id': str(uuid.uuid4()), 
        'autor': nome_usuario, 
        'texto': texto, 
        'respostas': []
    }

    for p in postagens:
        if p['id'] == id_post:
            if not parent_id:
                p['comentarios'].append(novo_coment)
            else:
                for c in p['comentarios']:
                    if c['id'] == parent_id:
                        novo_coment['texto'] = f"@{c['autor']} {texto}"
                        c['respostas'].append(novo_coment)
                        break
    return redirect(url_for('index'))

@app.route('/deletar/<id_post>')
def deletar(id_post):
    if session.get('user') not in ADMINS: 
        return "Negado", 403
        
    global postagens
    postagens = [p for p in postagens if p['id'] != id_post]
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
