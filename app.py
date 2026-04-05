from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'chave_super_secreta_do_cleitinho'

UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ADMINS = ['robertdcg1999@gmail.com', 'cleitinhodacruzsilva4@gmail.com']

# Bancos de dados temporários
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
        email = request.form.get('email').strip().lower() # Limpa espaços e deixa minúsculo
        senha = request.form.get('senha')
        if email and email not in usuarios:
            usuarios[email] = generate_password_hash(senha)
            session['user'] = email
            return redirect(url_for('index'))
        else:
            return "Este e-mail já está cadastrado! <a href='/login'>Fazer Login</a>"
    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_digitado = request.form.get('email').strip().lower()
        senha_digitada = request.form.get('senha')
        
        # VERIFICAÇÃO RIGOROSA:
        # 1. O e-mail existe no "banco"? 
        # 2. A senha combina com o e-mail?
        if email_digitado in usuarios and check_password_hash(usuarios[email_digitado], senha_digitada):
            session['user'] = email_digitado
            return redirect(url_for('index'))
        else:
            return "E-mail ou senha incorretos, ou usuário não existe! <a href='/cadastro'>Crie uma conta primeiro</a>"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear() # Limpa tudo da memória do navegador
    return redirect(url_for('index'))

@app.route('/postar', methods=['GET', 'POST'])
def postar():
    if session.get('user') not in ADMINS:
        return "Acesso negado!", 403
    if request.method == 'POST':
        video = request.files.get('video')
        desc = request.form.get('descricao')
        if video:
            filename = video.filename
            video.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            postagens.insert(0, {
                'id': filename, 
                'video': filename, 
                'desc': desc, 
                'likes': [], 
                'comentarios': []
            })
            return redirect(url_for('index'))
    return render_template('postar.html')

@app.route('/curtir/<id_video>')
def curtir(id_video):
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    for p in postagens:
        if p['id'] == id_video:
            if user not in p['likes']:
                p['likes'].append(user)
            else:
                p['likes'].remove(user)
    return redirect(url_for('index'))

@app.route('/comentar/<id_video>', methods=['POST'])
def comentar(id_video):
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    texto = request.form.get('conteudo')
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
    postagens = [p for p in postagens if p['id'] != id_video]
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
