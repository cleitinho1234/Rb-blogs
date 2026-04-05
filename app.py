from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
# Essa chave protege as sessões de login do site
app.secret_key = 'chave_super_secreta_do_cleitinho'

# Configuração da pasta onde os vídeos ficam salvos
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# E-mails que têm permissão de Administrador (Postar e Deletar)
ADMINS = ['robertdcg1999@gmail.com', 'cleitinhodacruzsilva4@gmail.com']

# Bancos de dados temporários (Lembre-se: apagam se o site reiniciar no Render)
usuarios = {} 
postagens = [] 

@app.route('/')
def index():
    user_email = session.get('user')
    e_admin = user_email in ADMINS
    return render_template('index.html', posts=postagens, user=user_email, e_admin=e_admin)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        if email and email not in usuarios:
            usuarios[email] = generate_password_hash(senha)
            session['user'] = email
            return redirect(url_for('index'))
    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        if email in usuarios and check_password_hash(usuarios[email], senha):
            session['user'] = email
            return redirect(url_for('index'))
        else:
            return "E-mail ou senha incorretos! <a href='/login'>Tentar novamente</a>"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/postar', methods=['GET', 'POST'])
def postar():
    if session.get('user') not in ADMINS:
        return "Você não tem permissão para postar!", 403
    
    if request.method == 'POST':
        video = request.files.get('video')
        desc = request.form.get('descricao')
        if video:
            filename = video.filename
            video.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Cria o post com a estrutura completa para evitar erro no HTML
            postagens.insert(0, {
                'id': filename, 
                'video': filename, 
                'desc': desc, 
                'likes': 0, 
                'comentarios': [],
                'data': 'Postado agora'
            })
            return redirect(url_for('index'))
    return render_template('postar.html')

@app.route('/curtir/<id_video>')
def curtir(id_video):
    if not session.get('user'):
        return redirect(url_for('login'))
    for p in postagens:
        if p['id'] == id_video:
            p['likes'] += 1
    return redirect(url_for('index'))

@app.route('/comentar/<id_video>', methods=['POST'])
def comentar(id_video):
    if not session.get('user'):
        return redirect(url_for('login'))
    texto = request.form.get('conteudo')
    user = session.get('user')
    if texto:
        for p in postagens:
            if p['id'] == id_video:
                p['comentarios'].append({'autor': user, 'texto': texto})
    return redirect(url_for('index'))

@app.route('/deletar/<id_video>')
def deletar(id_video):
    if session.get('user') not in ADMINS:
        return "Acesso negado!", 403
    global postagens
    # Remove da lista
    postagens = [p for p in postagens if p['id'] != id_video]
    
    # Apaga o arquivo físico
    caminho = os.path.join(app.config['UPLOAD_FOLDER'], id_video)
    if os.path.exists(caminho):
        os.remove(caminho)
        
    return redirect(url_for('index'))

if __name__ == "__main__":
    # Roda o site
    app.run(host='0.0.0.0', port=5000)
