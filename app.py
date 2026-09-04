 # ==================================================
# © 2026 JNB TECNOLOGIA — VERSÃO PERMANENTE 
# REDE · JOGOS · IA · DNA · CADASTRO PERMANENTE ✅
# ==================================================

from flask import Flask, request, session, redirect, url_for, render_template_string, make_response
import psycopg2
from psycopg2.extras import RealDictCursor
import cloudinary
import cloudinary.uploader
import os
import random
import hashlib
import base64
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("CHAVE_UNIFICADA", "JNB_TECNOLOGIA_2026_SEGURA")
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 315360000

# ⚠️ AUMENTA O LIMITE DE UPLOAD DO FLASK PARA VÍDEOS (Ex: 100 MB)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# 1. CONEXÃO COM BANCO DE DADOS PERMANENTE (PostgreSQL)
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# 2. CONFIGURAÇÃO DE FOTOS E VÍDEOS PERMANENTES (Cloudinary)
cloudinary.config(
    cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key = os.environ.get("CLOUDINARY_API_KEY"),
    api_secret = os.environ.get("CLOUDINARY_API_SECRET")
)

# 🔒 ÁREA PRIVADA — COLOQUE SEU E-MAIL AQUI
EMAIL_DONO = "seu_email_aqui@seu_dominio.com"
SENHA_MESTRA_ACESSO = "JNB@2026#DONO"

