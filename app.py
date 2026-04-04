from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# Pasta para salvar os vídeos que seu primo enviar
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Lista simples para guardar as postagens (na memória por enquanto)
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
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
            video.save(video_path)
            # Salva o caminho do vídeo e a descrição
            postagens.insert(0, {'video': video.filename, 'desc': descricao})
            return redirect(url_for('index'))
            
    return render_template('postar.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
