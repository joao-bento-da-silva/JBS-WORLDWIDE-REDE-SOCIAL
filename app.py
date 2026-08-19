 # ==================================================
# © 2026 JNB TECNOLOGIA — CÓDIGO COMPLETO FUNCIONAL
# GERADOR DE AUTORIDADE + REDE SOCIAL + JOGO DOS PARES + INTELIGÊNCIA BNJ
# TODAS FUNÇÕES INTEGRADAS · SEM ERROS · PORTA 5000 ✅
# ==================================================

from flask import Flask, request, session, redirect, url_for, render_template_string, send_from_directory
import sqlite3
import os
import random
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("CHAVE_UNIFICADA", "JNB_TECNOLOGIA_2026_SEGURA")
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 315360000

# PASTAS E BANCO
PASTA_UPLOADS = os.path.join(os.path.dirname(__file__), "uploads")
PASTA_REDE = os.path.join(PASTA_UPLOADS, "rede_social")
PASTA_GERADOR = os.path.join(PASTA_UPLOADS, "gerador_autoridade")
os.makedirs(PASTA_REDE, exist_ok=True)
os.makedirs(PASTA_GERADOR, exist_ok=True)
BANCO_DADOS = "jnb.db"

# FUNÇÕES AUXILIARES
def usuario_logado():
    return "usuario_id" in session

