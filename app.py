from flask import Flask, render_template_string, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import uuid

app = Flask(__name__)

# CONFIGURAÇÕES
app.config['SECRET_KEY'] = 'REDE_FUNCIONA_JBS_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco_rede.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'arquivos_rede'
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
db = SQLAlchemy(app)

# MODELOS DO BANCO DE DADOS
class Usuario(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    data = db.Column(db.DateTime, default=datetime.now)

class Postagem(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    id_usuario = db.Column(db.String(36), nullable=False)
    texto = db.Column(db.Text, default='')
    midia = db.Column(db.String(200))
    data = db.Column(db.DateTime, default=datetime.now)
    curtidas = db.Column(db.Integer, default=0)

class Comentario(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    id_postagem = db.Column(db.String(36), nullable=False)
    id_usuario = db.Column(db.String(36), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    data = db.Column(db.DateTime, default=datetime.now)

class Curtida(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    id_postagem = db.Column(db.String(36), nullable=False)
    id_usuario = db.Column(db.String(36), nullable=False)

# TELAS HTML — EXATAMENTE COMO ESTAVAM
INICIO = """
<!DOCTYPE html>
<html>
<head>
    <title>Minha Rede</title>
    <meta charset="utf-8">
    <style>
        * { margin:0; padding:0; font-family:Arial; }
        body { background:linear-gradient(45deg, #1877f2, #34c759); min-height:100vh; color:white; text-align:center; padding-top:150px; }
        h1 { font-size:50px; margin-bottom:20px; }
        p { font-size:20px; margin-bottom:40px; }
        .b { padding:15px 40px; margin:10px; border-radius:8px; font-size:18px; font-weight:bold; text-decoration:none; display:inline-block; }
        .cad { background:white; color:#34c759; }
        .ent { background:#ffcc00; color:#111; }
    </style>
</head>
<body>
    <h1>📱 MINHA REDE SOCIAL</h1>
    <p>Cadastre, poste, curta e comente — tudo funcionando!</p>
    <a href="/cadastro" class="b cad">CRIAR CONTA</a>
    <a href="/login" class="b ent">ENTRAR</a>
</body>
</html>
"""

CADASTRO = """
<!DOCTYPE html>
<html>
<head>
    <title>Cadastro</title>
    <meta charset="utf-8">
    <style>
        * { margin:0; padding:0; font-family:Arial; }
        body { background:#f0f2f5; min-height:100vh; display:flex; align-items:center; justify-content:center; }
        .cx { background:white; padding:40px; border-radius:10px; width:400px; box-shadow:0 0 10px #0002; }
        h2 { text-align:center; color:#1877f2; margin-bottom:20px; }
        input { width:100%; padding:12px; margin:8px 0; border:1px solid #ddd; border-radius:6px; font-size:16px; }
        button { width:100%; padding:12px; background:#34c759; color:white; border:none; border-radius:6px; font-size:18px; font-weight:bold; margin-top:10px; cursor:pointer; }
        .lnk { text-align:center; margin-top:20px; }
    </style>
</head>
<body>
    <div class="cx">
        <h2>Criar Conta</h2>
        <form method="POST">
            <input type="text" name="nome" placeholder="Seu nome" required>
            <input type="email" name="email" placeholder="Seu e-mail" required>
            <input type="password" name="senha" placeholder="Sua senha" required>
            <button type="submit">CADASTRAR</button>
        </form>
        <div class="lnk">Já tem conta? <a href="/login">Entrar</a></div>
    </div>
</body>
</html>
"""

LOGIN = """
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <meta charset="utf-8">
    <style>
        * { margin:0; padding:0; font-family:Arial; }
        body { background:#f0f2f5; min-height:100vh; display:flex; align-items:center; justify-content:center; }
        .cx { background:white; padding:40px; border-radius:10px; width:400px; box-shadow:0 0 10px #0002; }
        h2 { text-align:center; color:#1877f2; margin-bottom:20px; }
        input { width:100%; padding:12px; margin:8px 0; border:1px solid #ddd; border-radius:6px; font-size:16px; }
        button { width:100%; padding:12px; background:#1877f2; color:white; border:none; border-radius:6px; font-size:18px; font-weight:bold; margin-top:10px; cursor:pointer; }
        .lnk { text-align:center; margin-top:20px; }
    </style>
</head>
<body>
    <div class="cx">
        <h2>Entrar</h2>
        <form method="POST">
            <input type="email" name="email" placeholder="Seu e-mail" required>
            <input type="password" name="senha" placeholder="Sua senha" required>
            <button type="submit">ENTRAR</button>
        </form>
        <div class="lnk">Não tem conta? <a href="/cadastro">Criar</a></div>
    </div>
</body>
</html>
"""

FEED = """
<!DOCTYPE html>
<html>
<head>
    <title>Feed</title>
    <meta charset="utf-8">
    <style>
        * { margin:0; padding:0; font-family:Arial; }
        .topo { background:#1877f2; color:white; padding:15px 30px; display:flex; justify-content:space-between; align-items:center; font-size:20px; font-weight:bold; }
        .topo a { color:white; margin-left:20px; font-weight:normal; text-decoration:none; }
        .corpo { max-width:650px; margin:20px auto; padding:0 15px; }
        .postar { background:white; padding:20px; border-radius:8px; margin-bottom:20px; box-shadow:0 2px 5px #0001; }
        textarea { width:100%; height:80px; border:1px solid #ddd; border-radius:6px; padding:10px; font-size:16px; margin-bottom:10px; }
        button { background:#1877f2; color:white; border:none; border-radius:6px; padding:8px 15px; font-size:15px; cursor:pointer; }
        .post { background:white; padding:20px; border-radius:8px; margin-bottom:15px; box-shadow:0 2px 5px #0001; }
        .nome { font-weight:bold; font-size:17px; margin-bottom:5px; }
        .data { color:#666; font-size:14px; margin-bottom:10px; }
        .acoes { margin:10px 0; padding:10px 0; border-top:1px solid #eee; border-bottom:1px solid #eee; }
        .coment { margin-top:10px; }
        .coment input { width:80%; padding:8px; border:1px solid #ddd; border-radius:15px; }
        .lista-coment { margin-top:10px; }
        .item-coment { background:#f5f5f5; padding:8px; border-radius:10px; margin-bottom:5px; font-size:15px; }
    </style>
</head>
<body>
    <div class="topo">
        <span>📱 MINHA REDE</span>
        <div>Olá, {{nome}}! <a href="/sair">Sair</a></div>
    </div>
    <div class="corpo">
        <div class="postar">
            <form method="POST" action="/fazer_post" enctype="multipart/form-data">
                <textarea name="texto" placeholder="No que está pensando?" required></textarea>
                <input type="file" name="arquivo" accept="image/*">
                <br><button type="submit">PUBLICAR</button>
            </form>
        </div>

        {% for p in posts %}
        <div class="post">
            <div class="nome">{{p.autor}}</div>
            <div class="data">{{p.data}}</div>
            {% if p.texto %}<p>{{p.texto}}</p>{% endif %}
            {% if p.midia %}<img src="/ver/{{p.midia}}" style="max-width:100%; border-radius:6px; margin:10px 0;">{% endif %}
            
            <div class="acoes">
                <form method="POST" action="/curtir/{{p.id}}" style="display:inline;">
                    <button type="submit">❤️ {{p.curtidas}}</button>
                </form>
            </div>

            <div class="coment">
                <form method="POST" action="/comentar/{{p.id}}">
                    <input type="text" name="texto" placeholder="Comente algo..." required>
                    <button type="submit">Enviar</button>
                </form>
                <div class="lista-coment">
                    {% for c in p.comentarios %}
                    <div class="item-coment"><strong>{{c.autor}}:</strong> {{c.texto}}</div>
                    {% endfor %}
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

# ROTAS — IGUAIS
@app.route('/')
def inicio():
    if 'user' in session:
        return redirect(url_for('feed'))
    return render_template_string(INICIO)

@app.route('/cadastro', methods=['GET','POST'])
def cad():
    if request.method == 'POST':
        if Usuario.query.filter_by(email=request.form['email']).first():
            return "<script>alert('Email já existe!');history.back()</script>"
        u = Usuario(nome=request.form['nome'], email=request.form['email'], senha=generate_password_hash(request.form['senha']))
        db.session.add(u)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template_string(CADASTRO)

@app.route('/login', methods=['GET','POST'])
def logar():
    if request.method == 'POST':
        u = Usuario.query.filter_by(email=request.form['email']).first()
        if not u or not check_password_hash(u.senha, request.form['senha']):
            return "<script>alert('Dados errados!');history.back()</script>"
        session['user'] = u.id
        return redirect(url_for('feed'))
    return render_template_string(LOGIN)

@app.route('/feed')
def feed():
    if 'user' not in session:
        return redirect(url_for('inicio'))
    eu = Usuario.query.get(session['user'])
    posts = Postagem.query.order_by(Postagem.data.desc()).all()
    lista = []
    for p in posts:
        au = Usuario.query.get(p.id_usuario)
        coms = Comentario.query.filter_by(id_postagem=p.id).all()
        lista_com = []
        for c in coms:
            lista_com.append({'autor': Usuario.query.get(c.id_usuario).nome, 'texto': c.texto})
        lista.append({
            'id': p.id, 'autor': au.nome, 'texto': p.texto, 'midia': p.midia,
            'data': p.data.strftime('%d/%m às %H:%M'), 'curtidas': p.curtidas, 'comentarios': lista_com
        })
    return render_template_string(FEED, nome=eu.nome, posts=lista)

@app.route('/fazer_post', methods=['POST'])
def fazer_post():
    if 'user' not in session:
        return redirect(url_for('inicio'))
    arq = request.files.get('arquivo')
    nome_arq = None
    if arq and arq.filename:
        nome_arq = secure_filename(f"{uuid.uuid4()}_{arq.filename}")
        arq.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_arq))
    db.session.add(Postagem(id_usuario=session['user'], texto=request.form['texto'], midia=nome_arq))
    db.session.commit()
    return redirect(url_for('feed'))

@app.route('/curtir/<idp>', methods=['POST'])
def curtir(idp):
    if 'user' not in session:
        return redirect(url_for('inicio'))
    post = Postagem.query.get(idp)
    ja = Curtida.query.filter_by(id_postagem=idp, id_usuario=session['user']).first()
    if ja:
        db.session.delete(ja)
        post.curtidas -= 1
    else:
        db.session.add(Curtida(id_postagem=idp, id_usuario=session['user']))
        post.curtidas += 1
    db.session.commit()
    return redirect(url_for('feed'))

@app.route('/comentar/<idp>', methods=['POST'])
def comentar(idp):
    if 'user' not in session:
        return redirect(url_for('inicio'))
    db.session.add(Comentario(id_postagem=idp, id_usuario=session['user'], texto=request.form['texto']))
    db.session.commit()
    return redirect(url_for('feed'))

@app.route('/ver/<arq>')
def ver(arq):
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], arq)

@app.route('/sair')
def sair():
    session.clear()
    return redirect(url_for('inicio'))

# CRIAR TABELAS NO BANCO
with app.app_context():
    db.create_all()

# RODAR NA PORTA 5000 — COMO PEDIU
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
 
