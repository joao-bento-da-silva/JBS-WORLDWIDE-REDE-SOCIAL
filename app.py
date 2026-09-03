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
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 315360000

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4", "mov", "avi", "webm", "bnj"}
BANCO_DADOS = "jnb_novo.db"

EMAIL_DONO = "seu_email_aqui@seu_dominio.com"
SENHA_MESTRA_ACESSO = "JNB@2026#DONO"

def usuario_logado():
    return "usuario_id" in session

def eh_dono():
    if not usuario_logado():
        return False
    try:
        conn = sqlite3.connect(BANCO_DADOS)
        c = conn.cursor()
        c.execute("SELECT email FROM usuarios WHERE id = ?", (session["usuario_id"],))
        usuario = c.fetchone()
        conn.close()
        return usuario and usuario[0].strip().lower() == EMAIL_DONO.lower()
    except:
        return False

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha_hash TEXT NOT NULL,
        pontos INTEGER DEFAULT 0,
        dna_chave TEXT NOT NULL,
        data_cadastro TEXT NOT NULL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS postagens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        texto TEXT,
        arquivo TEXT,
        data_postagem TEXT NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS curtidas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        postagem_id INTEGER NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (postagem_id) REFERENCES postagens(id),
        UNIQUE(usuario_id, postagem_id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS conversas_ia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        pergunta TEXT NOT NULL,
        resposta TEXT NOT NULL,
        data_hora TEXT NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )""")
    conn.commit()
    conn.close()

init_db()

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
        return "🧬 Cada usuário tem sua chave única. Salve o .bnj no celular!"
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
    <style>*{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif;}body{background:linear-gradient(180deg,#0f172a,#1e293b);color:#e2e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center;}.caixa{background:rgba(15,23,42,0.8);padding:40px;border-radius:12px;border:1px solid #f59e0b;width:90%;max-width:400px;}h1{color:#f59e0b;text-align:center;margin-bottom:30px;}input{width:100%;padding:12px;margin:8px 0;background:#020617;border:1px solid #334155;color:white;border-radius:6px;}button{width:100%;padding:12px;background:#f59e0b;color:#1e1b16;border:none;border-radius:6px;font-weight:bold;cursor:pointer;}.link{text-align:center;margin-top:15px;font-size:14px;color:#94a3b8;}.link a{color:#f59e0b;text-decoration:none;}</style>
</head>
<body><div class="caixa"><h1>JNB TECNOLOGIA</h1><form action="/entrar" method="POST"><input type="email" name="email" placeholder="E-mail" required><input type="password" name="senha" placeholder="Senha" required><button type="submit">Entrar</button></form><div class="link">Não tem conta? <a href="/cadastrar">Cadastre-se — PERMANENTE ✅</a></div></div></body></html>''')

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
                conn = sqlite3.connect(BANCO_DADOS)
                c = conn.cursor()
                c.execute("INSERT INTO usuarios (nome, email, senha_hash, dna_chave, data_cadastro) VALUES (?, ?, ?, ?, ?)",(nome, email, senha_hash, dna_chave, data_cad))
                conn.commit()
                usuario_id = c.lastrowid
                conn.close()
                session["usuario_id"] = usuario_id
                session["nome_usuario"] = nome
                return redirect(url_for("plataforma"))
            except sqlite3.IntegrityError:
                return '<div style="text-align:center;padding:50px;background:#0f172a;color:white;"><h2 style="color:red;">E-mail já cadastrado!</h2><a href="/cadastrar" style="color:#f59e0b;">Voltar</a></div>'
    return render_template_string('''<!DOCTYPE html><html lang="pt-br"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Cadastrar — JNB TECNOLOGIA</title><style>*{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif;}body{background:linear-gradient(180deg,#0f172a,#1e293b);color:#e2e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center;}.caixa{background:rgba(15,23,42,0.8);padding:40px;border-radius:12px;border:1px solid #f59e0b;width:90%;max-width:400px;}h1{color:#f59e0b;text-align:center;margin-bottom:30px;}input{width:100%;padding:12px;margin:8px 0;background:#020617;border:1px solid #334155;color:white;border-radius:6px;}button{width:100%;padding:12px;background:#f59e0b;color:#1e1b16;border:none;border-radius:6px;font-weight:bold;cursor:pointer;}.link{text-align:center;margin-top:15px;font-size:14px;color:#94a3b8;}.link a{color:#f59e0b;text-decoration:none;}</style></head><body><div class="caixa"><h1>Cadastrar ✅ PERMANENTE</h1><form method="POST"><input type="text" name="nome" placeholder="Seu nome" required><input type="email" name="email" placeholder="E-mail" required><input type="password" name="senha" placeholder="Senha" required><button type="submit">Cadastrar — Para Sempre</button></form><div class="link">Já tem conta? <a href="/">Entrar</a></div></div></body></html>''')

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
            session.permanent = True
            return redirect(url_for("plataforma"))
    return '<div style="text-align:center;padding:50px;background:#0f172a;color:white;"><h2 style="color:red;">E-mail ou senha inválidos!</h2><a href="/" style="color:#f59e0b;font-size:18px;">Voltar</a></div>'

@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("inicio"))

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/area_privada", methods=["GET", "POST"])
def area_privada():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    if not eh_dono():
        return '<div style="text-align:center;padding:50px;background:#0f172a;color:white;"><h2 style="color:red;">🚫 ACESSO NEGADO</h2><a href="/plataforma" style="color:#f59e0b;">Voltar</a></div>'
    if request.method == "POST":
        if request.form.get("senha_mestra") == SENHA_MESTRA_ACESSO:
            return redirect(url_for("painel_dono"))
        return '<div style="text-align:center;padding:50px;background:#0f172a;color:white;"><h2 style="color:red;">❌ Senha incorreta!</h2><a href="/area_privada" style="color:#f59e0b;">Tentar novamente</a></div>'
     
# ==============================================================================
# ROTA DO PAINEL DE DNA - CÓDIGO INTEGRAL CORRIGIDO
# ==============================================================================
@app.route("/dna_painel", methods=["GET", "POST"])
def dna_painel():
    if "usuario_id" not in session:
        return redirect(url_for("inicio"))

    resultado_texto = ""
    texto_original = ""
    acao_realizada = ""

    DNA_MAPA = {'00': 'A', '01': 'T', '10': 'C', '11': 'G'}
    REV_DNA_MAPA = {v: k for k, v in DNA_MAPA.items()}

    def texto_para_dna(texto):
        try:
            binario = "".join(f"{ord(c):08b}" for c in texto)
            return "".join(DNA_MAPA[binario[i:i+2]] for i in range(0, len(binario), 2))
        except Exception:
            return "Erro ao processar a criptografia."

    def dna_para_texto(dna):
        try:
            dna = "".join(c for c in dna.upper() if c in REV_DNA_MAPA)
            binario = "".join(REV_DNA_MAPA[c] for c in dna)
            caracteres = [chr(int(binario[i:i+8], 2)) for i in range(0, len(binario), 8)]
            return "".join(caracteres)
        except Exception:
            return "Erro: O conteudo nao possui uma sequencia valida de DNA."

    if request.method == "POST":
        texto_original = request.form.get("dna_texto", "").strip()
        botao_pressionado = request.form.get("acao", "")

        if texto_original:
            if botao_pressionado == "criptografar":
                resultado_texto = texto_para_dna(texto_original)
                acao_realizada = "Criptografado (DNA)"
                flash("Texto transformado em DNA com sucesso!", "sucesso")
                
            elif botao_pressionado == "descriptografar":
                if "JNB-DNA-ENCRYPTED" in texto_original:
                    linhas = texto_original.split("\n")
                    texto_original = linhas[-1].strip()
                
                resultado_texto = dna_para_texto(texto_original)
                acao_realizada = "Descriptografado para Texto Original"
                flash("Sequencia de DNA decodificada com sucesso!", "sucesso")

    html_template = """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Arquivos DNA</title>
    <script src="https://tailwindcss.com"></script>
    <style>body{background:linear-gradient(180deg,#090d16,#111827);color:#e2e8f0;min-height:100vh;}</style>
</head>
<body class="flex items-center justify-center p-4">
    <div class="bg-gray-900 p-8 rounded-xl border-2 border-emerald-500/50 max-w-2xl w-full shadow-2xl">
        <h1 class="text-4xl font-bold text-emerald-400 text-center mb-2 tracking-wide">SISTEMA DE ARQUIVOS DNA</h1>
        <p class="text-center text-gray-400 mb-6 text-sm">Criptografe documentos em sequencias geneticas ou decodifique arquivos .bnj</p>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="text-center p-3 rounded-lg mb-6 text-sm font-bold bg-emerald-950/80 text-emerald-400 border border-emerald-500/30">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <form method="POST" class="space-y-4">
            <div>
                <label class="block text-gray-400 mb-2 font-medium text-sm">Insira o texto original ou cole o DNA criptografado:</label>
                <textarea name="dna_texto" rows="6" placeholder="Digite o texto para criptografar OU cole a sequencia de DNA (A, T, C, G) para ler..." class="w-full bg-gray-950 border-2 border-gray-800 rounded-lg p-3 text-emerald-400 font-mono focus:border-emerald-500 focus:outline-none placeholder-gray-600" required>{{ texto_original }}</textarea>
            </div>

            <div class="grid grid-cols-2 gap-4">
                <button type="submit" name="acao" value="criptografar" class="bg-emerald-700 hover:bg-emerald-600 text-white font-bold py-3 rounded-lg transition duration-200 uppercase tracking-wider text-sm">
                    Criptografar para DNA
                </button>
                <button type="submit" name="acao" value="descriptografar" class="bg-cyan-700 hover:bg-cyan-600 text-white font-bold py-3 rounded-lg transition duration-200 uppercase tracking-wider text-sm">
                    Descriptografar DNA
                </button>
            </div>
        </form>

        {% if resultado_texto %}
        <div class="mt-8 pt-6 border-t border-gray-800">
            <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Resultado: [ {{ acao_realizada }} ]</h3>
            <div class="bg-gray-950 border border-emerald-500/20 rounded-lg p-4 font-mono text-yellow-400 max-h-48 overflow-y-auto whitespace-pre-wrap break-all text-sm select-all">{{ resultado_texto }}</div>
            
            <form action="/baixar_dna_arquivo" method="POST" class="mt-4">
                <input type="hidden" name="dna_texto" value="{{ resultado_texto }}">
                <button type="submit" class="w-full bg-yellow-600 hover:bg-yellow-500 text-black font-bold py-3 rounded-lg transition duration-200 uppercase tracking-wider text-sm">
                    Gerar e Baixar Arquivo .bnj
                </button>
            </form>
        </div>
        {% endif %}

        <p class="text-center mt-6 text-sm"><a href="/plataforma" class="text-emerald-500 hover:underline"><- Voltar para a Plataforma</a></p>
    </div>
</body>
</html>"""

    return render_template_string(html_template, texto_original=texto_original, resultado_texto=resultado_texto, acao_realizada=acao_realizada)
 # ==============================================================================
# 1. ROTA DO PAINEL PRINCIPAL (CRIPTOGRAFAR / DESCRIPTOGRAFAR)
# ==============================================================================
@app.route("/dna_painel", methods=["GET", "POST"])
def dna_painel():
    if "usuario_id" not in session:
        return redirect(url_for("inicio"))

    resultado_texto = ""
    texto_original = ""
    acao_realizada = ""

    DNA_MAPA = {'00': 'A', '01': 'T', '10': 'C', '11': 'G'}
    REV_DNA_MAPA = {v: k for k, v in DNA_MAPA.items()}

    def texto_para_dna(texto):
        try:
            binario = "".join(f"{ord(c):08b}" for c in texto)
            return "".join(DNA_MAPA[binario[i:i+2]] for i in range(0, len(binario), 2))
        except Exception:
            return "Erro ao processar a criptografia."

    def dna_para_texto(dna):
        try:
            dna = "".join(c for c in dna.upper() if c in REV_DNA_MAPA)
            binario = "".join(REV_DNA_MAPA[c] for c in dna)
            caracteres = [chr(int(binario[i:i+8], 2)) for i in range(0, len(binario), 8)]
            return "".join(caracteres)
        except Exception:
            return "Erro: O conteudo nao possui uma sequencia valida de DNA."

    if request.method == "POST":
        texto_original = request.form.get("dna_texto", "").strip()
        botao_pressionado = request.form.get("acao", "")

        if texto_original:
            if botao_pressionado == "criptografar":
                resultado_texto = texto_para_dna(texto_original)
                acao_realizada = "Criptografado (DNA)"
                flash("Texto transformado em DNA com sucesso!", "sucesso")
                
            elif botao_pressionado == "descriptografar":
                if "JNB-DNA-ENCRYPTED" in texto_original:
                    linhas = texto_original.split("\n")
                    texto_original = linhas[-1].strip()
                
                resultado_texto = dna_para_texto(texto_original)
                acao_realizada = "Descriptografado para Texto Original"
                flash("Sequencia de DNA decodificada com sucesso!", "sucesso")

    html_template = """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Arquivos DNA</title>
    <script src="https://tailwindcss.com"></script>
    <style>body{background:linear-gradient(180deg,#090d16,#111827);color:#e2e8f0;min-height:100vh;}</style>
</head>
<body class="flex items-center justify-center p-4">
    <div class="bg-gray-900 p-8 rounded-xl border-2 border-emerald-500/50 max-w-2xl w-full shadow-2xl">
        <h1 class="text-4xl font-bold text-emerald-400 text-center mb-2 tracking-wide">SISTEMA DE ARQUIVOS DNA</h1>
        <p class="text-center text-gray-400 mb-6 text-sm">Criptografe documentos em sequencias geneticas ou decodifique arquivos .bnj</p>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="text-center p-3 rounded-lg mb-6 text-sm font-bold bg-emerald-950/80 text-emerald-400 border border-emerald-500/30">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <form method="POST" class="space-y-4">
            <div>
                <label class="block text-gray-400 mb-2 font-medium text-sm">Insira o texto original ou cole o DNA criptografado:</label>
                <textarea name="dna_texto" rows="6" placeholder="Digite o texto para criptografar OU cole a sequencia de DNA (A, T, C, G) para ler..." class="w-full bg-gray-950 border-2 border-gray-800 rounded-lg p-3 text-emerald-400 font-mono focus:border-emerald-500 focus:outline-none placeholder-gray-600" required>{{ texto_original }}</textarea>
            </div>

            <div class="grid grid-cols-2 gap-4">
                <button type="submit" name="acao" value="criptografar" class="bg-emerald-700 hover:bg-emerald-600 text-white font-bold py-3 rounded-lg transition duration-200 uppercase tracking-wider text-sm">
                    Criptografar para DNA
                </button>
                <button type="submit" name="acao" value="descriptografar" class="bg-cyan-700 hover:bg-cyan-600 text-white font-bold py-3 rounded-lg transition duration-200 uppercase tracking-wider text-sm">
                    Descriptografar DNA
                </button>
            </div>
        </form>

        {% if resultado_texto %}
        <div class="mt-8 pt-6 border-t border-gray-800">
            <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Resultado: [ {{ acao_realizada }} ]</h3>
            <div class="bg-gray-950 border border-emerald-500/20 rounded-lg p-4 font-mono text-yellow-400 max-h-48 overflow-y-auto whitespace-pre-wrap break-all text-sm select-all">{{ resultado_texto }}</div>
            
            <form action="/baixar_dna_arquivo" method="POST" class="mt-4">
                <input type="hidden" name="dna_texto" value="{{ resultado_texto }}">
                <button type="submit" class="w-full bg-yellow-600 hover:bg-yellow-500 text-black font-bold py-3 rounded-lg transition duration-200 uppercase tracking-wider text-sm">
                    Gerar e Baixar Arquivo .bnj
                </button>
            </form>
        </div>
        {% endif %}

        <p class="text-center mt-6 text-sm"><a href="/plataforma" class="text-emerald-500 hover:underline"><- Voltar para a Plataforma</a></p>
    </div>
</body>
</html>"""

    return render_template_string(html_template, texto_original=texto_original, resultado_texto=resultado_texto, acao_realizada=acao_realizada)


# ==============================================================================
# 2. ROTA ADICIONAL (GERA O DOWNLOAD DO ARQUIVO .BNJ)
# ==============================================================================
@app.route("/baixar_dna_arquivo", methods=["POST"])
def baixar_dna_arquivo():
    if "usuario_id" not in session:
        return redirect(url_for("inicio"))
        
    dna_texto = request.form.get("dna_texto", "").strip()
    if not dna_texto:
        return "Nenhum dado fornecido", 400
        
    data_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conteudo = f"JNB-DNA-ENCRYPTED\r\n{data_atual}\r\n{dna_texto}"
    
    resp = make_response(conteudo)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    resp.headers["Content-Disposition"] = f"attachment; filename=documento_dna_{timestamp}.bnj"
    resp.headers["Content-Type"] = "application/octet-stream"
    
    return resp