def eh_dono():
    if not usuario_logado():
        return False
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT email FROM usuarios WHERE id = %s", (session["usuario_id"],))
        usuario = c.fetchone()
        conn.close()
        return usuario and usuario[0].strip().lower() == EMAIL_DONO.lower()
    except:
        return False

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha_hash TEXT NOT NULL,
        pontos BIGINT DEFAULT 0,
        dna_chave TEXT NOT NULL,
        data_cadastro TEXT NOT NULL
    );""")
    c.execute("""CREATE TABLE IF NOT EXISTS postagens (
        id SERIAL PRIMARY KEY,
        usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
        texto TEXT,
        arquivo TEXT,
        data_postagem TEXT NOT NULL
    );""")
    c.execute("""CREATE TABLE IF NOT EXISTS curtidas (
        id SERIAL PRIMARY KEY,
        usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
        postagem_id INTEGER NOT NULL REFERENCES postagens(id) ON DELETE CASCADE,
        UNIQUE(usuario_id, postagem_id)
    );""")
    c.execute("""CREATE TABLE IF NOT EXISTS conversas_ia (
        id SERIAL PRIMARY KEY,
        usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
        pergunta TEXT NOT NULL,
        resposta TEXT NOT NULL,
        data_hora TEXT NOT NULL
    );""")
    conn.commit()
    conn.close()

try:
    init_db()
except Exception as e:
    print(f"Aguardando conexão com o Banco de Dados: {e}")

def usuario_logado():
    return "usuario_id" in session

def responder_ia(pergunta):
    p = pergunta.lower().strip()
    if "brasil" in p and ("descobriu" in p or "ano" in p):
        return "O Brasil foi descoberto em 22 de abril de 1500 por Pedro Álvares Cabral."
    elif "quem é você" in p or "quem criou" in p:
        return "Eu sou a IA da JNB TECNOLOGIA, criada por João Bento da Silva."
    elif "jogo" in p and "cartas" in p:
        return "🃏 Y→Y, A→Z, Z→A, B→X, X→B, C→G, G→C, D→F, F→D, E→E."
    elif "bentinho" in p or "números" in p:
        return "🎮 0→0, 1→9, 2→8, 3→7, 4→6, 5→5, 6→4, 7→3, 8→2, 9→1."
    elif "dna" in p:
        return "🧬 Cada usuário tem sua chave única. Criptografe suas mensagens e salve o .bnj no celular!"
    elif "oi" in p or "olá" in p:
        return "Olá! 👋 Bem-vindo à JNB TECNOLOGIA!"
    else:
        return f"Entendi! Você perguntou: \"{pergunta}\""

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
        <div class="link">Não tem conta? <a href="/cadastrar">Cadastre-se — PERMANENTE ✅</a></div>
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
            data_cad = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("INSERT INTO usuarios (nome, email, senha_hash, dna_chave, data_cadastro) VALUES (%s, %s, %s, %s, %s) RETURNING id;",
                          (nome, email, senha_hash, dna_chave, data_cad))
                usuario_id = c.fetchone()[0]
                conn.commit()
                conn.close()
                session["usuario_id"] = usuario_id
                session["nome_usuario"] = nome
                return redirect(url_for("plataforma"))
            except Exception as e:
                return f'''<div style="text-align:center;padding:50px;background:#0f172a;color:white;">
                    <h2 style="color:red;">Erro ou E-mail já cadastrado!</h2>
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
        <h1>Cadastrar ✅ PERMANENTE</h1>
        <form method="POST">
            <input type="text" name="nome" placeholder="Seu nome" required>
            <input type="email" name="email" placeholder="E-mail" required>
            <input type="password" name="senha" placeholder="Senha" required>
            <button type="submit">Cadastrar — Para Sempre</button>
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
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT id, nome FROM usuarios WHERE email = %s AND senha_hash = %s", (email, senha_hash))
        usuario = c.fetchone()
        conn.close()
        if usuario:
            session["usuario_id"] = usuario[0]
            session["nome_usuario"] = usuario[1]
            session.permanent = True
            return redirect(url_for("plataforma"))
    return '''<div style="text-align:center;padding:50px;background:#0f172a;color:white;">
        <h2 style="color:red;">E-mail ou senha inválidos!</h2>
        <a href="/" style="color:#f59e0b;font-size:18px;">Voltar</a>
    </div>'''

@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("inicio"))

@app.route("/area_privada", methods=["GET", "POST"])
def area_privada():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    if not eh_dono():
        return '''<div style="text-align:center;padding:50px;background:#0f172a;color:white;">
            <h2 style="color:red;">🚫 ACESSO NEGADO — Área exclusiva do dono</h2>
            <a href="/plataforma" style="color:#f59e0b;">Voltar</a>
        </div>'''
    if request.method == "POST":
        if request.form.get("senha_mestra") == SENHA_MESTRA_ACESSO:
            return redirect(url_for("painel_dono"))
        return '''<div style="text-align:center;padding:50px;background:#0f172a;color:white;">
            <h2 style="color:red;">❌ Senha incorreta!</h2>
            <a href="/area_privada" style="color:#f59e0b;">Tentar novamente</a>
        </div>'''
    return render_template_string('''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔒 Área Privada</title>
    <style>body{background:linear-gradient(180deg,#0f172a,#1e293b);color:white;min-height:100vh;display:flex;align-items:center;justify-content:center;font-family:Arial,sans-serif;}
    .caixa{background:rgba(15,23,42,0.9);padding:40px;border-radius:12px;border:2px solid #f59e0b;max-width:400px;width:90%;text-align:center;}
    h1{color:#f59e0b;margin-bottom:20px;}
    input{width:100%;padding:12px;margin:8px 0;background:#020617;border:1px solid #334155;color:white;border-radius:6px;}
    button{width:100%;padding:12px;background:#f59e0b;color:black;border:none;border-radius:6px;font-weight:bold;cursor:pointer;}
    a{color:#f59e0b;text-decoration:none;display:block;margin-top:20px;}</style>
</head>
<body>
    <div class="caixa">
        <h1>🔒 ÁREA PRIVADA</h1>
        <p style="margin-bottom:20px;">Confirme a senha mestra para acessar</p>
        <form method="POST">
            <input type="password" name="senha_mestra" placeholder="Senha Mestra" required>
            <button type="submit">🔓 Desbloquear</button>
        </form>
        <a href="/plataforma">← Voltar</a>
    </div>
</body>
</html>''')

@app.route("/painel_dono")
def painel_dono():
    if not usuario_logado() or not eh_dono():
        return redirect(url_for("inicio"))
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM usuarios")
    total_usuarios = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM postagens")
    total_postagens = c.fetchone()[0]
    conn.close()
    return render_template_string(f'''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚙️ Painel do Dono</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body{{background:linear-gradient(180deg,#0f172a,#1e293b);color:#e2e8f0;min-height:100vh;}}</style>
</head>
<body class="p-6 max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold text-yellow-500 mb-6">⚙️ PAINEL DO DONO</h1>
    <a href="/plataforma" class="text-yellow-500 mb-4 inline-block">← Voltar</a>
    <div class="grid grid-cols-2 gap-4">
        <div class="bg-gray-800 p-4 rounded-lg border border-yellow-500/30">
            <p class="text-gray-400">Total de Usuários</p>
            <p class="text-2xl font-bold text-yellow-500">{total_usuarios}</p>
        </div>
        <div class="bg-gray-800 p-4 rounded-lg border border-yellow-500/30">
            <p class="text-gray-400">Total de Postagens</p>
            <p class="text-2xl font-bold text-yellow-500">{total_postagens}</p>
        </div>
    </div>
</body>
</html>''')

@app.route("/responder_ia", methods=["POST"])
def responder_ia_rota():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    pergunta = request.form.get("pergunta", "").strip()
    if not pergunta:
        return "Digite uma pergunta!"
    resposta = responder_ia(pergunta)
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO conversas_ia (usuario_id, pergunta, resposta, data_hora) VALUES (%s, %s, %s, %s)",
              (session["usuario_id"], pergunta, resposta, data_hora))
    conn.commit()
    conn.close()
    return resposta

@app.route("/jogo_cartas", methods=["GET", "POST"])
def jogo_cartas():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    REGRAS = {'Y':'Y','A':'Z','Z':'A','B':'X','X':'B','C':'G','G':'C','D':'F','F':'D','E':'E'}
    CARTAS = ['Y','A','B','C','D','E','F','G','X','Z']
    if "cartas_fase" not in session: session["cartas_fase"] = 1
    if "cartas_pontos" not in session: session["cartas_pontos"] = 0
    fase = session["cartas_fase"]
    pontos = session["cartas_pontos"]
    qtd = {1:3,2:6,3:8,4:9}[fase]
    valor = {1:100,2:300,3:500,4:1000}[fase]
    if "cartas_alvo" not in session or len(session.get("cartas_alvo",[])) != qtd:
        session["cartas_alvo"] = random.sample(CARTAS, qtd)
        session["cartas_resposta"] = []
    alvo = session["cartas_alvo"]
    resposta = session["cartas_resposta"]
    msg = ""
    if request.method == "POST":
        if "nova" in request.form:
            session["cartas_alvo"] = random.sample(CARTAS, qtd)
            session["cartas_resposta"] = []
        elif "selecionar" in request.form:
            resposta.append(request.form["selecionar"])
            session["cartas_resposta"] = resposta
        elif "verificar" in request.form:
            if len(resposta) != len(alvo):
                msg = "❌ Selecione todas!"
            else:
                correta = [REGRAS[c] for c in alvo]
                if resposta == correta:
                    pontos += valor
                    session["cartas_pontos"] = pontos
                    msg = f"✅ ACERTOU! +{valor} PONTOS!"
                    try:
                        conn = get_db_connection()
                        c = conn.cursor()
                        c.execute("UPDATE usuarios SET pontos = pontos + %s WHERE id = %s", (valor, session["usuario_id"]))
                        conn.commit()
                        conn.close()
                    except: pass
                    if fase < 4:
                        session["cartas_fase"] += 1
                        session.pop("cartas_alvo", None)
                    else:
                        msg = "🏆 VENCEU!"
                        session["cartas_fase"] = 1
                        session.pop("cartas_alvo", None)
                else:
                    msg = "❌ Errou!"
                    session["cartas_resposta"] = []
    alvo_html = "".join([f"<span style='background:#f59e0b;color:black;padding:12px 18px;border-radius:8px;margin:5px;font-size:24px;font-weight:bold;'>{c}</span>" for c in alvo])
    resp_html = "".join([f"<span style='background:#22c55e;color:black;padding:12px 18px;border-radius:8px;margin:5px;font-size:24px;font-weight:bold;'>{c}</span>" for c in resposta]) if resposta else "<p style='color:#94a3b8;'>Clique nas cartas...</p>"
    disp_html = "".join([f"<button type='submit' name='selecionar' value='{c}' style='background:#33415e;color:white;padding:12px 18px;border-radius:8px;margin:5px;font-size:24px;font-weight:bold;border:2px solid #f59e0b;cursor:pointer;'>{c}</button>" for c in CARTAS])
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
    <a href="/plataforma" class="text-yellow-500">← Voltar</a>
    <h1 class="text-4xl font-bold text-yellow-500 text-center my-6">🃏 Jogo das Cartas</h1>
    <p class="text-center text-lg mb-4">Fase {fase}/4 · Pontos: {pontos}</p>
    {f'<div class="text-center p-3 rounded-lg mb-4 text-lg font-bold {"bg-green-900/50 text-green-400" if "✅" in msg or "🏆" in msg else "bg-red-900/50 text-red-400"}">{msg}</div>' if msg else ''}
    <div class="bg-gray-800 p-5 rounded-lg border border-yellow-500/30 mb-5">
        <p class="text-center mb-3 text-gray-400">🎯 Cartas Alvo:</p>
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
    <div class="flex gap-3 justify-center">
        <form method="POST"><button type="submit" name="verificar" class="bg-green-600 text-white font-bold px-6 py-3 rounded-lg">✅ Verificar</button></form>
        <form method="POST"><button type="submit" name="nova" class="bg-yellow-600 text-black font-bold px-6 py-3 rounded-lg">🔄 Novas</button></form>
    </div>
</body>
</html>''')

@app.route("/jogo_bentinho", methods=["GET", "POST"])
def jogo_bentinho():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    
    TABELA = {'0':'0','1':'9','2':'8','3':'7','4':'6','5':'5','6':'4','7':'3','8':'2','9':'1'}
    def inverter(num): return "".join(TABELA[d] for d in num if d in TABELA)
    
    if "bent_fase" not in session or session["bent_fase"] not in [1, 2, 3, 4]: 
        session["bent_fase"] = 1
    if "bent_pontos" not in session: 
        session["bent_pontos"] = 0
        
    if "bent_num" not in session or session.get("bent_fase_atual") != session["bent_fase"] or "bent_alvo" not in session:
        tam = {1:3, 2:6, 3:8, 4:9}[session["bent_fase"]]
        session["bent_num"] = "".join(random.choice("0123456789") for _ in range(tam))
        session["bent_alvo"] = inverter(session["bent_num"])
        session["bent_fase_atual"] = session["bent_fase"]
        
    msg = ""
    PTS = {1:250000, 2:2500000, 3:25000000, 4:1000000000}
    
    if request.method == "POST":
        if request.form.get("acao") == "reiniciar":
            session["bent_fase"] = 1
            session["bent_pontos"] = 0
            session.pop("bent_num", None)
            session.pop("bent_alvo", None)
            session.pop("bent_fase_atual", None)
            return redirect(url_for("jogo_bentinho"))
            
        resp = request.form.get("resposta", "").strip()
        alvo_correto = session.get("bent_alvo", "")
        
        if resp and resp == alvo_correto:
            pts = PTS.get(session["bent_fase"], 250000)
            session["bent_pontos"] += pts
            msg = f"✅ ACERTOU! +{pts:,} PONTOS!".replace(",", ".")
            
            try:
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("UPDATE usuarios SET pontos = pontos + %s WHERE id = %s", (pts, session["usuario_id"]))
                conn.commit()
                conn.close()
            except Exception as err:
                print(f"Erro ao salvar pontos do Bentinho: {err}")
                
            if session["bent_fase"] < 4:
                session["bent_fase"] += 1
                session.pop("bent_num", None)
                session.pop("bent_alvo", None)
            else:
                msg = "🏆 PARABÉNS! VOCÊ VENCEU O JOGO DOS NÚMEROS!"
                session["bent_fase"] = 1
                session.pop("bent_num", None)
                session.pop("bent_alvo", None)
        else:
            msg = "❌ Errou!"
            session["bent_pontos"] = 0
            
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
        <p class="text-center text-gray-400 mb-6">Fase {session.get("bent_fase", 1)}/4 · Pontos: {session.get("bent_pontos", 0)}</p>
        {f'<div class="text-center p-4 rounded-lg mb-6 text-lg font-bold {"bg-green-900/50 text-green-400" if "✅" in msg or "🏆" in msg else "bg-red-900/50 text-red-400"}">{msg}</div>' if msg else ''}
        <div class="bg-gray-900 border-2 border-yellow-500/40 rounded-lg p-6 text-center mb-6">
            <p class="text-gray-400 mb-2">Número:</p>
            <p class="text-5xl font-mono text-yellow-400 font-bold tracking-widest">{session.get("bent_num", "---")}</p>
        </div>
        <form method="POST" class="space-y-4">
            <input type="text" name="resposta" placeholder="___" class="w-full bg-gray-900 border-2 border-yellow-500 rounded-lg text-center text-2xl text-yellow-400 p-3 font-mono" required autocomplete="off">
            <div class="flex gap-3">
                <button type="submit" class="flex-1 bg-yellow-600 text-black font-bold py-3 rounded-lg text-lg">✅ Decifrar</button>
                <button type="submit" name="acao" value="reiniciar" class="bg-gray-600 text-white px-6 py-3 rounded-lg">🔄 Reiniciar</button>
            </div>
        </form>
        <p class="text-center mt-6"><a href="/plataforma" class="text-yellow-500">← Voltar</a></p>
    </div>
</body>
</html>''')

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

@app.route("/plataforma", methods=["GET", "POST"])
def plataforma():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    usuario_id = session["usuario_id"]
    
    # PROCESSAMENTO DE POSTAGENS E UPLOADS
    if request.method == "POST" and "texto_post" in request.form:
        texto = request.form.get("texto_post", "").strip()
        arquivo = request.files.get("arquivo")
        url_midia = None
        
        if arquivo and arquivo.filename != "":
            try:
                # upload automático que aceita fotos, GIFs e vídeos
                res = cloudinary.uploader.upload(
                    arquivo,
                    resource_type="auto"
                )
                url_midia = res.get("secure_url")
            except Exception as e:
                print(f"Erro ao enviar mídia para Cloudinary: {e}")

        if texto or url_midia:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("INSERT INTO postagens (usuario_id, texto, arquivo, data_postagem) VALUES (%s, %s, %s, %s)",
                      (usuario_id, texto, url_midia, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
        return redirect(url_for("plataforma"))
    
    if "curtir" in request.args:
        pid = request.args.get("curtir")
        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO curtidas (usuario_id, postagem_id) VALUES (%s, %s)", (usuario_id, pid))
            conn.commit()
        except:
            conn.rollback()
            c.execute("DELETE FROM curtidas WHERE usuario_id = %s AND postagem_id = %s", (usuario_id, pid))
            conn.commit()
        conn.close()
        return redirect(url_for("plataforma") + "#post-" + str(pid))
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT nome, pontos, dna_chave, email FROM usuarios WHERE id = %s", (usuario_id,))
    usuario_dados = c.fetchone()
    if not usuario_dados:
        conn.close()
        session.clear()
        return redirect(url_for("inicio"))
    nome_usuario, total_pontos, dna_chave, email_usuario = usuario_dados
    
    c.execute("""SELECT p.id, p.texto, p.arquivo, p.data_postagem, u.nome,
               (SELECT COUNT(*) FROM curtidas c WHERE c.postagem_id = p.id) as total_curtidas,
               EXISTS(SELECT 1 FROM curtidas c WHERE c.postagem_id = p.id AND c.usuario_id = %s) as curtiu
               FROM postagens p JOIN usuarios u ON p.usuario_id = u.id ORDER BY p.data_postagem DESC""", (usuario_id,))
    postagens = c.fetchall()
    conn.close()
    
    posts_html = ""
    for p in postagens:
        pid, texto, arquivo, data, autor, curtidas, curtiu = p
        posts_html += f'''<div id="post-{pid}" class="bg-gray-800 p-4 rounded-lg border border-yellow-500/30 mb-4">
            <h4 class="font-bold text-yellow-400">{autor}</h4><p class="text-sm text-gray-400">{data}</p>
            {f'<p class="my-3 whitespace-pre-wrap">{texto}</p>' if texto else ''}'''
        
        # EXIBIÇÃO DE MÍDIA (FOTO OU VÍDEO)
        if arquivo:
            arq_lower = arquivo.lower()
            if any(ext in arq_lower for ext in [".mp4", ".mov", ".webm", ".m4v", ".avi", "/video/"]):
                posts_html += f'<video controls class="max-w-full rounded-lg my-3 w-full max-h-96"><source src="{arquivo}"></video>'
            else:
                posts_html += f'<img src="{arquivo}" class="max-w-full rounded-lg my-3 max-h-96 object-cover">'
                
        posts_html += f'''<div class="mt-3 pt-3 border-t border-gray-700">
            <a href="/plataforma?curtir={pid}#post-{pid}" class="text-{'red' if curtiu else 'gray'}-400 font-bold">👍 {curtidas} Curtida{'s' if curtidas != 1 else ''}</a>
        </div></div>'''
        
    if not posts_html:
        posts_html = '<p class="text-center text-gray-500 py-10">Ainda não há postagens. Seja o primeiro!</p>'
    
    botao_admin = f'<a href="/area_privada" class="bg-red-600 text-white px-4 py-2 rounded-lg text-sm ml-2">🔒 Área Privada</a>' if email_usuario.strip().lower() == EMAIL_DONO.lower() else ""
    
    return render_template_string(f'''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plataforma — JNB TECNOLOGIA</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>.tab-content{{display:block;}}.tab-content.hidden{{display:none !important;}}</style>
</head>
<body class="bg-gray-900 text-gray-100 min-h-screen">
    <div class="container mx-auto px-4 py-6">
        <div class="flex flex-wrap justify-between items-center border-b border-gray-700 pb-4 mb-6">
            <div><h1 class="text-2xl font-bold text-yellow-500">⚡ JNB TECNOLOGIA</h1><p class="text-gray-400">Bem-vindo, {nome_usuario}!</p></div>
            <div class="text-right">
                <p class="text-sm text-gray-400">Pontos</p><p class="text-xl font-bold text-yellow-500">{total_pontos}</p>
                <a href="/sair" class="text-red-400 text-sm ml-2">Sair</a> {botao_admin}
            </div>
        </div>
        <div class="flex flex-wrap gap-2 mb-6 border-b border-gray-700 pb-2">
            <button class="tab-btn bg-yellow-600 text-black px-4 py-2 rounded-t-lg" onclick="switchTab('rede', event)">Rede Social</button>
            <button class="tab-btn bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-t-lg" onclick="switchTab('jogo', event)">🎮 Jogos</button>
            <button class="tab-btn bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-t-lg" onclick="switchTab('ia', event)">🤖 IA</button>
            <button class="tab-btn bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-t-lg" onclick="switchTab('dna', event)">🧬 DNA</button>
        </div>
        
        <div id="tab-rede" class="tab-content">
            <div class="bg-red-900/30 border border-red-500/50 p-4 rounded-lg mb-4">
                <p class="text-red-300 font-bold">⚠️ Proibido: nudez, conteúdo sexual, violência, ódio, ilegal. Postagens inadequadas serão apagadas e usuário banido.</p>
            </div>
            
            <!-- FORMULÁRIO COM ENCTYPE CONFIGURADO PARA ACEITAR ARQUIVOS -->
            <div class="bg-gray-800 p-4 rounded-lg border border-yellow-500/30 mb-6">
                <form method="POST" action="/plataforma" enctype="multipart/form-data">
                    <textarea name="texto_post" placeholder="Compartilhe algo..." class="w-full p-3 bg-gray-900 border border-gray-700 rounded-lg mb-3 text-white" rows="3"></textarea>
                    <div class="flex flex-wrap items-center gap-3">
                        <label class="cursor-pointer bg-gray-700 hover:bg-gray-600 px-3 py-2 rounded-lg text-sm text-white font-bold">
                            📷 Foto / Vídeo
                            <input type="file" name="arquivo" accept="image/*,video/*" class="hidden" onchange="mostrarNomeArquivo(this)">
                        </label>
                        <span id="nome-arquivo" class="text-xs text-yellow-400 font-mono"></span>
                        <button type="submit" class="bg-yellow-600 hover:bg-yellow-500 text-black font-bold px-6 py-2 rounded-lg ml-auto">📤 Publicar ✅ Permanente</button>
                    </div>
                </form>
            </div>
            <div class="space-y-4">{posts_html}</div>
        </div>
        
        <div id="tab-jogo" class="tab-content hidden">
            <div class="grid md:grid-cols-2 gap-6 max-w-2xl mx-auto">
                <div class="bg-gray-800 p-6 rounded-lg border border-yellow-500/30 text-center">
                    <h2 class="text-2xl font-bold text-yellow-500 mb-4">🎮 Jogo Bentinho</h2>
                    <p class="text-gray-400 mb-6">4 fases · Até 1.000.000.000 de pontos!</p>
                    <a href="/jogo_bentinho" class="inline-block bg-yellow-600 text-black font-bold px-6 py-3 rounded-lg">▶️ Jogar</a>
                </div>
                <div class="bg-gray-800 p-6 rounded-lg border border-yellow-500/30 text-center">
                    <h2 class="text-2xl font-bold text-yellow-500 mb-4">🃏 Jogo das Cartas</h2>
                    <p class="text-gray-400 mb-6">4 fases · Até 1.000 pontos!</p>
                    <a href="/jogo_cartas" class="inline-block bg-yellow-600 text-black font-bold px-6 py-3 rounded-lg">▶️ Jogar</a>
                </div>
            </div>
        </div>
        
        <div id="tab-ia" class="tab-content hidden">
            <div class="bg-gray-800 p-6 rounded-lg border border-yellow-500/30 max-w-2xl mx-auto">
                <h2 class="text-2xl font-bold text-yellow-500 mb-4">🤖 IA — Pergunte!</h2>
                <div id="ia-conversa" class="bg-gray-900 p-4 rounded-lg mb-4 h-64 overflow-y-auto space-y-3"></div>
                <form onsubmit="enviarIA(event)">
                    <input type="text" id="pergunta-ia" placeholder="Faça sua pergunta..." class="w-full p-3 bg-gray-900 border border-gray-700 rounded-lg mb-3 text-white">
                    <button type="submit" class="bg-yellow-600 text-black font-bold px-6 py-2 rounded-lg">Enviar</button>
                </form>
            </div>
        </div>
        
        <div id="tab-dna" class="tab-content hidden">
            <div class="bg-gray-800 p-6 rounded-lg border border-yellow-500/30 max-w-2xl mx-auto">
                <h2 class="text-2xl font-bold text-yellow-500 mb-4">🧬 DNA — Criptografia</h2>
                <p class="text-gray-400 mb-4">Sua chave única: <code id="chave-dna" class="bg-gray-900 px-2 py-1 rounded text-yellow-400">{dna_chave}</code></p>
                
                <form method="POST" action="/baixar_dna">
                    <textarea id="dna_texto" name="dna_texto" placeholder="Digite ou cole sua mensagem aqui..." class="w-full p-3 bg-gray-900 border border-gray-700 rounded-lg mb-3 text-white" rows="5"></textarea>
                    
                    <div class="flex flex-wrap gap-2 mb-4">
                        <button type="button" onclick="criptografarDNA()" class="bg-yellow-600 hover:bg-yellow-500 text-black font-bold px-4 py-2 rounded-lg">🔒 Criptografar</button>
                        <button type="button" onclick="descriptografarDNA()" class="bg-blue-600 hover:bg-blue-500 text-white font-bold px-4 py-2 rounded-lg">🔓 Descriptografar</button>
                        <button type="submit" class="bg-green-600 hover:bg-green-500 text-white font-bold px-4 py-2 rounded-lg ml-auto">📥 Baixar .bnj</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    
    <script>
    function switchTab(nome, evt) {{
        document.querySelectorAll('.tab-content').forEach(t => t.classList.add('hidden'));
        document.querySelectorAll('.tab-btn').forEach(b => {{b.classList.remove('bg-yellow-600','text-black');b.classList.add('bg-gray-700','hover:bg-gray-600');}});
        document.getElementById('tab-' + nome).classList.remove('hidden');
        if(evt) {{
            evt.target.classList.add('bg-yellow-600','text-black');
            evt.target.classList.remove('bg-gray-700','hover:bg-gray-600');
        }}
    }}

    function mostrarNomeArquivo(input) {{
        const txt = input.files[0] ? input.files[0].name : '';
        document.getElementById('nome-arquivo').innerText = txt ? "📎 " + txt : "";
    }}

    async function enviarIA(e) {{
        e.preventDefault();
        const pergunta = document.getElementById('pergunta-ia').value;
        if(!pergunta) return;
        const div = document.getElementById('ia-conversa');
        div.innerHTML += `<div class="bg-gray-800 p-2 rounded"><strong class="text-yellow-400">Você:</strong> ${{pergunta}}</div>`;
        document.getElementById('pergunta-ia').value = '';
        const resp = await fetch('/responder_ia', {{method:'POST', body:new URLSearchParams({{pergunta}})}});
        const texto = await resp.text();
        div.innerHTML += `<div class="bg-gray-800 p-2 rounded"><strong class="text-green-400">IA:</strong> ${{texto}}</div>`;
        div.scrollTop = div.scrollHeight;
    }}

    function criptografarDNA() {{
        const campo = document.getElementById('dna_texto');
        const txt = campo.value;
        if(!txt) return alert("Digite um texto para criptografar!");
        try {{
            const encriptado = btoa(encodeURIComponent(txt));
            campo.value = "DNA-ENC::" + encriptado;
        }} catch(e) {{
            alert("Erro ao criptografar!");
        }}
    }}

    function descriptografarDNA() {{
        const campo = document.getElementById('dna_texto');
        let txt = campo.value.trim();
        if(!txt) return alert("Cole o texto criptografado para descriptografar!");
        if(txt.startsWith("DNA-ENC::")) {{
            txt = txt.replace("DNA-ENC::", "");
        }}
        try {{
            const decriptado = decodeURIComponent(atob(txt));
            campo.value = decriptado;
        }} catch(e) {{
            alert("Texto inválido ou não criptografado com o formato DNA!");
        }}
    }}
    </script>
</body>
</html>''')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
