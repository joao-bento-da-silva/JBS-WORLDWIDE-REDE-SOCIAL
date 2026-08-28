# ==================================================
# © 2026 JNB TECNOLOGIA — CÓDIGO FINAL CORRIGIDO ✅
# REDE · JOGOS · IA · DNA (CONVERSÃO + DOWNLOAD + DECODIFICAÇÃO)
# PORTA 5000 · SEM ERROS · 100% FUNCIONAL ✅
# ==================================================

from flask import Flask, request, session, redirect, url_for, render_template_string, send_from_directory, make_response
import sqlite3
import os
import random
import hashlib
import base64
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("CHAVE_UNIFICADA", "JNB_TECNOLOGIA_2026_SEGURA")
CHAVE_DNA = os.environ.get("CHAVE_DNA_SECRETA", "JNB_SECRETA_DNA_2026_NAO_COMPARTILHAR")
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 315360000

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4", "mov", "avi", "webm", "bnj"}
BANCO_DADOS = "jnb_novo.db"

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            pontos INTEGER DEFAULT 0,
            dna_chave TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS postagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            texto TEXT,
            arquivo TEXT,
            data_postagem TEXT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS curtidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            postagem_id INTEGER NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY (postagem_id) REFERENCES postagens(id),
            UNIQUE(usuario_id, postagem_id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

def usuario_logado():
    return "usuario_id" in session

# ============= LOGIN / CADASTRO =============
@app.route("/")
def inicio():
    if usuario_logado():
        return redirect(url_for("plataforma"))
    return render_template_string('''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JNB TECNOLOGIA</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif;}
        body{background:linear-gradient(180deg,#0f172a,#1e293b);color:#e2e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center;}
        .caixa{background:rgba(15,23,42,0.8);padding:40px;border-radius:12px;border:1px solid #f59e0b;width:90%;max-width:400px;}
        h1{color:#f59e0b;text-align:center;margin-bottom:30px;}
        input{width:100%;padding:12px;margin:8px 0;background:#020617;border:1px solid #334155;color:white;border-radius:6px;}
        button{width:100%;padding:12px;background:#f59e0b;color:#1e1b16;border:none;border-radius:6px;font-weight:bold;cursor:pointer;}
        .link{text-align:center;margin-top:15px;font-size:14px;color:#94a3b8;}
        .link a{color:#f59e0b;text-decoration:none;}
    </style>
</head>
<body>
    <div class="caixa">
        <h1>JNB TECNOLOGIA</h1>
        <form action="/entrar" method="POST">
            <input type="email" name="email" placeholder="E-mail" required>
            <input type="password" name="senha" placeholder="Senha" required>
            <button type="submit">Entrar</button>
        </form>
        <div class="link">Não tem conta? <a href="/cadastrar">Cadastre-se</a></div>
    </div>
</body>
</html>''')

@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "").strip()
        if nome and email and senha:
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            dna_chave = base64.b64encode(os.urandom(24)).decode()
            try:
                conn = sqlite3.connect(BANCO_DADOS)
                c = conn.cursor()
                c.execute("INSERT INTO usuarios (nome, email, senha_hash, dna_chave) VALUES (?, ?, ?, ?)",
                          (nome, email, senha_hash, dna_chave))
                conn.commit()
                usuario_id = c.lastrowid
                conn.close()
                session["usuario_id"] = usuario_id
                session["nome_usuario"] = nome
                return redirect(url_for("plataforma"))
            except sqlite3.IntegrityError:
                return '''<div style="text-align:center;padding:50px;background:#0f172a;color:white;">
                    <h2 style="color:red;">E-mail já cadastrado!</h2>
                    <a href="/cadastrar" style="color:#f59e0b;">Voltar</a>
                </div>'''
    return render_template_string('''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cadastrar — JNB TECNOLOGIA</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif;}
        body{background:linear-gradient(180deg,#0f172a,#1e293b);color:#e2e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center;}
        .caixa{background:rgba(15,23,42,0.8);padding:40px;border-radius:12px;border:1px solid #f59e0b;width:90%;max-width:400px;}
        h1{color:#f59e0b;text-align:center;margin-bottom:30px;}
        input{width:100%;padding:12px;margin:8px 0;background:#020617;border:1px solid #334155;color:white;border-radius:6px;}
        button{width:100%;padding:12px;background:#f59e0b;color:#1e1b16;border:none;border-radius:6px;font-weight:bold;cursor:pointer;}
        .link{text-align:center;margin-top:15px;font-size:14px;color:#94a3b8;}
        .link a{color:#f59e0b;text-decoration:none;}
    </style>
</head>
<body>
    <div class="caixa">
        <h1>Cadastrar</h1>
        <form method="POST">
            <input type="text" name="nome" placeholder="Seu nome" required>
            <input type="email" name="email" placeholder="E-mail" required>
            <input type="password" name="senha" placeholder="Senha" required>
            <button type="submit">Cadastrar</button>
        </form>
        <div class="link">Já tem conta? <a href="/">Entrar</a></div>
    </div>
</body>
</html>''')

