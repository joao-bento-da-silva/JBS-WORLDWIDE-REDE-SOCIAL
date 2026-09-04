 # ================================================== 
# © 2026 JNB TECNOLOGIA — VERSÃO DEFINITIVA CORRIGIDA
# REDE · JOGOS BENTINHO + CARTAS · IA APRENDIZ · DNA ATGC
# CADASTRO PERMANENTE · POSTAGENS PERMANENTES · PORTA 5000
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
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 315360000

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4", "mov", "avi", "webm", "bnj"}

EMAIL_DONO = os.environ.get("EMAIL_DONO", "joasilva19577@gmail.com")

# ==============================================
# CONEXÃO COM O BANCO DE DADOS HÍBRIDO (POSTGRES / SQLITE)
# ==============================================
def get_db():
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        try:
            import psycopg2
            import psycopg2.extras
            if database_url.startswith("postgres://"):
                database_url = database_url.replace("postgres://", "postgresql://", 1)
            conn = psycopg2.connect(database_url, cursor_factory=psycopg2.extras.DictCursor)
            return conn, "postgres"
        except Exception as e:
            print(f"Erro de conexão Postgres: {e}")

    conn = sqlite3.connect(os.path.join(BASE_DIR, "jnb_definitiva.db"))
    conn.row_factory = sqlite3.Row
    return conn, "sqlite"

def init_db():
    conn, db_type = get_db()
    c = conn.cursor()
    
    pk_auto = "SERIAL PRIMARY KEY" if db_type == "postgres" else "INTEGER PRIMARY KEY AUTOINCREMENT"
    
    c.execute(f"""CREATE TABLE IF NOT EXISTS usuarios (
        id {pk_auto},
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha_hash TEXT NOT NULL,
        pontos INTEGER DEFAULT 0,
        dna_chave TEXT NOT NULL,
        data_cadastro TEXT NOT NULL
    )""")
    
    c.execute(f"""CREATE TABLE IF NOT EXISTS postagens (
        id {pk_auto},
        usuario_id INTEGER NOT NULL,
        texto TEXT,
        arquivo TEXT,
        data_postagem TEXT NOT NULL
    )""")
    
    c.execute(f"""CREATE TABLE IF NOT EXISTS curtidas (
        id {pk_auto},
        postagem_id INTEGER NOT NULL,
        usuario_id INTEGER NOT NULL,
        data_curtida TEXT NOT NULL,
        UNIQUE(postagem_id, usuario_id)
    )""")
    
    c.execute(f"""CREATE TABLE IF NOT EXISTS conhecimento_ia (
        id {pk_auto},
        pergunta TEXT NOT NULL UNIQUE,
        resposta TEXT NOT NULL,
        autor_id INTEGER,
        data_hora TEXT NOT NULL
    )""")
    
    conn.commit()
    conn.close()

init_db()

# ==============================================
# FUNÇÕES AUXILIARES
# ==============================================
def usuario_logado():
    return "usuario_id" in session

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ==============================================
# SISTEMA DNA — CONVERSÃO ATGC COMPLETA
# ==============================================
MAPA_BIN_DNA = {'00': 'A', '01': 'T', '10': 'G', '11': 'C'}
MAPA_DNA_BIN = {'A': '00', 'T': '01', 'G': '10', 'C': '11'}

def texto_para_dna(texto):
    bytes_texto = texto.encode('utf-8')
    bits = ''.join(f'{b:08b}' for b in bytes_texto)
    dna = ''.join(MAPA_BIN_DNA[bits[i:i+2]] for i in range(0, len(bits), 2))
    return dna

def dna_para_texto(dna_str):
    try:
        dna_str = dna_str.upper().strip().replace("\n", "").replace(" ", "")
        bits = ''.join(MAPA_DNA_BIN[c] for c in dna_str if c in MAPA_DNA_BIN)
        bytes_lista = bytearray(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))
        return bytes_lista.decode('utf-8')
    except Exception:
        return "ERRO: Sequência DNA inválida ou corrompida!"

