from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Lista para guardar as postagens
postagens = []

@app.route('/')
def index():
    return render_template('index.html', posts=postagens)

@app.route('/postar', methods=['GET', 'POST'])
def postar():
    if request.method == 'POST':
        descricao = request.form.get('descricao')
        video = request.files.get('video')
        
        if video:
            video_filename = video.filename
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
            video.save(video_path)
            
            # Usamos o nome do arquivo como um "ID" para deletar depois
            nova_postagem = {
                'id': video_filename, 
                'video': video_filename,
                'desc': descricao,
                'data': "Postado agora"
            }
            postagens.insert(0, nova_postagem)
            return redirect(url_for('index'))
            
    return render_template('postar.html')

@app.route('/deletar/<id_video>')
def deletar(id_video):
    # 1. Remove da lista visual
    global postagens
    postagens = [p for p in postagens if p['id'] != id_video]
    
    # 2. Tenta apagar o arquivo real da pasta para não encher o servidor
    caminho_arquivo = os.path.join(app.config['UPLOAD_FOLDER'], id_video)
    if os.path.exists(caminho_arquivo):
        os.remove(caminho_arquivo)
        
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