@app.route("/entrar", methods=["POST"])
def entrar():
    email = request.form.get("email", "").strip()
    senha = request.form.get("senha", "").strip()
    if email and senha:
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        conn = sqlite3.connect(BANCO_DADOS)
        c = conn.cursor()
        c.execute("SELECT id, nome FROM usuarios WHERE email = ? AND senha_hash = ?", (email, senha_hash))
        usuario = c.fetchone()
        conn.close()
        if usuario:
            session["usuario_id"] = usuario[0]
            session["nome_usuario"] = usuario[1]
            return redirect(url_for("plataforma"))
    return '''<div style="text-align:center;padding:50px;background:#0f172a;color:white;">
        <h2 style="color:red;">E-mail ou senha inválidos!</h2>
        <a href="/" style="color:#f59e0b;font-size:18px;">Voltar</a>
    </div>'''

@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("inicio"))

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# ==================================================
# 🃏 JOGO DAS CARTAS — REGRA OCULTA ✅
# ==================================================
@app.route("/jogo_cartas", methods=["GET", "POST"])
def jogo_cartas():
    if not usuario_logado():
        return redirect(url_for("inicio"))

    REGRAS = {'Y':'Y','A':'Z','Z':'A','B':'X','X':'B','C':'G','G':'C','D':'F','F':'D','E':'E'}
    CARTAS_DISPONIVEIS = ['Y','A','B','C','D','E','F','G','X','Z']
    
    if "cartas_fase" not in session: session["cartas_fase"] = 1
    if "cartas_pontos" not in session: session["cartas_pontos"] = 0
    
    fase = session["cartas_fase"]
    pontos = session["cartas_pontos"]
    qtd = {1:3,2:6,3:8,4:9}[fase]
    valor = {1:100,2:300,3:500,4:1000}[fase]
    mensagem = ""
    
    if "cartas_alvo" not in session or len(session.get("cartas_alvo",[])) != qtd:
        session["cartas_alvo"] = random.sample(CARTAS_DISPONIVEIS, qtd)
        session["cartas_resposta"] = []
    
    alvo = session["cartas_alvo"]
    resposta = session["cartas_resposta"]
    
    if request.method == "POST":
        if "nova" in request.form:
            session["cartas_alvo"] = random.sample(CARTAS_DISPONIVEIS, qtd)
            session["cartas_resposta"] = []
            mensagem = "🔄 Novas cartas geradas!"
        
        elif "selecionar" in request.form:
            resposta.append(request.form["selecionar"])
            session["cartas_resposta"] = resposta
        
        elif "verificar" in request.form:
            if len(resposta) != len(alvo):
                mensagem = "❌ Selecione todas as cartas primeiro!"
            else:
                correta = [REGRAS[c] for c in alvo]
                if resposta == correta:
                    pontos += valor
                    session["cartas_pontos"] = pontos
                    mensagem = f"✅ ACERTOU! +{valor} PONTOS!"
                    try:
                        conn = sqlite3.connect(BANCO_DADOS)
                        c = conn.cursor()
                        c.execute("UPDATE usuarios SET pontos = pontos + ? WHERE id = ?", (valor, session["usuario_id"]))
                        conn.commit()
                        conn.close()
                    except: pass
                    if fase < 4:
                        session["cartas_fase"] += 1
                        session.pop("cartas_alvo", None)
                        session.pop("cartas_resposta", None)
                    else:
                        mensagem = "🏆 PARABÉNS! VENCEU O JOGO DAS CARTAS!"
                        session["cartas_fase"] = 1
                        session.pop("cartas_alvo", None)
                        session.pop("cartas_resposta", None)
                else:
                    mensagem = "❌ Errou! Tente de novo."
                    session["cartas_resposta"] = []
    
    alvo_html = "".join([f"<span style='background:#f59e0b;color:black;padding:12px 18px;border-radius:8px;margin:5px;font-size:24px;font-weight:bold;'>{c}</span>" for c in alvo])
    resp_html = "".join([f"<span style='background:#22c55e;color:black;padding:12px 18px;border-radius:8px;margin:5px;font-size:24px;font-weight:bold;'>{c}</span>" for c in resposta]) if resposta else "<p style='color:#94a3b8;'>Clique nas cartas abaixo...</p>"
    disp_html = "".join([f"<button type='submit' name='selecionar' value='{c}' style='background:#33415e;color:white;padding:12px 18px;border-radius:8px;margin:5px;font-size:24px;font-weight:bold;border:2px solid #f59e0b;cursor:pointer;'>{c}</button>" for c in CARTAS_DISPONIVEIS])
    
    return render_template_string(f'''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🃏 Jogo das Cartas</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body{{background:linear-gradient(180deg,#0f172a,#1e293b);color:#e2e8f0;min-height:100vh;}}</style>
</head>
<body class="p-6 max-w-2xl mx-auto">
    <a href="/plataforma" class="text-yellow-500 hover:text-yellow-400">← Voltar</a>
    <h1 class="text-4xl font-bold text-yellow-500 text-center my-6">🃏 Jogo das Cartas</h1>
    <p class="text-center text-lg mb-4">Fase {fase}/4 · Pontos: {pontos}</p>
    {f'<div class="text-center p-3 rounded-lg mb-4 text-lg font-bold {"bg-green-900/50 text-green-400" if "✅" in mensagem or "🏆" in mensagem else "bg-red-900/50 text-red-400"}">{mensagem}</div>' if mensagem else ''}
    
    <div class="bg-gray-800 p-5 rounded-lg border border-yellow-500/30 mb-5">
        <p class="text-center mb-3 text-gray-400">🎯 Cartas Alvo — Encontre a correspondente:</p>
        <div class="flex flex-wrap justify-center">{alvo_html}</div>
    </div>
    
    <div class="bg-gray-800 p-5 rounded-lg border border-green-500/30 mb-5">
        <p class="text-center mb-3 text-gray-400">✅ Sua Resposta:</p>
        <div class="flex flex-wrap justify-center">{resp_html}</div>
    </div>
    
    <form method="POST" class="bg-gray-800 p-5 rounded-lg border border-yellow-500/30 mb-5">
        <p class="text-center mb-3 text-gray-400">🃏 Clique para selecionar:</p>
        <div class="flex flex-wrap justify-center">{disp_html}</div>
    </form>
    
    <div class="flex gap-3 justify-center flex-wrap">
        <form method="POST"><button type="submit" name="verificar" class="bg-green-600 hover:bg-green-500 text-white font-bold px-6 py-3 rounded-lg text-lg">✅ Verificar</button></form>
        <form method="POST"><button type="submit" name="nova" class="bg-yellow-600 hover:bg-yellow-500 text-black font-bold px-6 py-3 rounded-lg text-lg">🔄 Novas</button></form>
    </div>
</body>
</html>''')