@app.route("/dna", methods=["GET", "POST"])
def pagina_dna():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    
    resultado = ""
    tipo_operacao = ""
    
    if request.method == "POST":
        acao = request.form.get("acao")
        entrada = request.form.get("conteudo", "").strip()
        
        if acao == "codificar" and entrada:
            resultado = texto_para_dna(entrada)
            tipo_operacao = "DNA Gerado (ATGC)"
        elif acao == "decodificar" and entrada:
            resultado = dna_para_texto(entrada)
            tipo_operacao = "Texto Decodificado"
            
    return render_template_string('''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DNA Cripto — ATGC</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 p-6 max-w-3xl mx-auto">
    <a href="/plataforma" class="text-yellow-500 font-bold mb-4 inline-block">&larr; Voltar para Plataforma</a>
    <h1 class="text-3xl font-bold text-yellow-500 mb-6">SISTEMA DNA (ATGC)</h1>
    
    <div class="bg-slate-800 p-6 rounded-lg border border-yellow-500/30 mb-6">
        <form method="POST" class="space-y-4">
            <label class="block font-bold">Digite o texto ou código DNA (ATGC):</label>
            <textarea name="conteudo" rows="5" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white font-mono" placeholder="Insira seu texto ou sequência ATGC..." required></textarea>
            
            <div class="flex gap-4">
                <button type="submit" name="acao" value="codificar" class="flex-1 bg-yellow-600 text-black font-bold py-3 rounded-lg hover:bg-yellow-500">Converter para DNA (ATGC)</button>
                <button type="submit" name="acao" value="decodificar" class="flex-1 bg-green-600 text-white font-bold py-3 rounded-lg hover:bg-green-500">Decodificar de DNA</button>
            </div>
        </form>
    </div>

    {% if resultado %}
    <div class="bg-slate-800 p-6 rounded-lg border border-green-500/30">
        <h3 class="text-xl font-bold text-green-400 mb-2">{{tipo_operacao}}:</h3>
        <div class="bg-slate-900 p-4 rounded border border-slate-700 font-mono text-yellow-300 break-all max-h-60 overflow-y-auto">
            {{resultado}}
        </div>
        <form action="/baixar_dna" method="POST" class="mt-4">
            <input type="hidden" name="dna_texto" value="{{resultado}}">
            <button type="submit" class="bg-blue-600 text-white font-bold px-4 py-2 rounded-lg">Baixar Arquivo .BNJ</button>
        </form>
    </div>
    {% endif %}
</body>
</html>''', resultado=resultado, tipo_operacao=tipo_operacao)

@app.route("/baixar_dna", methods=["POST"])
def baixar_dna():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    dna_texto = request.form.get("dna_texto", "").strip()
    if not dna_texto:
        return "Nenhum conteúdo para salvar", 400
    
    conteudo = f"JNB-DNA-ATGC\nDATA:{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{dna_texto}"
    resp = make_response(conteudo)
    resp.headers["Content-Disposition"] = f"attachment; filename=documento_dna_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bnj"
    resp.headers["Content-Type"] = "application/octet-stream"
    return resp

# ==============================================
# INTELIGÊNCIA ARTIFICIAL — APRENDIZ
# ==============================================
CONHECIMENTO_PADRAO = {
    "brasil": "O Brasil foi descoberto em 22 de abril de 1500 por Pedro Álvares Cabral.",
    "quem e voce": "Eu sou a IA da JNB TECNOLOGIA, criada por Joao Bento da Silva.",
    "jogo de cartas": "Regra: Y->Y, A<->Z, B<->X, C<->G, D<->F, E->E.",
    "jogo bentinho": "Regra: 0<->0, 1<->9, 2<->8, 3<->7, 4<->6, 5<->5, 6<->4, 7<->3, 8<->2, 9<->1.",
    "oi": "Olá! Bem-vindo à JNB TECNOLOGIA! Como posso ajudar?",
    "ola": "Olá! Em que posso ser útil?"
}