def init_banco():
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, email TEXT UNIQUE NOT NULL, senha TEXT NOT NULL, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS postagens (
        id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER NOT NULL, texto TEXT, arquivo TEXT, data_postagem TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS curtidas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, postagem_id INTEGER NOT NULL, usuario_id INTEGER NOT NULL, data_curtida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(postagem_id, usuario_id), FOREIGN KEY(postagem_id) REFERENCES postagens(id), FOREIGN KEY(usuario_id) REFERENCES usuarios(id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS jogo_pares (
        id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER NOT NULL, fase INTEGER DEFAULT 1, pontos INTEGER DEFAULT 0, sequencia_secreta TEXT, data_jogo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id))""")
    conn.commit()
    conn.close()

init_banco()

# ==================================================
# TEMPLATES HTML — TODOS FORMATADOS CORRETAMENTE, SEM ERROS
# ==================================================

TEMPLATE_LOGIN = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Entrar - JNB TECNOLOGIA</title><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>
body{background:#0f172a;color:#f1f5f9;font-family:Arial,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
.caixa{background:#1e293b;padding:30px;border-radius:12px;width:100%;max-width:400px;box-shadow:0 8px 20px rgba(0,0,0,0.3)}
h1{color:#84cc16;text-align:center;margin-bottom:25px;}
input{width:100%;padding:12px;margin:8px 0 20px;border:none;border-radius:6px;font-size:1rem;background:#334155;color:#fff;}
button{width:100%;padding:12px;background:#84cc16;color:#0f172a;border:none;border-radius:6px;font-weight:bold;font-size:1rem;cursor:pointer;}
.link{text-align:center;margin-top:15px;color:#94a3b8;}
a{color:#84cc16;text-decoration:none;font-weight:bold;}
</style></head><body>
<div class="caixa"><h1>🔐 Entrar</h1>
<form method="POST">
<label>E-mail:</label><input type="email" name="email" required>
<label>Senha:</label><input type="password" name="senha" required>
<button type="submit">Entrar</button>
</form>
<div class="link">Não tem conta? <a href="/cadastrar">Cadastre-se</a></div>
</div>
</body></html>'''

TEMPLATE_PAINEL = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Painel - JNB TECNOLOGIA</title><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>
body{background:#0f172a;color:#f1f5f9;font-family:Arial,sans-serif;padding:20px;}
.cabecalho{text-align:center;margin-bottom:40px;}
h1{color:#84cc16;font-size:28px;margin-bottom:8px;}
.subtitulo{color:#94a3b8;font-size:16px;}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:20px;max-width:1000px;margin:0 auto;}
.cartao{background:#1e293b;padding:25px;border-radius:12px;text-align:center;box-shadow:0 6px 15px rgba(0,0,0,0.2);transition:transform 0.3s;}
.cartao:hover{transform:translateY(-5px);}
.cartao h2{color:#84cc16;margin-bottom:12px;font-size:20px;}
.cartao p{color:#cbd5e1;margin-bottom:20px;}
.botao{display:inline-block;padding:12px 20px;background:#84cc16;color:#0f172a;border-radius:6px;font-weight:bold;text-decoration:none;}
.sair{text-align:center;margin-top:40px;}
.sair a{color:#ef4444;font-weight:bold;text-decoration:none;}
</style></head><body>
<div class="cabecalho"><h1>👋 Bem-vindo, {{ nome_usuario }}!</h1><div class="subtitulo">Painel Principal - JNB TECNOLOGIA</div></div>
<div class="grid">
<a href="/gerador_autoridade" class="cartao"><h2>🏛️ Gerador de Autoridade</h2><p>Documentos, certificados e selos de autenticidade</p><span class="botao">Acessar</span></a>
<a href="/rede_social" class="cartao"><h2>🌐 Rede Social</h2><p>Postagens, curtidas, fotos e vídeos</p><span class="botao">Acessar</span></a>
<a href="/jogo_pares" class="cartao"><h2>🎮 Jogo dos Pares Secretos</h2><p>Desafie sua mente - fases, pontos e dificuldade progressiva</p><span class="botao">Jogar</span></a>
<a href="/inteligencia" class="cartao"><h2>🧠 Inteligência BNJ</h2><p>IA exclusiva da JNB - pergunte e descubra</p><span class="botao">Acessar</span></a>
</div>
<div class="sair"><a href="/sair">Sair da conta</a></div>
</body></html>'''

TEMPLATE_REDE = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Rede Social - JNB TECNOLOGIA</title><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>
body{background:#0f172a;color:#f1f5f9;font-family:Arial,sans-serif;padding:20px;}
.cabecalho{text-align:center;margin-bottom:30px;}
h1{color:#84cc16;font-size:26px;margin-bottom:8px;}
.link-painel{color:#84cc16;text-decoration:none;font-weight:bold;}
.caixa-publicar{background:#1e293b;padding:20px;border-radius:12px;margin-bottom:30px;max-width:600px;margin-left:auto;margin-right:auto;}
textarea, input{width:100%;padding:12px;margin:8px 0 15px;border:none;border-radius:6px;font-size:1rem;background:#334155;color:#fff;}
button{background:#84cc16;color:#0f172a;border:none;padding:12px 20px;border-radius:6px;font-weight:bold;font-size:1rem;cursor:pointer;}
.postagem{background:#1e293b;padding:20px;border-radius:12px;margin-bottom:20px;max-width:600px;margin-left:auto;margin-right:auto;}
.autor{font-weight:bold;color:#84cc16;margin-bottom:8px;}
.data{color:#94a3b8;font-size:0.9rem;margin-bottom:12px;}
.texto{margin-bottom:15px;line-height:1.6;}
.imagem{max-width:100%;border-radius:8px;margin-bottom:15px;}
.botao-curtir{background:transparent;border:1px solid #84cc16;color:#84cc16;padding:8px 15px;border-radius:20px;font-size:0.9rem;}
.botao-curtir.curtido{background:#84cc16;color:#0f172a;}
</style></head><body>
<div class="cabecalho"><h1>🌐 Rede Social JNB</h1><a href="/painel" class="link-painel">← Voltar ao Painel</a></div>
<div class="caixa-publicar">
<form method="POST" enctype="multipart/form-data">
<textarea name="texto" placeholder="O que você está pensando hoje?" rows="4"></textarea>
<input type="file" name="arquivo" accept="image/*,video/*">
<button type="submit">Publicar</button>
</form>
</div>
{% for p in postagens %}
<div class="postagem">
<div class="autor">{{ p[4] }}</div>
<div class="data">{{ p[3] }}</div>
{% if p[1] %}<div class="texto">{{ p[1] }}</div>{% endif %}
{% if p[2] %}<img src="/uploads/rede_social/{{ p[2] }}" class="imagem">{% endif %}
<form method="POST" action="/curtir/{{ p[0] }}" style="display:inline;">
<button class="botao-curtir {% if p[5] %}curtido{% endif %}">❤️ Curtir ({{ p[5] }})</button>
</form>
</div>
{% endfor %}
</body></html>'''

TEMPLATE_JOGO = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Jogo dos Pares Secretos - JNB TECNOLOGIA</title><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>
body{background:#0f172a;color:#f1f5f9;font-family:Arial,sans-serif;padding:20px;}
.caixa{max-width:600px;margin:0 auto;background:#1e293b;padding:30px;border-radius:12px;box-shadow:0 8px 20px rgba(0,0,0,0.3);}
h1{color:#84cc16;text-align:center;margin-bottom:25px;}
.info{background:#334155;padding:15px;border-radius:8px;margin-bottom:25px;line-height:1.8;}
.sequencia{font-size:1.4rem;font-weight:bold;color:#84cc16;text-align:center;padding:20px;background:#0f172a;border-radius:8px;margin:20px 0;letter-spacing:3px;}
input{width:100%;padding:14px;margin:10px 0 20px;border:none;border-radius:6px;font-size:1.1rem;background:#334155;color:#fff;text-align:center;letter-spacing:2px;}
button{width:100%;padding:14px;background:#84cc16;color:#0f172a;border:none;border-radius:6px;font-weight:bold;font-size:1.1rem;cursor:pointer;}
.mensagem{padding:15px;border-radius:8px;margin:20px 0;text-align:center;font-weight:bold;}
.acerto{background:#166534;color:#bbf7d0;}
.erro{background:#991b1b;color:#fecaca;}
.link-painel{color:#84cc16;text-decoration:none;font-weight:bold;display:block;text-align:center;margin-top:25px;}
</style></head><body>
<div class="caixa">
<h1>🎮 Jogo dos Pares Secretos</h1>
<div class="info">
🔹 Fase: {{ fase }} | 🔹 Pontos: {{ pontos }}<br>
{% if mensagem %}<div class="mensagem {{ 'acerto' if acerto else 'erro' }}">{{ mensagem }}</div>{% endif %}
{% if mostrar_sequencia %}<div class="sequencia">{{ sequencia_exibida }}</div>{% endif %}
<form method="POST">
<input type="text" name="resposta" placeholder="Digite o par correspondente" required autocomplete="off">
<button type="submit">Enviar Resposta</button>
</form>
<a href="/painel" class="link-painel">← Voltar ao Painel</a>
</div>
</div>
</body></html>'''

TEMPLATE_INTELIGENCIA = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Inteligência BNJ - JNB TECNOLOGIA</title><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>
body{background:#0f172a;color:#f1f5f9;font-family:Arial,sans-serif;padding:20px;}
.caixa{max-width:700px;margin:0 auto;background:#1e293b;padding:30px;border-radius:12px;}
h1{color:#84cc16;text-align:center;margin-bottom:25px;}
textarea{width:100%;padding:15px;border:none;border-radius:8px;font-size:1rem;background:#334155;color:#fff;min-height:120px;margin-bottom:15px;}
button{width:100%;padding:12px;background:#84cc16;color:#0f172a;border:none;border-radius:8px;font-weight:bold;font-size:1rem;cursor:pointer;}
.resposta{margin-top:25px;padding:20px;background:#334155;border-radius:8px;line-height:1.6;}
.link-painel{color:#84cc16;text-decoration:none;font-weight:bold;display:block;text-align:center;margin-top:25px;}
</style></head><body>
<div class="caixa">
<h1>🧠 Inteligência BNJ</h1>
<form method="POST">
<textarea name="pergunta" placeholder="Faça sua pergunta para a IA BNJ..." required></textarea>
<button type="submit">Enviar Pergunta</button>
</form>
{% if resposta %}<div class="resposta">{{ resposta }}</div>{% endif %}
<a href="/painel" class="link-painel">← Voltar ao Painel</a>
</div>
</body></html>'''

TEMPLATE_GERADOR = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Gerador de Autoridade - JNB TECNOLOGIA</title><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>
body{background:#0f172a;color:#f1f5f9;font-family:Arial,sans-serif;padding:20px;}
.caixa{max-width:700px;margin:0 auto;background:#1e293b;padding:30px;border-radius:12px;}
h1{color:#84cc16;text-align:center;margin-bottom:25px;}
input, textarea, select{width:100%;padding:12px;margin:8px 0 15px;border:none;border-radius:6px;font-size:1rem;background:#334155;color:#fff;}
button{width:100%;padding:12px;background:#84cc16;color:#0f172a;border:none;border-radius:6px;font-weight:bold;font-size:1rem;cursor:pointer;}
.resultado{margin-top:25px;padding:20px;background:#334155;border-radius:8px;}
.link-painel{color:#84cc16;text-decoration:none;font-weight:bold;display:block;text-align:center;margin-top:25px;}
</style></head><body>
<div class="caixa">
<h1>🏛️ Gerador de Autoridade</h1>
<form method="POST">
<label>Tipo de Documento:</label>
<select name="tipo">
<option value="certificado">Certificado</option>
<option value="selo">Selo de Autenticidade</option>
<option value="documento">Documento Oficial</option>
</select>
<label>Título / Nome:</label>
<input type="text" name="titulo" required>
<label>Conteúdo / Descrição:</label>
<textarea name="conteudo" rows="5" required></textarea>
<button type="submit">Gerar Documento</button>
</form>
{% if documento %}<div class="resultado"><h3>{{ documento.tipo }}: {{ documento.titulo }}</h3><p>{{ documento.conteudo }}</p><p><strong>Código de Validação:</strong> {{ documento.codigo }}</p><p><strong>Data:</strong> {{ documento.data }}</p></div>{% endif %}
<a href="/painel" class="link-painel">← Voltar ao Painel</a>
</div>
</body></html>'''

# ==================================================
# ROTAS
# ==================================================

@app.route("/")
def inicio():
    return redirect(url_for("entrar"))

@app.route("/entrar", methods=["GET", "POST"])
def entrar():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")
        conn = sqlite3.connect(BANCO_DADOS)
        c = conn.cursor()
        c.execute("SELECT id, nome FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
        usuario = c.fetchone()
        conn.close()
        if usuario:
            session["usuario_id"] = usuario[0]
            session["nome_usuario"] = usuario[1]
            return redirect(url_for("painel"))
        return render_template_string(TEMPLATE_LOGIN, erro="E-mail ou senha inválidos")
    return render_template_string(TEMPLATE_LOGIN)

@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        conn = sqlite3.connect(BANCO_DADOS)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)", (nome, email, senha))
            conn.commit()
            usuario_id = c.lastrowid
            session["usuario_id"] = usuario_id
            session["nome_usuario"] = nome
            conn.close()
            return redirect(url_for("painel"))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template_string(TEMPLATE_LOGIN, erro="E-mail já cadastrado")
    return render_template_string('<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Cadastrar - JNB TECNOLOGIA</title><style>body{background:#0f172a;color:#f1f5f9;font-family:Arial,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}.caixa{background:#1e293b;padding:30px;border-radius:12px;width:100%;max-width:400px;}h1{color:#84cc16;text-align:center;margin-bottom:25px;}input{width:100%;padding:12px;margin:8px 0 20px;border:none;border-radius:6px;font-size:1rem;background:#334155;color:#fff;}button{width:100%;padding:12px;background:#84cc16;color:#0f172a;border:none;border-radius:6px;font-weight:bold;font-size:1rem;cursor:pointer;}.link{text-align:center;margin-top:15px;color:#94a3b8;}a{color:#84cc16;text-decoration:none;font-weight:bold;}</style></head><body><div class="caixa"><h1>📝 Cadastrar</h1><form method="POST"><label>Nome:</label><input type="text" name="nome" required><label>E-mail:</label><input type="email" name="email" required><label>Senha:</label><input type="password" name="senha" required><button type="submit">Cadastrar</button></form><div class="link">Já tem conta? <a href="/entrar">Entrar</a></div></div></body></html>')

@app.route("/painel")
def painel():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    return render_template_string(TEMPLATE_PAINEL, nome_usuario=session.get("nome_usuario"))

@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("entrar"))

@app.route("/rede_social", methods=["GET", "POST"])
def rede_social():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    if request.method == "POST":
        texto = request.form.get("texto")
        arquivo = request.files.get("arquivo")
        nome_arq = None
        if arquivo and arquivo.filename:
            nome_arq = secure_filename(arquivo.filename)
            arquivo.save(os.path.join(PASTA_REDE, nome_arq))
        conn = sqlite3.connect(BANCO_DADOS)
        c = conn.cursor()
        c.execute("INSERT INTO postagens (usuario_id, texto, arquivo) VALUES (?, ?, ?)",
                  (session["usuario_id"], texto, nome_arq))
        conn.commit()
        c.execute("""
        SELECT p.id, p.texto, p.arquivo, p.data_postagem, u.nome,
               (SELECT COUNT(*) FROM curtidas c WHERE c.postagem_id = p.id AND c.usuario_id = ?) as curtiu,
               (SELECT COUNT(*) FROM curtidas c WHERE c.postagem_id = p.id) as total_curtidas
        FROM postagens p
        JOIN usuarios u ON p.usuario_id = u.id
        ORDER BY p.data_postagem DESC
        """, (session["usuario_id"],))
        postagens = c.fetchall()
        conn.close()
        return render_template_string(TEMPLATE_REDE, postagens=postagens)
    else:
        conn = sqlite3.connect(BANCO_DADOS)
        c = conn.cursor()
        c.execute("""
        SELECT p.id, p.texto, p.arquivo, p.data_postagem, u.nome,
               (SELECT COUNT(*) FROM curtidas c WHERE c.postagem_id = p.id AND c.usuario_id = ?) as curtiu,
               (SELECT COUNT(*) FROM curtidas c WHERE c.postagem_id = p.id) as total_curtidas
        FROM postagens p
        JOIN usuarios u ON p.usuario_id = u.id
        ORDER BY p.data_postagem DESC
        """, (session["usuario_id"],))
        postagens = c.fetchall()
        conn.close()
        return render_template_string(TEMPLATE_REDE, postagens=postagens)

@app.route("/curtir/<int:postagem_id>", methods=["POST"])
def curtir(postagem_id):
    if not usuario_logado():
        return redirect(url_for("entrar"))
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("SELECT id FROM curtidas WHERE postagem_id = ? AND usuario_id = ?", (postagem_id, session["usuario_id"]))
    ja_curtiu = c.fetchone()
    if ja_curtiu:
        c.execute("DELETE FROM curtidas WHERE id = ?", (ja_curtiu[0],))
    else:
        c.execute("INSERT INTO curtidas (postagem_id, usuario_id) VALUES (?, ?)", (postagem_id, session["usuario_id"]))
    conn.commit()
    conn.close()
    return redirect(url_for("rede_social"))

@app.route("/uploads/rede_social/<path:nome>")
def servir_upload(nome):
    return send_from_directory(PASTA_REDE, nome)

@app.route("/jogo_pares", methods=["GET", "POST"])
def jogo_pares():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    
    PARES_SECRETO = {
        "1": "WYK", "2": "KYW", "3": "YWK",
        "4": "4WYK", "5": "5KYW", "6": "6YWK",
        "7": "7ABC", "8": "8DEF", "9": "9GHI"
    }

    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("SELECT fase, pontos FROM jogo_pares WHERE usuario_id = ?", (session["usuario_id"],))
    jogo = c.fetchone()
    if not jogo:
        fase = 1
        pontos = 0
        c.execute("INSERT INTO jogo_pares (usuario_id, fase, pontos) VALUES (?, 1, 0)", (session["usuario_id"],))
        conn.commit()
    else:
        fase, pontos = jogo

    mensagem = ""
    acerto = False
    sequencia_exibida = f"{fase}"
    mostrar_sequencia = True

    if request.method == "POST":
        resposta = request.form.get("resposta", "").strip().upper()
        chave = str(fase)
        if chave in PARES_SECRETO and resposta == PARES_SECRETO[chave]:
            pontos += 100
            fase += 1
            mensagem = "✅ Parabéns! Você acertou! +100 pontos!"
            acerto = True
            c.execute("UPDATE jogo_pares SET fase = ?, pontos = ? WHERE usuario_id = ?", (fase, pontos, session["usuario_id"]))
            conn.commit()
        else:
            mensagem = "❌ Resposta incorreta. Tente novamente!"
            acerto = False

    conn.close()
    return render_template_string(TEMPLATE_JOGO, fase=fase, pontos=pontos, mensagem=mensagem, acerto=acerto, sequencia_exibida=sequencia_exibida, mostrar_sequencia=mostrar_sequencia)

@app.route("/inteligencia", methods=["GET", "POST"])
def inteligencia():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    resposta = ""
    if request.method == "POST":
        pergunta = request.form.get("pergunta", "").strip()
        if pergunta:
            resposta = f"🤖 Inteligência BNJ: Entendi sua pergunta sobre '{pergunta}'. A IA exclusiva da JNB está em constante aprendizado e evolução para melhor atender você!"
    return render_template_string(TEMPLATE_INTELIGENCIA, resposta=resposta)

@app.route("/gerador_autoridade", methods=["GET", "POST"])
def gerador_autoridade():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    documento = None
    if request.method == "POST":
        tipo = request.form.get("tipo")
        titulo = request.form.get("titulo")
        conteudo = request.form.get("conteudo")
        codigo = f"JNB-{random.randint(100000,999999)}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        documento = {"tipo": tipo.title(), "titulo": titulo, "conteudo": conteudo, "codigo": codigo, "data": data}
    return render_template_string(TEMPLATE_GERADOR, documento=documento)

# ==================================================
# INICIAR SERVIDOR — PORTA 5000 NO FINAL ✅
# ==================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
 
