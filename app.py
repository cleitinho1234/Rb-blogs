from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# Configura a pasta de uploads dentro de static
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Lista para guardar as postagens temporariamente
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
            
            # Adiciona a nova postagem no topo da lista
            nova_postagem = {
                'video': video_filename,
                'desc': descricao,
                'data': "Postado agora"
            }
            postagens.insert(0, nova_postagem)
            return redirect(url_for('index'))
            
    return render_template('postar.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