@app.route("/ensinar_ia", methods=["GET", "POST"])
def ensinar_ia():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    msg = ""
    if request.method == "POST":
        pergunta = request.form.get("pergunta", "").strip().lower()
        resposta = request.form.get("resposta", "").strip()
        if pergunta and resposta:
            try:
                conn, db_type = get_db()
                c = conn.cursor()
                param = "%s" if db_type == "postgres" else "?"
                c.execute(f"INSERT INTO conhecimento_ia (pergunta, resposta, autor_id, data_hora) VALUES ({param}, {param}, {param}, {param})",
                          (pergunta, resposta, session["usuario_id"], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
                msg = "Conhecimento ensinado com sucesso!"
            except Exception:
                msg = "Essa pergunta já possui resposta no banco de dados."

    return render_template_string('''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ensinar IA — JNB</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 p-6 max-w-2xl mx-auto">
    <a href="/plataforma" class="text-yellow-500 font-bold mb-4 inline-block">&larr; Voltar para Plataforma</a>
    <h1 class="text-3xl font-bold text-yellow-500 mb-6">Ensinar Inteligência Artificial</h1>
    {% if msg %}<div class="bg-yellow-500/20 text-yellow-300 p-3 rounded mb-4">{{msg}}</div>{% endif %}
    
    <form method="POST" class="bg-slate-800 p-6 rounded-lg space-y-4 border border-slate-700">
        <div>
            <label class="block mb-1">Pergunta / Termo de busca:</label>
            <input type="text" name="pergunta" class="w-full bg-slate-900 p-3 rounded border border-slate-700 text-white" placeholder="ex: O que é a linguagem JNB?" required>
        </div>
        <div>
            <label class="block mb-1">Resposta da IA:</label>
            <textarea name="resposta" rows="4" class="w-full bg-slate-900 p-3 rounded border border-slate-700 text-white" placeholder="ex: A linguagem JNB é um sistema de criptografia e compilação..." required></textarea>
        </div>
        <button type="submit" class="w-full bg-yellow-500 text-black font-bold p-3 rounded hover:bg-yellow-400">Salvar Conhecimento</button>
    </form>
</body>
</html>''', msg=msg)

@app.route("/perguntar_ia", methods=["POST"])
def perguntar_ia():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    
    pergunta = request.form.get("pergunta", "").strip().lower()
    resposta_ia = ""
    
    for key, val in CONHECIMENTO_PADRAO.items():
        if key in pergunta:
            resposta_ia = val
            break
            
    if not resposta_ia:
        conn, db_type = get_db()
        c = conn.cursor()
        c.execute("SELECT resposta FROM conhecimento_ia")
        registros = c.fetchall()
        
        c.execute("SELECT pergunta, resposta FROM conhecimento_ia")
        for reg in c.fetchall():
            if reg["pergunta"] in pergunta or pergunta in reg["pergunta"]:
                resposta_ia = reg["resposta"]
                break
        conn.close()

    if not resposta_ia:
        resposta_ia = f"Ainda não sei a resposta para '{pergunta}'. Você pode me ensinar no menu 'Ensinar IA'!"

    session["ultima_resposta_ia"] = resposta_ia
    return redirect(url_for("plataforma"))

# ==============================================
# REDE SOCIAL / POSTAGENS PERMANENTES & CURTIDAS
# ==============================================
@app.route("/postar", methods=["POST"])
def postar():
    if not usuario_logado():
        return redirect(url_for("inicio"))
        
    texto = request.form.get("texto", "").strip()
    file = request.files.get("arquivo")
    filename = None
    
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        
    if texto or filename:
        conn, db_type = get_db()
        c = conn.cursor()
        param = "%s" if db_type == "postgres" else "?"
        c.execute(f"INSERT INTO postagens (usuario_id, texto, arquivo, data_postagem) VALUES ({param}, {param}, {param}, {param})",
                  (session["usuario_id"], texto, filename, datetime.now().strftime("%d/%m/%Y %H:%M")))
        conn.commit()
        conn.close()
        
    return redirect(url_for("plataforma"))

@app.route("/curtir/<int:post_id>", methods=["POST"])
def curtir(post_id):
    if not usuario_logado():
        return redirect(url_for("inicio"))
        
    conn, db_type = get_db()
    c = conn.cursor()
    param = "%s" if db_type == "postgres" else "?"
    
    try:
        c.execute(f"INSERT INTO curtidas (postagem_id, usuario_id, data_curtida) VALUES ({param}, {param}, {param})",
                  (post_id, session["usuario_id"], datetime.now().strftime("%d/%m/%Y %H:%M")))
        conn.commit()
    except Exception:
        # Se o usuário já curtiu, descurte
        c.execute(f"DELETE FROM curtidas WHERE postagem_id = {param} AND usuario_id = {param}",
                  (post_id, session["usuario_id"]))
        conn.commit()
    finally:
        conn.close()
        
    return redirect(url_for("plataforma"))

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# ==============================================
# JOGOS (BENTINHO & CARTAS)
# ==============================================
MAPA_BENTINHO = {'0':'0','1':'9','2':'8','3':'7','4':'6','5':'5','6':'4','7':'3','8':'2','9':'1'}
MAPA_CARTAS = {'Y':'Y','A':'Z','Z':'A','B':'X','X':'B','C':'G','G':'C','D':'F','F':'D','E':'E'}

@app.route("/jogar", methods=["POST"])
def jogar():
    if not usuario_logado():
        return redirect(url_for("inicio"))
        
    tipo_jogo = request.form.get("tipo_jogo")
    entrada = request.form.get("entrada", "").strip().upper()
    saida = ""
    
    if tipo_jogo == "bentinho":
        saida = ''.join(MAPA_BENTINHO.get(c, c) for c in entrada)
    elif tipo_jogo == "cartas":
        saida = ''.join(MAPA_CARTAS.get(c, c) for c in entrada)
        
    session["resultado_jogo"] = f"Entrada: {entrada} | Resultado: {saida}"
    return redirect(url_for("plataforma"))

# ==============================================
# AUTENTICAÇÃO E CADASTROS
# ==============================================
@app.route("/")
def inicio():
    if usuario_logado():
        return redirect(url_for("plataforma"))
    return render_template_string('''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JNB Tecnologia — Entrar</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 flex items-center justify-center min-h-screen p-4">
    <div class="bg-slate-800 p-8 rounded-xl border border-yellow-500/30 max-w-md w-full shadow-2xl">
        <h1 class="text-3xl font-bold text-center text-yellow-500 mb-2">JNB TECNOLOGIA</h1>
        <p class="text-center text-slate-400 mb-6">Plataforma & Rede Social Integrada</p>
        
        <form action="/login" method="POST" class="space-y-4">
            <div>
                <label class="block text-sm mb-1">E-mail:</label>
                <input type="email" name="email" class="w-full bg-slate-900 border border-slate-700 p-3 rounded text-white" required>
            </div>
            <div>
                <label class="block text-sm mb-1">Senha:</label>
                <input type="password" name="senha" class="w-full bg-slate-900 border border-slate-700 p-3 rounded text-white" required>
            </div>
            <button type="submit" class="w-full bg-yellow-500 text-black font-bold p-3 rounded hover:bg-yellow-400 transition">Entrar</button>
        </form>
        <p class="text-center text-sm mt-4 text-slate-400">Não tem conta? <a href="/cadastro" class="text-yellow-500 font-bold">Cadastre-se</a></p>
    </div>
</body>
</html>''')

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    msg = ""
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "").strip()
        
        if nome and email and senha:
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            dna_chave = texto_para_dna(f"{email}:{datetime.now().timestamp()}")
            
            conn, db_type = get_db()
            c = conn.cursor()
            param = "%s" if db_type == "postgres" else "?"
            try:
                c.execute(f"INSERT INTO usuarios (nome, email, senha_hash, dna_chave, data_cadastro) VALUES ({param}, {param}, {param}, {param}, {param})",
                          (nome, email, senha_hash, dna_chave, datetime.now().strftime("%d/%m/%Y")))
                conn.commit()
                conn.close()
                return redirect(url_for("inicio"))
            except Exception as e:
                msg = f"Erro ao cadastrar: E-mail já utilizado ou inválido. ({str(e)})"
                
    return render_template_string('''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JNB — Cadastro</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 flex items-center justify-center min-h-screen p-4">
    <div class="bg-slate-800 p-8 rounded-xl border border-yellow-500/30 max-w-md w-full shadow-2xl">
        <h1 class="text-2xl font-bold text-center text-yellow-500 mb-6">Criar Conta Permanente</h1>
        {% if msg %}<div class="bg-red-500/20 text-red-400 p-3 rounded mb-4 text-sm">{{msg}}</div>{% endif %}
        
        <form method="POST" class="space-y-4">
            <div>
                <label class="block text-sm mb-1">Nome Completo:</label>
                <input type="text" name="nome" class="w-full bg-slate-900 border border-slate-700 p-3 rounded text-white" required>
            </div>
            <div>
                <label class="block text-sm mb-1">E-mail:</label>
                <input type="email" name="email" class="w-full bg-slate-900 border border-slate-700 p-3 rounded text-white" required>
            </div>
            <div>
                <label class="block text-sm mb-1">Senha:</label>
                <input type="password" name="senha" class="w-full bg-slate-900 border border-slate-700 p-3 rounded text-white" required>
            </div>
            <button type="submit" class="w-full bg-yellow-500 text-black font-bold p-3 rounded hover:bg-yellow-400 transition">Finalizar Cadastro</button>
        </form>
        <p class="text-center text-sm mt-4 text-slate-400">Já possui conta? <a href="/" class="text-yellow-500 font-bold">Faça login</a></p>
    </div>
</body>
</html>''', msg=msg)

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email", "").strip()
    senha = request.form.get("senha", "").strip()
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    
    conn, db_type = get_db()
    c = conn.cursor()
    param = "%s" if db_type == "postgres" else "?"
    c.execute(f"SELECT id, nome, email FROM usuarios WHERE email = {param} AND senha_hash = {param}", (email, senha_hash))
    user = c.fetchone()
    conn.close()
    
    if user:
        session["usuario_id"] = user["id"]
        session["usuario_nome"] = user["nome"]
        return redirect(url_for("plataforma"))
    return "Credenciais inválidas. <a href='/'>Tentar novamente</a>"

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("inicio"))