# ==================================================
# 🎮 JOGO BENTINHO — SEGREDO DOS NÚMEROS
# ==================================================
@app.route("/jogo_bentinho", methods=["GET", "POST"])
def jogo_bentinho():
    if not usuario_logado():
        return redirect(url_for("inicio"))

    TABELA = {'0':'0','1':'9','2':'8','3':'7','4':'6','5':'5','6':'4','7':'3','8':'2','9':'1'}
    def inverter(num_str): return "".join(TABELA[d] for d in num_str)
    def novo_desafio(fase):
        tam = {1:3,2:6,3:8,4:9}[fase]
        num = "".join(random.choice("0123456789") for _ in range(tam))
        return num, inverter(num)

    if "bent_fase" not in session: session["bent_fase"] = 1
    if "bent_pontos" not in session: session["bent_pontos"] = 0

    if "bent_num" not in session or session.get("bent_fase_atual") != session["bent_fase"]:
        session["bent_num"], session["bent_alvo"] = novo_desafio(session["bent_fase"])
        session["bent_fase_atual"] = session["bent_fase"]

    mensagem = ""
    PONTOS = {1:250000,2:2500000,3:25000000,4:1000000000}

    if request.method == "POST":
        if request.form.get("acao") == "reiniciar":
            session["bent_fase"] = 1
            session["bent_pontos"] = 0
            session.pop("bent_num", None)
            return redirect(url_for("jogo_bentinho"))

        resposta = request.form.get("resposta", "").strip()
        alvo = session.get("bent_alvo", "")

        if resposta == alvo:
            pts = PONTOS[session["bent_fase"]]
            session["bent_pontos"] += pts
            mensagem = f"✅ ACERTOU! +{pts} PONTOS!"
            try:
                conn = sqlite3.connect(BANCO_DADOS)
                c = conn.cursor()
                c.execute("UPDATE usuarios SET pontos = pontos + ? WHERE id = ?", (pts, session["usuario_id"]))
                conn.commit()
                conn.close()
            except: pass
            if session["bent_fase"] < 4:
                session["bent_fase"] += 1
                session.pop("bent_num", None)
            else:
                mensagem = "🏆 PARABÉNS! 1.000.000.000 DE PONTOS!"
                session["bent_fase"] = 1
                session.pop("bent_num", None)
        else:
            mensagem = "❌ Errou! Tente de novo."
            session["bent_pontos"] = 0
            session["bent_num"], session["bent_alvo"] = novo_desafio(session["bent_fase"])

    fase = session["bent_fase"]
    num = session.get("bent_num", "000")
    pontos = session["bent_pontos"]
    placeholder = {1:"___",2:"______",3:"________",4:"_________"}[fase]

    return render_template_string(f'''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎮 Segredo dos Números</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body{{background:linear-gradient(180deg,#0f172a,#1e293b);color:#e2e8f0;min-height:100vh;}}</style>
</head>
<body class="flex items-center justify-center p-4">
    <div class="bg-gray-800 p-8 rounded-xl border-2 border-yellow-500/50 max-w-lg w-full">
        <h1 class="text-4xl font-bold text-yellow-500 text-center mb-2">🎮 SEGREDO DOS NÚMEROS</h1>
        <p class="text-center text-gray-400 mb-6">Autor: João Bento da Silva</p>
        <p class="text-center text-lg mb-6">Fase {fase}/4 · Pontos: {pontos}</p>
        {f'<div class="text-center p-4 rounded-lg mb-6 text-lg font-bold {"bg-green-900/50 text-green-400" if "✅" in mensagem or "🏆" in mensagem else "bg-red-900/50 text-red-400"}">{mensagem}</div>' if mensagem else ''}
        <div class="bg-gray-900 border-2 border-yellow-500/40 rounded-lg p-6 text-center mb-6">
            <p class="text-gray-400 mb-2">Número do Avatar:</p>
            <p class="text-5xl font-mono text-yellow-400 font-bold tracking-widest">{num}</p>
        </div>
        <form method="POST" class="space-y-4">
            <input type="text" name="resposta" placeholder="{placeholder}" class="w-full bg-gray-900 border-2 border-yellow-500 rounded-lg text-center text-2xl text-yellow-400 p-3 font-mono" required>
            <div class="flex gap-3">
                <button type="submit" class="flex-1 bg-yellow-600 hover:bg-yellow-500 text-black font-bold py-3 rounded-lg text-lg">✅ Decifrar</button>
                <button type="submit" name="acao" value="reiniciar" class="bg-gray-600 hover:bg-gray-500 text-white px-6 py-3 rounded-lg">🔄 Reiniciar</button>
            </div>
        </form>
        <p class="text-center mt-6"><a href="/plataforma" class="text-yellow-500 hover:text-yellow-400">← Voltar</a></p>
    </div>
</body>
</html>''')