# ==============================================
# PAINEL PRINCIPAL (PLATAFORMA & REDE SOCIAL)
# ==============================================
@app.route("/plataforma")
def plataforma():
    if not usuario_logado():
        return redirect(url_for("inicio"))
        
    conn, db_type = get_db()
    c = conn.cursor()
    
    # Carregar postagens com dados de usuários e contagem de curtidas
    query_posts = """
        SELECT p.id, p.texto, p.arquivo, p.data_postagem, u.nome,
        (SELECT COUNT(*) FROM curtidas c WHERE c.postagem_id = p.id) as total_curtidas,
        (SELECT COUNT(*) FROM curtidas c WHERE c.postagem_id = p.id AND c.usuario_id = {}) as curtiu_usuario
        FROM postagens p
        JOIN usuarios u ON p.usuario_id = u.id
        ORDER BY p.id DESC
    """.format(session["usuario_id"])
    
    c.execute(query_posts)
    postagens = c.fetchall()
    conn.close()

    res_ia = session.pop("ultima_resposta_ia", None)
    res_jogo = session.pop("resultado_jogo", None)

    return render_template_string('''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JNB TECNOLOGIA — Plataforma</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen">
    <header class="bg-slate-800 border-b border-yellow-500/30 p-4 sticky top-0 z-50">
        <div class="max-w-6xl mx-auto flex justify-between items-center">
            <h1 class="text-2xl font-bold text-yellow-500">JNB TECNOLOGIA</h1>
            <div class="flex items-center gap-4">
                <span>Olá, <strong>{{session.usuario_nome}}</strong></span>
                <a href="/logout" class="bg-red-600 text-white px-3 py-1 rounded text-sm font-bold hover:bg-red-500">Sair</a>
            </div>
        </div>
    </header>

    <main class="max-w-6xl mx-auto p-4 grid grid-cols-1 md:grid-cols-3 gap-6 mt-4">
        <div class="space-y-6">
            <div class="bg-slate-800 p-4 rounded-lg border border-slate-700">
                <h2 class="text-xl font-bold text-yellow-500 mb-3">Módulos Exclusivos</h2>
                <div class="space-y-2">
                    <a href="/dna" class="block bg-slate-900 p-3 rounded border border-yellow-500/20 hover:border-yellow-500 font-bold text-yellow-400">SISTEMA DNA (ATGC)</a>
                    <a href="/ensinar_ia" class="block bg-slate-900 p-3 rounded border border-slate-700 hover:border-yellow-500 font-bold text-slate-200">Ensinar a IA</a>
                </div>
            </div>

            <div class="bg-slate-800 p-4 rounded-lg border border-slate-700">
                <h2 class="text-xl font-bold text-yellow-500 mb-3">Assistente IA</h2>
                <form action="/perguntar_ia" method="POST" class="space-y-2">
                    <input type="text" name="pergunta" placeholder="Pergunte algo para a IA..." class="w-full bg-slate-900 border border-slate-700 p-2 rounded text-white" required>
                    <button type="submit" class="w-full bg-yellow-500 text-black font-bold p-2 rounded hover:bg-yellow-400">Perguntar</button>
                </form>
                {% if res_ia %}
                <div class="mt-3 bg-slate-900 p-3 rounded border border-yellow-500/30 text-sm text-yellow-300">
                    <strong>IA:</strong> {{res_ia}}
                </div>
                {% endif %}
            </div>

            <div class="bg-slate-800 p-4 rounded-lg border border-slate-700">
                <h2 class="text-xl font-bold text-yellow-500 mb-3">Jogos & Mapeamento</h2>
                <form action="/jogar" method="POST" class="space-y-2">
                    <select name="tipo_jogo" class="w-full bg-slate-900 border border-slate-700 p-2 rounded text-white">
                        <option value="bentinho">Jogo Bentinho (Números 0-9)</option>
                        <option value="cartas">Jogo de Cartas (Letras Y, A, B, C...)</option>
                    </select>
                    <input type="text" name="entrada" placeholder="Digite para converter..." class="w-full bg-slate-900 border border-slate-700 p-2 rounded text-white" required>
                    <button type="submit" class="w-full bg-slate-700 text-white font-bold p-2 rounded hover:bg-slate-600">Executar Código</button>
                </form>
                {% if res_jogo %}
                <div class="mt-3 bg-slate-900 p-3 rounded border border-slate-700 text-sm text-slate-300 font-mono">
                    {{res_jogo}}
                </div>
                {% endif %}
            </div>
        </div>

        <div class="md:col-span-2 space-y-6">
            <div class="bg-slate-800 p-4 rounded-lg border border-slate-700">
                <h2 class="text-lg font-bold text-yellow-500 mb-3">Criar Postagem Permanente</h2>
                <form action="/postar" method="POST" enctype="multipart/form-data" class="space-y-3">
                    <textarea name="texto" rows="3" placeholder="No que você está pensando?" class="w-full bg-slate-900 border border-slate-700 p-3 rounded text-white"></textarea>
                    <div class="flex items-center justify-between">
                        <input type="file" name="arquivo" class="text-sm text-slate-400">
                        <button type="submit" class="bg-yellow-500 text-black font-bold px-6 py-2 rounded hover:bg-yellow-400">Publicar</button>
                    </div>
                </form>
            </div>

            <div class="space-y-4">
                {% for post in postagens %}
                <div class="bg-slate-800 p-5 rounded-lg border border-slate-700 space-y-3">
                    <div class="flex justify-between items-center">
                        <span class="font-bold text-yellow-500">{{post.nome}}</span>
                        <span class="text-xs text-slate-500">{{post.data_postagem}}</span>
                    </div>
                    {% if post.texto %}
                    <p class="text-slate-200 whitespace-pre-line">{{post.texto}}</p>
                    {% endif %}
                    {% if post.arquivo %}
                        {% set ext = post.arquivo.rsplit('.', 1)[1].lower() %}
                        {% if ext in ['png', 'jpg', 'jpeg', 'gif'] %}
                        <img src="/uploads/{{post.arquivo}}" class="rounded-lg max-h-96 w-full object-cover border border-slate-700">
                        {% elif ext in ['mp4', 'mov', 'avi', 'webm'] %}
                        <video controls class="w-full rounded-lg max-h-96 border border-slate-700">
                            <source src="/uploads/{{post.arquivo}}">
                        </video>
                        {% endif %}
                    {% endif %}
                    <div class="pt-2 border-t border-slate-700 flex items-center justify-between">
                        <form action="/curtir/{{post.id}}" method="POST">
                            <button type="submit" class="flex items-center gap-2 text-sm font-bold {{ 'text-red-500' if post.curtiu_usuario else 'text-slate-400' }} hover:text-red-400">
                                &#10084; {{ post.total_curtidas }} {{ 'Curtida' if post.total_curtidas == 1 else 'Curtidas' }}
                            </button>
                        </form>
                    </div>
                </div>
                {% else %}
                <div class="text-center text-slate-500 py-8">Nenhuma postagem encontrada. Seja o primeiro a publicar!</div>
                {% endfor %}
            </div>
        </div>
    </main>
</body>
</html>''', postagens=postagens, res_ia=res_ia, res_jogo=res_jogo)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