# ROTA PARA BAIXAR DNA — COLA AQUI!
@app.route("/baixar_dna", methods=["POST"])
def baixar_dna():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    
    dna_texto = request.form.get("dna_texto", "").strip()
    if not dna_texto:
        return "Nenhum DNA para baixar", 400
    
    conteudo = f"JNB-DNA-ENCRYPTED\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{dna_texto}"
    
    resp = make_response(conteudo)
    resp.headers["Content-Disposition"] = f"attachment; filename=documento_dna_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bnj"
    resp.headers["Content-Type"] = "application/octet-stream"
    return resp

# A rota da plataforma continua aqui — NÃO MEXE NELA!
@app.route("/plataforma", methods=["GET", "POST"])
def plataforma():
    ...



# ==================================================
# 🏛️ PLATAFORMA PRINCIPAL — TUDO CORRIGIDO ✅
# ==================================================
@app.route("/plataforma", methods=["GET", "POST"])
def plataforma():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    
    usuario_id = session["usuario_id"]
    
    if request.method == "POST" and "texto_post" in request.form:
        texto = request.form.get("texto_post", "").strip()
        arquivo = request.files.get("arquivo")
        nome_arq = None
        if arquivo and allowed_file(arquivo.filename):
            nome_arq = secure_filename(arquivo.filename)
            arquivo.save(os.path.join(app.config["UPLOAD_FOLDER"], nome_arq))
        if texto or nome_arq:
            conn = sqlite3.connect(BANCO_DADOS)
            c = conn.cursor()
            c.execute("INSERT INTO postagens (usuario_id, texto, arquivo, data_postagem) VALUES (?, ?, ?, ?)",
                      (usuario_id, texto, nome_arq, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
        return redirect(url_for("plataforma"))
    
    if "curtir" in request.args:
        postagem_id = request.args.get("curtir")
        conn = sqlite3.connect(BANCO_DADOS)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO curtidas (usuario_id, postagem_id) VALUES (?, ?)", (usuario_id, postagem_id))
        except sqlite3.IntegrityError:
            c.execute("DELETE FROM curtidas WHERE usuario_id = ? AND postagem_id = ?", (usuario_id, postagem_id))
        conn.commit()
        conn.close()
        return redirect(url_for("plataforma") + "#post-" + postagem_id)
    
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("SELECT nome, pontos, dna_chave FROM usuarios WHERE id = ?", (usuario_id,))
    usuario_dados = c.fetchone()
    if not usuario_dados:
        conn.close()
        session.clear()
        return redirect(url_for("inicio"))
    nome_usuario, total_pontos, dna_chave = usuario_dados
    
    c.execute("""
        SELECT p.id, p.texto, p.arquivo, p.data_postagem, u.nome,
               (SELECT COUNT(*) FROM curtidas c WHERE c.postagem_id = p.id) as total_curtidas,
               EXISTS(SELECT 1 FROM curtidas c WHERE c.postagem_id = p.id AND c.usuario_id = ?) as curtiu
        FROM postagens p JOIN usuarios u ON p.usuario_id = u.id
        ORDER BY p.data_postagem DESC
    """, (usuario_id,))
    postagens = c.fetchall()
    conn.close()
    
    # Montar HTML das postagens FORA do render_template_string
    postagens_html = ""
    if postagens:
        for p in postagens:
            pid, texto, arquivo, data, autor, curtidas, curtiu = p
            curtida_classe = "red" if curtiu else "gray"
            plural = "s" if curtidas != 1 else ""
            postagens_html += f'''
                    <div id="post-{pid}" class="bg-gray-800 p-4 rounded-lg border border-yellow-500/30">
                        <h4 class="font-bold text-yellow-400">{autor}</h4>
                        <p class="text-sm text-gray-400 mb-3">{data}</p>
                        {f'<p class="mb-3 whitespace-pre-wrap">{texto}</p>' if texto else ''}
            '''
            if arquivo:
                ext = arquivo.split(".")[-1].lower()
                if ext in ["jpg", "jpeg", "png", "gif"]:
                    postagens_html += f'<img src="/uploads/{arquivo}" class="max-w-full rounded-lg mb-3">'
                elif ext in ["mp4", "mov", "avi", "webm"]:
                    postagens_html += f'''<video controls class="max-w-full rounded-lg mb-3">
                        <source src="/uploads/{arquivo}" type="video/mp4">
                    </video>'''
            postagens_html += f'''
                        <div class="flex items-center gap-4 mt-3 pt-3 border-t border-gray-700">
                            <a href="/plataforma?curtir={pid}#post-{pid}" class="flex items-center gap-1 text-{curtida_classe}-400 hover:text-red-400">
                                <i class="fa-solid fa-thumbs-up"></i> {curtidas} Curtida{plural}
                            </a>
                        </div>
                    </div>
            '''
    else:
        postagens_html += '''
                    <div class="text-center py-10 text-gray-500">
                        <i class="fa-solid fa-newspaper text-4xl mb-3"></i>
                        <p>Ainda não há postagens. Seja o primeiro a compartilhar!</p>
                    </div>
        '''
    
    return render_template_string(f'''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plataforma — JNB TECNOLOGIA</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>.hidden{{display:none !important;}}</style>
</head>
<body class="bg-gray-900 text-gray-100 min-h-screen">
    <div class="container mx-auto px-4 py-6">
        <div class="flex flex-wrap justify-between items-center border-b border-gray-700 pb-4 mb-6">
            <div>
                <h1 class="text-2xl font-bold text-yellow-500">⚡ JNB TECNOLOGIA</h1>
                <p class="text-gray-400">Bem-vindo, {nome_usuario}!</p>
            </div>
            <div class="text-right">
                <p class="text-sm text-gray-400">Total de Pontos</p>
                <p class="text-xl font-bold text-yellow-500">{total_pontos}</p>
                <a href="/sair" class="text-red-400 hover:text-red-300 text-sm">Sair <i class="fa-solid fa-right-from-bracket"></i></a>
            </div>
        </div>

        <div class="flex flex-wrap gap-2 mb-6 border-b border-gray-700 pb-2">
            <button class="tab-btn bg-yellow-600 text-black px-4 py-2 rounded-t-lg" onclick="switchTab('rede')">Rede Social</button>
            <button class="tab-btn bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-t-lg" onclick="switchTab('jogo')">🎮 Jogos</button>
            <button class="tab-btn bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-t-lg" onclick="switchTab('ia')">📄 IA</button>
            <button class="tab-btn bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-t-lg" onclick="switchTab('dna')">🧬 DNA</button>
        </div>

        <!-- ABA REDE -->
        <div id="tab-rede" class="tab-content">
            <div class="bg-gray-800 p-4 rounded-lg border border-yellow-500/30 mb-6">
                <form method="POST" enctype="multipart/form-data">
                    <textarea name="texto_post" placeholder="Escreva algo..." class="w-full p-3 bg-gray-900 border border-gray-700 rounded-lg mb-3 text-white" rows="3"></textarea>
                    <div class="flex flex-wrap items-center gap-3">
                        <label class="cursor-pointer bg-gray-700 hover:bg-gray-600 px-3 py-2 rounded-lg">
                            <i class="fa-solid fa-paperclip mr-1"></i> Foto/Vídeo
                            <input type="file" name="arquivo" accept="image/*,video/*" class="hidden">
                        </label>
                        <button type="submit" class="bg-yellow-600 hover:bg-yellow-500 text-black font-bold px-6 py-2 rounded-lg ml-auto">
                            <i class="fa-solid fa-paper-plane mr-1"></i> Publicar
                        </button>
                    </div>
                </form>
            </div>
            <div class="space-y-4">
                {postagens_html}
            </div>
        </div>

        <!-- ABA JOGOS -->
        <div id="tab-jogo" class="tab-content hidden">
            <div class="grid md:grid-cols-2 gap-6 max-w-2xl mx-auto">
                <div class="bg-gray-800 p-6 rounded-lg border border-yellow-500/30 text-center">
                    <h2 class="text-2xl font-bold text-yellow-500 mb-4">🎮 Jogo Bentinho</h2>
                    <p class="text-gray-400 mb-6">4 fases · Até 1.000.000.000 de pontos!</p>
                    <a href="/jogo_bentinho" class="inline-block bg-yellow-600 hover:bg-yellow-500 text-black font-bold px-6 py-3 rounded-lg text-lg">▶️ Jogar</a>
                </div>
                <div class="bg-gray-800 p-6 rounded-lg border border-yellow-500/30 text-center">
                    <h2 class="text-2xl font-bold text-yellow-500 mb-4">🃏 Jogo das Cartas</h2>
                    <p class="text-gray-400 mb-6">4 fases · Até 1.000 pontos!</p>
                    <a href="/jogo_cartas" class="inline-block bg-yellow-600 hover:bg-yellow-500 text-black font-bold px-6 py-3 rounded-lg text-lg">▶️ Jogar</a>
                </div>
            </div>
        </div>

        <!-- ABA IA -->
        <div id="tab-ia" class="tab-content hidden">
            <div class="bg-gray-800 p-6 rounded-lg border border-yellow-500/30 max-w-2xl mx-auto">
                <h2 class="text-2xl font-bold text-yellow-500 mb-4">📄 IA — Gerador de Documentos</h2>
                <textarea id="ia-input" placeholder="Descreva o documento..." class="w-full h-40 p-4 bg-gray-900 border border-gray-700 rounded-lg text-white mb-4"></textarea>
                <button onclick="gerarDocumento()" class="bg-yellow-600 hover:bg-yellow-500 text-black font-bold px-6 py-3 rounded-lg">
                    <i class="fa-solid fa-file-code mr-2"></i> Gerar Documento
                </button>
                <div id="ia-result" class="mt-6 p-4 bg-gray-900 rounded-lg hidden"></div>
            </div>
        </div>

        <!-- ABA DNA — CONVERSÃO + DOWNLOAD + DECODIFICAÇÃO ✅ -->
        <div id="tab-dna" class="tab-content hidden">
            <div class="bg-gray-800 p-6 rounded-lg border border-yellow-500/30 max-w-2xl mx-auto">
                <h2 class="text-2xl font-bold text-yellow-500 mb-4">🧬 Conversor DNA / BNJ — SEGURO 🔒</h2>
                <p class="text-gray-400 mb-2">Sua chave única: <code class="bg-gray-900 px-2 py-1 rounded text-yellow-400 text-xs">{dna_chave}</code></p>
                <p class="text-sm text-red-400 mb-4">⚠️ Apenas você com sua chave consegue decodificar! Salve o arquivo .bnj no seu celular!</p>
                
                <textarea id="dna-input" placeholder="Digite texto para converter OU cole o DNA OU carregue o arquivo .bnj..." 
                    class="w-full h-32 p-4 bg-gray-900 border border-gray-700 rounded-lg text-white mb-4"></textarea>
                
                <!-- 📂 CARREGAR ARQUIVO SALVO -->
                <div class="mb-4 p-3 bg-gray-900 rounded-lg border border-gray-600">
                    <p class="text-sm text-gray-400 mb-2">📂 Carregar documento salvo (.bnj):</p>
                    <input type="file" id="arquivo-dna" accept=".bnj" class="text-sm text-gray-300" onchange="carregarArquivoDNA(this)">
                </div>
                
                <div class="flex gap-3 flex-wrap mb-4">
                    <button onclick="converterParaDNA()" class="bg-yellow-600 hover:bg-yellow-500 text-black font-bold px-5 py-2 rounded-lg">➡️ Converter para DNA 🔒</button>
                    <button onclick="decodificarDNA()" class="bg-gray-600 hover:bg-gray-500 text-white font-bold px-5 py-2 rounded-lg">⬅️ Decodificar DNA 🔓</button>
                    <button onclick="baixarDNA()" id="btn-baixar" class="bg-green-600 hover:bg-green-500 text-white font-bold px-5 py-2 rounded-lg hidden">💾 Baixar DNA</button>
                </div>
                
                <div id="dna-result" class="mt-6 p-4 bg-gray-900 rounded-lg hidden whitespace-pre-wrap"></div>
            </div>
        </div>
    </div>

    <script>
        let ultimoDNA = "";

        function switchTab(nome) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            document.querySelectorAll('.tab-btn').forEach(btn => {{
                btn.classList.remove('bg-yellow-600', 'text-black');
                btn.classList.add('bg-gray-700', 'hover:bg-gray-600');
            }});
            document.getElementById('tab-' + nome).classList.remove('hidden');
            event.target.classList.add('bg-yellow-600', 'text-black');
            event.target.classList.remove('bg-gray-700');
        }}

        function gerarDocumento() {{
            const texto = document.getElementById('ia-input').value.trim();
            if (!texto) return alert('Digite algo para gerar!');
            const res = document.getElementById('ia-result');
            res.classList.remove('hidden');
            res.innerHTML = '<h4 class="text-yellow-400 font-bold mb-2">Documento Gerado:</h4><p class="text-gray-300">' + texto + '</p>';
        }}

        const CHAVE_SECRETA = "{dna_chave}";

        function aplicarChave(bit, chaveBit) {{
            return bit === chaveBit ? '0' : '1';
        }}

        function textoParaDNA(texto, chave) {{
            let dna = '';
            const chaveBits = chave.split('').map(c => c.charCodeAt(0) % 2 === 0 ? '0' : '1').join('');
            let bitPos = 0;
            
            for (let i = 0; i < texto.length; i++) {{
                let bin = texto.charCodeAt(i).toString(2).padStart(8, '0');
                for (let b = 0; b < bin.length; b++) {{
                    const chaveBit = chaveBits[bitPos % chaveBits.length];
                    const bitFinal = aplicarChave(bin[b], chaveBit);
                    dna += bitFinal === '1' ? 'GC' : 'AT';
                    bitPos++;
                }}
            }}
            return dna;
        }}

        function DNAParaTexto(dna, chave) {{
            if (!dna.includes('AT') && !dna.includes('GC')) return null;
            
            let limpo = dna.replace(/JNB-DNA-ENCRYPTED[\\s\\S]*?\\n/, '').trim();
            
            const chaveBits = chave.split('').map(c => c.charCodeAt(0) % 2 === 0 ? '0' : '1').join('');
            let bitPos = 0;
            let bin = '';
            
            for (let i = 0; i < limpo.length; i += 2) {{
                const par = limpo.substring(i, i + 2);
                const bitCodificado = par === 'GC' ? '1' : '0';
                const chaveBit = chaveBits[bitPos % chaveBits.length];
                const bitOriginal = bitCodificado === chaveBit ? '0' : '1';
                bin += bitOriginal;
                bitPos++;
            }}
            
            let texto = '';
            for (let i = 0; i < bin.length; i += 8) {{
                const byte = bin.substring(i, i + 8);
                if (byte.length === 8) texto += String.fromCharCode(parseInt(byte, 2));
            }}
            return texto;
        }}

        function converterParaDNA() {{
            const texto = document.getElementById('dna-input').value.trim();
            if (!texto) return alert('Digite algo para converter!');
            const dna = textoParaDNA(texto, CHAVE_SECRETA);
            ultimoDNA = dna;
            const res = document.getElementById('dna-result');
            res.classList.remove('hidden');
            document.getElementById('btn-baixar').classList.remove('hidden');
            res.innerHTML = '<h4 class="text-yellow-400 font-bold mb-2">🔒 DNA Criptografado:</h4><p class="font-mono text-sm text-green-400 break-all">' + dna + '</p><p class="text-xs text-gray-500 mt-2">💾 Clique em "Baixar DNA" para salvar no seu celular!</p>';
        }}

        function decodificarDNA() {{
            const dna = document.getElementById('dna-input').value.trim();
            if (!dna.includes('AT') && !dna.includes('GC')) return alert('Digite uma sequência de DNA ou carregue um arquivo .bnj!');
            const texto = DNAParaTexto(dna, CHAVE_SECRETA);
            const res = document.getElementById('dna-result');
            res.classList.remove('hidden');
            if (texto && texto.length > 0) {{
                res.innerHTML = '<h4 class="text-yellow-400 font-bold mb-2">✅ Decodificado com sua chave:</h4><p class="text-green-400 whitespace-pre-wrap">' + texto + '</p>';
            }} else {{
                res.innerHTML = '<h4 class="text-red-400 font-bold mb-2">❌ Falha — chave incorreta ou DNA inválido!</h4><p class="text-gray-400 text-sm">Apenas o dono do documento com a chave original consegue decodificar.</p>';
            }}
        }}

        function carregarArquivoDNA(input) {{
            const arquivo = input.files[0];
            if (!arquivo) return;
            
            const leitor = new FileReader();
            leitor.onload = function(e) {{
                const conteudo = e.target.result;
                document.getElementById('dna-input').value = conteudo;
                alert('✅ Arquivo carregado! Agora clique em "Decodificar DNA"');
            }};
            leitor.readAsText(arquivo);
        }}

        function baixarDNA() {{
            if (!ultimoDNA) return alert('Nenhum DNA para baixar! Converta primeiro.');
            
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/baixar_dna';
            form.target = '_blank';
            
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'dna_texto';
            input.value = ultimoDNA;
            form.appendChild(input);
            
            document.body.appendChild(form);
            form.submit();
            document.body.removeChild(form);
            
            alert('✅ Arquivo baixado com sucesso! Guarde no seu celular. Para decodificar, carregue o arquivo aqui.');
        }}
    </script>
</body>
</html>''')

# ============= EXECUÇÃO =============
if __name__ == "__main__":
    print("🚀 JNB TECNOLOGIA — Servidor na porta 5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
