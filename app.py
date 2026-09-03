 # ================================================== 
# © 2026 JNB TECNOLOGIA — VERSÃO DEFINITIVA
# REDE · JOGOS BENTINHO + CARTAS · IA APRENDIZ · DNA CRIPTO
# CADASTRO PERMANENTE · POSTAGENS PERMANENTES · PORTA 5000
# TUDO INTEGRADO · SEM FALTAR NADA · 100% FUNCIONAL
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

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4", "mov", "avi", "webm", "bnj"}
BANCO_DADOS = "jnb_definitiva.db"

EMAIL_DONO = "seu_email_aqui@seu_dominio.com"
SENHA_MESTRA_ACESSO = "JNB@2026#DONO"


# ==============================================
# INICIALIZACAO DO BANCO DE DADOS
# ==============================================
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
    c.execute("""CREATE TABLE IF NOT EXISTS conhecimento_ia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pergunta TEXT NOT NULL UNIQUE,
        resposta TEXT NOT NULL,
        autor_id INTEGER,
        data_hora TEXT NOT NULL
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


# ==============================================
# FUNCOES AUXILIARES
# ==============================================
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


def usuario_logado():
    return "usuario_id" in session


# ==============================================
# INTELIGENCIA ARTIFICIAL — BASE DE CONHECIMENTO
# ==============================================
def carregar_conhecimento():
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("SELECT pergunta, resposta FROM conhecimento_ia")
    dados = c.fetchall()
    conn.close()
    return {p.lower(): r for p, r in dados}


CONHECIMENTO_PADRAO = {
    "brasil": "O Brasil foi descoberto em 22 de abril de 1500 por Pedro Álvares Cabral.",
    "quem e voce": "Eu sou a IA da JNB TECNOLOGIA, criada por Joao Bento da Silva.",
    "jogo de cartas": "Regra: Y->Y, A<->Z, B<->X, C<->G, D<->F, E->E.",
    "jogo bentinho": "Regra: 0<->0, 1<->9, 2<->8, 3<->7, 4<->6, 5<->5, 6<->4, 7<->3, 8<->2, 9<->1.",
    "dna": "Cada usuario tem sua chave unica. Use para criptografar e salvar como .bnj!",
    "oi": "Ola! Bem-vindo a JNB TECNOLOGIA! Como posso ajudar?",
    "ola": "Ola! Em que posso ser util?"
}


def responder_ia(pergunta):
    p = pergunta.lower().strip()
    base = carregar_conhecimento()
    for chave in base:
        if chave in p or p in chave:
            return base[chave]
    for chave, resp in CONHECIMENTO_PADRAO.items():
        if chave in p or p in chave:
            return resp
    return f"Ainda nao aprendi isso! Voce pode me ensinar na aba 'Ensinar IA'! Pergunta: \"{pergunta}\""


@app.route("/ensinar_ia", methods=["GET", "POST"])
def ensinar_ia():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    msg = ""
    if request.method == "POST":
        pergunta = request.form.get("pergunta", "").strip()
        resposta = request.form.get("resposta", "").strip()
        if pergunta and resposta:
            try:
                conn = sqlite3.connect(BANCO_DADOS)
                c = conn.cursor()
                c.execute("INSERT INTO conhecimento_ia (pergunta, resposta, autor_id, data_hora) VALUES (?, ?, ?, ?)",
                          (pergunta, resposta, session["usuario_id"], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
                msg = "Aprendi! Obrigado por me ensinar!"
            except sqlite3.IntegrityError:
                msg = "Ja tenho essa pergunta cadastrada!"
        else:
            msg = "Preencha pergunta e resposta!"
    return render_template_string('''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ensinar IA</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: linear-gradient(180deg, #0f172a, #1e293b); color: #e2e8f0; min-height: 100vh; }
    </style>
</head>
<body class="p-6 max-w-2xl mx-auto">
    <a href="/plataforma" class="text-yellow-500 mb-4 inline-block">Voltar</a>
    <h1 class="text-3xl font-bold text-yellow-500 mb-6">ENSINAR A INTELIGENCIA ARTIFICIAL</h1>
    {% if msg %}
    <div class="p-4 rounded-lg mb-6 font-bold {{'bg-green-900/50 text-green-400' if 'Aprendi' in msg else 'bg-yellow-900/50 text-yellow-400'}}">
        {{msg}}
    </div>
    {% endif %}
    <form method="POST" class="bg-gray-800 p-6 rounded-lg border border-yellow-500/30">
        <label class="block mb-2 font-bold">Pergunta ou palavra-chave:</label>
        <input type="text" name="pergunta" class="w-full p-3 bg-gray-900 border border-gray-700 rounded-lg mb-4 text-white" placeholder="Ex: capital do Brasil" required>
        <label class="block mb-2 font-bold">Resposta que a IA deve aprender:</label>
        <textarea name="resposta" class="w-full p-3 bg-gray-900 border border-gray-700 rounded-lg mb-4 text-white" rows="4" placeholder="Digite a resposta correta..." required></textarea>
        <button type="submit" class="bg-yellow-600 text-black font-bold px-6 py-3 rounded-lg">Salvar na Base de Conhecimento</button>
    </form>
    <p class="mt-6 text-gray-400 text-sm">Cada novo ensinamento fica salvo para todos os usuarios. A IA aprende e melhora cada dia!</p>
</body>
</html>''', msg=msg)


@app.route("/responder_ia", methods=["POST"])
def responder_ia_rota():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    pergunta = request.form.get("pergunta", "").strip()
    if not pergunta:
        return "Digite uma pergunta!"
    resposta = responder_ia(pergunta)
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("INSERT INTO conversas_ia (usuario_id, pergunta, resposta, data_hora) VALUES (?, ?, ?, ?)",
              (session["usuario_id"], pergunta, resposta, data_hora))
    conn.commit()
    conn.close()
    return resposta


# ==============================================
# SISTEMA DNA — CRIPTOGRAFIA E DESCRIPTOGRAFIA
# ==============================================
def criptografar(texto, chave):
    chave_bytes = base64.b64decode(chave)
    texto_bytes = texto.encode("utf-8")
    resultado = bytearray()
    for i, b in enumerate(texto_bytes):
        resultado.append(b ^ chave_bytes[i % len(chave_bytes)])
    return base64.b64encode(resultado).decode("utf-8")


def descriptografar(dados_b64, chave):
    try:
        chave_bytes = base64.b64decode(chave)
        dados_bytes = base64.b64decode(dados_b64)
        resultado = bytearray()
        for i, b in enumerate(dados_bytes):
            resultado.append(b ^ chave_bytes[i % len(chave_bytes)])
        return resultado.decode("utf-8")
    except:
        return "ERRO: Chave invalida ou dados corrompidos!"


@app.route("/dna_criptografar", methods=["POST"])
def dna_criptografar():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    texto = request.form.get("texto_cripto", "").strip()
    if not texto:
        return "Digite o texto para criptografar!"
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("SELECT dna_chave FROM usuarios WHERE id = ?", (session["usuario_id"],))
    chave = c.fetchone()[0]
    conn.close()
    return criptografar(texto, chave)


@app.route("/dna_descriptografar", methods=["POST"])
def dna_descriptografar():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    dados = request.form.get("dados_cripto", "").strip()
    chave_usuario = request.form.get("chave_manual", "").strip()
    if not dados:
        return "Cole o texto criptografado!"
    if not chave_usuario:
        conn = sqlite3.connect(BANCO_DADOS)
        c = conn.cursor()
        c.execute("SELECT dna_chave FROM usuarios WHERE id = ?", (session["usuario_id"],))
        chave_usuario = c.fetchone()[0]
        conn.close()
    return descriptografar(dados, chave_usuario)


@app.route("/baixar_dna", methods=["POST"])
def baixar_dna():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    dna_texto = request.form.get("dna_texto", "").strip()
    if not dna_texto:
        return "Nenhum conteudo para salvar", 400
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("SELECT dna_chave FROM usuarios WHERE id = ?", (session["usuario_id"],))
    chave = c.fetchone()[0]
    conn.close()
    conteudo = f"JNB-DNA-ENCRYPTED\nCHAVE:{chave}\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{dna_texto}"
    resp = make_response(conteudo)
    resp.headers["Content-Disposition"] = f"attachment; filename=documento_dna_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bnj"
    resp.headers["Content-Type"] = "application/octet-stream"
    return resp


# ==============================================
# JOGO BENTINHO — SEGREDO DOS NUMEROS
# ==============================================
@app.route("/jogo_bentinho", methods=["GET", "POST"])
def jogo_bentinho():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    TABELA = {'0': '0', '1': '9', '2': '8', '3': '7', '4': '6', '5': '5', '6': '4', '7': '3', '8': '2', '9': '1'}

    def inverter(num):
        return "".join(TABELA[d] for d in num)

    if "bent_fase" not in session:
        session["bent_fase"] = 1
    if "bent_pontos" not in session:
        session["bent_pontos"] = 0
    fase = session["bent_fase"]
    PTS = {1: 250000, 2: 2500000, 3: 25000000, 4: 1000000000}
    TAM = {1: 3, 2: 6, 3: 8, 4: 9}

    if "bent_num" not in session or session.get("bent_fase_atual") != fase:
        session["bent_num"] = "".join(random.choice("0123456789") for _ in range(TAM[fase]))
        session["bent_alvo"] = inverter(session["bent_num"])
        session["bent_fase_atual"] = fase

    msg = ""
    if request.method == "POST":
        if request.form.get("acao") == "reiniciar":
            session["bent_fase"] = 1
            session["bent_pontos"] = 0
            session.pop("bent_num", None)
            return redirect(url_for("jogo_bentinho"))
        resp = request.form.get("resposta", "").strip()
        if resp == session["bent_alvo"]:
            pts = PTS[fase]
            session["bent_pontos"] += pts
            msg = f"ACERTOU! +{pts} PONTOS!"
            try:
                conn = sqlite3.connect(BANCO_DADOS)
                c = conn.cursor()
                c.execute("UPDATE usuarios SET pontos = pontos + ? WHERE id = ?", (pts, session["usuario_id"]))
                conn.commit()
                conn.close()
            except:
                pass
            if fase < 4:
                session["bent_fase"] += 1
                session.pop("bent_num", None)
            else:
                msg = "PARABENS! 1.000.000.000 DE PONTOS! VOCE VENCEU!"
                session["bent_fase"] = 1
                session.pop("bent_num", None)
        else:
            msg = "Errou! Tente de novo."

    return render_template_string('''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Segredo dos Numeros</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: linear-gradient(180deg, #0f172a, #1e293b); color: #e2e8f0; min-height: 100vh; }
    </style>
</head>
<body class="flex items-center justify-center p-4">
    <div class="bg-gray-800 p-8 rounded-xl border-2 border-yellow-500/50 max-w-lg w-full">
        <h1 class="text-4xl font-bold text-yellow-500 text-center mb-2">SEGREDO DOS NUMEROS</h1>
        <p class="text-center text-gray-400 mb-6">Fase {{fase}}/4 · Pontos: {{pontos}}</p>
        {% if msg %}
        <div class="text-center p-4 rounded-lg mb-6 text-lg font-bold {{'bg-green-900/50 text-green-400' if 'ACERTOU' in msg or 'PARABENS' in msg else 'bg-red-900/50 text-red-400'}}">
            {{msg}}
        </div>
        {% endif %}
        <div class="bg-gray-900 border-2 border-yellow-500/40 rounded-lg p-6 text-center mb-6">
            <p class="text-gray-400 mb-2">Numero:</p>
            <p class="text-5xl font-mono text-yellow-400 font-bold tracking-widest">{{numero}}</p>
        </div>
        <form method="POST" class="space-y-4">
            <input type="text" name="resposta" placeholder="Digite o numero invertido..." class="w-full bg-gray-900 border-2 border-yellow-500 rounded-lg text-center text-2xl text-yellow-400 p-3 font-mono" required>
            <div class="flex gap-3">
                <button type="submit" class="flex-1 bg-yellow-600 text-black font-bold py-3 rounded-lg text-lg">Decifrar</button>
                <button type="submit" name="acao" value="reiniciar" class="bg-gray-600 text-white px-6 py-3 rounded-lg">Reiniciar</button>
            </div>
        </form>
        <p class="text-center mt-6"><a href="/plataforma" class="text-yellow-500">Voltar</a></p>
    </div>
</body>
</html>''', fase=fase, pontos=session["bent_pontos"], numero=session["bent_num"], msg=msg)


# ==============================================
# JOGO DAS CARTAS — REGRA DEFINITIVA
# ==============================================
@app.route("/jogo_cartas", methods=["GET", "POST"])
def jogo_cartas():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    REGRAS = {'Y': 'Y', 'A': 'Z', 'Z': 'A', 'B': 'X', 'X': 'B', 'C': 'G', 'G': 'C', 'D': 'F', 'F': 'D', 'E': 'E'}
    CARTAS = ['Y', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'X', 'Z']
    if "cartas_fase" not in session:
        session["cartas_fase"] = 1
    if "cartas_pontos" not in session:
        session["cartas_pontos"] = 0
    fase = session["cartas_fase"]
    pontos = session["cartas_pontos"]
    qtd = {1: 3, 2: 6, 3: 8, 4: 9}[fase]
    valor = {1: 100, 2: 300, 3: 500, 4: 1000}[fase]

    if "cartas_alvo" not in session or len(session.get("cartas_alvo", [])) != qtd:
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
                msg = "Selecione todas as cartas!"
            else:
                correta = [REGRAS[c] for c in alvo]
                if resposta == correta:
                    pontos += valor
                    session["cartas_pontos"] = pontos
                    msg = f"ACERTOU! +{valor} PONTOS!"
                    try:
                        conn = sqlite3.connect(BANCO_DADOS)
                        c = conn.cursor()
                        c.execute("UPDATE usuarios SET pontos = pontos + ? WHERE id = ?", (valor, session["usuario_id"]))
                        conn.commit()
                        conn.close()
                    except:
                        pass
                    if fase < 4:
                        session["cartas_fase"] += 1
                        session.pop("cartas_alvo", None)
                    else:
                        msg = "PARABENS! VOCE VENCEU TODAS AS FASES!"
                        session["cartas_fase"] = 1
                        session.pop("cartas_alvo", None)
                else:
                    msg = "Errou! Tente de novo."
                    session["cartas_resposta"] = []

    alvo_html = "".join([f"<span style='background:#f59e0b;color:black;padding:12px 18px;border-radius:8px;margin:5px;font-size:24px;font-weight:bold;'>{c}</span>" for c in alvo])
    resp_html = "".join([f"<span style='background:#22c55e;color:black;padding:12px 18px;border-radius:8px;margin:5px;font-size:24px;font-weight:bold;'>{c}</span>" for c in resposta]) if resposta else "<p style='color:#94a3b8;'>Clique nas cartas...</p>"
    disp_html = "".join([f"<button type='submit' name='selecionar' value='{c}' style='background:#33415e;color:white;padding:12px 18px;border-radius:8px;margin:5px;font-size:24px;font-weight:bold;border:2px solid #f59e0b;cursor:pointer;'>{c}</button>" for c in CARTAS])

    return render_template_string(f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jogo das Cartas</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background: linear-gradient(180deg, #0f172a, #1e293b); color: #e2e8f0; min-height: 100vh; }}
    </style>
</head>
<body class="p-6 max-w-2xl mx-auto">
    <a href="/plataforma" class="text-yellow-500">Voltar</a>
    <h1 class="text-4xl font-bold text-yellow-500 text-center my-6">JOGO DAS CARTAS</h1>
    <p class="text-center text-lg mb-4">Fase {fase}/4 · Pontos: {pontos}</p>
    {f'<div class="text-center p-3 rounded-lg mb-4 text-lg font-bold {"bg-green-900/50 text-green-400" if "ACERTOU" in msg or "PARABENS" in msg else "bg-red-900/50 text-red-400"}">{msg}</div>' if msg else ''}
    <div class="bg-gray-800 p-5 rounded-lg border border-yellow-500/30 mb-5">
        <p class="text-center mb-3 text-gray-400">Cartas Alvo:</p>
        <div class="flex flex-wrap justify-center">{alvo_html}</div>
    </div>
    <div class="bg-gray-800 p-5 rounded-lg border border-green-500/30 mb-5">
        <p class="text-center mb-3 text-gray-400">Sua Resposta (transforme cada carta):</p>
        <div class="flex flex-wrap justify-center">{resp_html}</div>
    </div>
    <form method="POST" class="bg-gray-800 p-5 rounded-lg border border-yellow-500/30 mb-5">
        <p class="text-center mb-3 text-gray-400">Selecione as cartas corretas:</p>
        <div class="flex flex-wrap justify-center">{disp_html}</div>
    </form>
    <div class="flex gap-3 justify-center">
        <form method="POST"><button type="submit" name="verificar" class="bg-green-600 text-white font-bold px-6 py-3 rounded-lg">Verificar</button></form>
        <form method="POST"><button type="submit" name="nova" class="bg-yellow-600 text-black font-bold px-6 py-3 rounded-lg">Novas Cartas</button></form>
    </div>
    <div class="mt-6 bg-gray-800 p-4 rounded-lg border border-gray-600">
        <p class="text-center text-gray-400 text-sm"><strong>Regra:</strong> Y->Y, A<->Z, B<->X, C<->G, D<->F, E->E</p>
    </div>
</body>
</html>""")


# ==============================================
# SISTEMA DE AUTENTICACAO
# ==============================================
@app.route("/")
def inicio():
    if usuario_logado():
        return redirect(url_for("plataforma"))
    return render_template_string("""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JNB TECNOLOGIA</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, sans-serif; }
        body { background: linear-gradient(180deg, #0f172a, #1e293b); color: #e2e8f0; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .caixa { background: rgba(15,23,42,0.8); padding: 40px; border-radius: 12px; border: 1px solid #f59e0b; width: 90%; max-width: 400px; }
        h1 { color: #f59e0b; text-align: center; margin-bottom: 30px; }
        input { width: 100%; padding: 12px; margin: 8px 0; background: #020617; border: 1px solid #334155; color: white; border-radius: 6px; }
        button { width: 100%; padding: 12px; background: #f59e0b; color: #1e1b16; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
        .link { text-align: center; margin-top: 15px; font-size: 14px; color: #94a3b8; }
        .link a { color: #f59e0b; text-decoration: none; }
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
        <div class="link">Nao tem conta? <a href="/cadastrar">Cadastre-se — PERMANENTE</a></div>
    </div>
</body>
</html>""")


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
                c.execute("INSERT INTO usuarios (nome, email, senha_hash, dna_chave, data_cadastro) VALUES (?, ?, ?, ?, ?)",
                          (nome, email, senha_hash, dna_chave, data_cad))
                conn.commit()
                usuario_id = c.lastrowid
                conn.close()
                session["usuario_id"] = usuario_id
                session["nome_usuario"] = nome
                return redirect(url_for("plataforma"))
            except sqlite3.IntegrityError:
                return '<div style="text-align:center;padding:50px;background:#0f172a;color:white;"><h2 style="color:red;">E-mail ja cadastrado!</h2><a href="/cadastrar" style="color:#f59e0b;">Voltar</a></div>'
    return render_template_string("""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cadastrar — JNB TECNOLOGIA</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, sans-serif; }
        body { background: linear-gradient(180deg, #0f172a, #1e293b); color: #e2e8f0; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .caixa { background: rgba(15,23,42,0.8); padding: 40px; border-radius: 12px; border: 1px solid #f59e0b; width: 90%; max-width: 400px; }
        h1 { color: #f59e0b; text-align: center; margin-bottom: 30px; }
        input { width: 100%; padding: 12px; margin: 8px 0; background: #020617; border: 1px solid #334155; color: white; border-radius: 6px; }
        button { width: 100%; padding: 12px; background: #f59e0b; color: #1e1b16; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
        .link { text-align: center; margin-top: 15px; font-size: 14px; color: #94a3b8; }
        .link a { color: #f59e0b; text-decoration: none; }
    </style>
</head>
<body>
    <div class="caixa">
        <h1>CADASTRO PERMANENTE</h1>
        <form method="POST">
            <input type="text" name="nome" placeholder="Seu nome" required>
            <input type="email" name="email" placeholder="E-mail" required>
            <input type="password" name="senha" placeholder="Senha" required>
            <button type="submit">Cadastrar — Para Sempre</button>
        </form>
        <div class="link">Ja tem conta? <a href="/">Entrar</a></div>
    </div>
</body>
</html>""")


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
    return '<div style="text-align:center;padding:50px;background:#0f172a;color:white;"><h2 style="color:red;">E-mail ou senha invalidos!</h2><a href="/" style="color:#f59e0b;font-size:18px;">Voltar</a></div>'


@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("inicio"))


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ==============================================
# AREA PRIVADA DO DONO
# ==============================================
@app.route("/area_privada", methods=["GET", "POST"])
def area_privada():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    if not eh_dono():
        return '<div style="text-align:center;padding:50px;background:#0f172a;color:white;"><h2 style="color:red;">ACESSO NEGADO</h2><a href="/plataforma" style="color:#f59e0b;">Voltar</a></div>'
    if request.method == "POST":
        if request.form.get("senha_mestra") == SENHA_MESTRA_ACESSO:
            return redirect(url_for("painel_dono"))
        return '<div style="text-align:center;padding:50px;background:#0f172a;color:white;"><h2 style="color:red;">Senha incorreta!</h2><a href="/area_privada" style="color:#f59e0b;">Tentar novamente</a></div>'
    return render_template_string('''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Area Privada</title>
    <style>
        body { background: linear-gradient(180deg, #0f172a, #1e293b); color: white; min-height: 100vh; display: flex; align-items: center; justify-content: center; font-family: Arial, sans-serif; }
        .caixa { background: rgba(15,23,42,0.9); padding: 40px; border-radius: 12px; border: 2px solid #f59e0b; max-width: 400px; width: 90%; text-align: center; }
        h1 { color: #f59e0b; margin-bottom: 20px; }
        input { width: 100%; padding: 12px; margin: 8px 0; background: #020617; border: 1px solid #334155; color: white; border-radius: 6px; }
        button { width: 100%; padding: 12px; background: #f59e0b; color: black; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
        a { color: #f59e0b; text-decoration: none; display: block; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="caixa">
        <h1>AREA PRIVADA</h1>
        <p style="margin-bottom:20px;">Confirme a senha mestra</p>
        <form method="POST">
            <input type="password" name="senha_mestra" placeholder="Senha Mestra" required>
            <button type="submit">Desbloquear</button>
        </form>
        <a href="/plataforma">Voltar</a>
    </div>
</body>
</html>''')


@app.route("/painel_dono")
def painel_dono():
    if not usuario_logado() or not eh_dono():
        return redirect(url_for("inicio"))
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM usuarios")
    total_usuarios = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM postagens")
    total_postagens = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM conhecimento_ia")
    total_conhecimento = c.fetchone()[0]
    conn.close()
    return render_template_string(f'''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel do Dono</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background: linear-gradient(180deg, #0f172a, #1e293b); color: #e2e8f0; min-height: 100vh; }}
    </style>
</head>
<body class="p-6 max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold text-yellow-500 mb-6">PAINEL DO DONO</h1>
    <a href="/plataforma" class="text-yellow-500 mb-4 inline-block">Voltar</a>
    <div class="grid grid-cols-3 gap-4">
        <div class="bg-gray-800 p-4 rounded-lg border border-yellow-500/30">
            <p class="text-gray-400">Total de Usuarios</p>
            <p class="text-2xl font-bold text-yellow-500">{total_usuarios}</p>
        </div>
        <div class="bg-gray-800 p-4 rounded-lg border border-yellow-500/30">
            <p class="text-gray-400">Total de Postagens</p>
            <p class="text-2xl font-bold text-yellow-500">{total_postagens}</p>
        </div>
        <div class="bg-gray-800 p-4 rounded-lg border border-yellow-500/30">
            <p class="text-gray-400">Conhecimento da IA</p>
            <p class="text-2xl font-bold text-yellow-500">{total_conhecimento}</p>
        </div>
    </div>
</body>
</html>''')


# ==============================================
# PLATAFORMA PRINCIPAL — REDE SOCIAL + TODAS AS ABAS
# ==============================================
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
        pid = request.args.get("curtir")
        conn = sqlite3.connect(BANCO_DADOS)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO curtidas (usuario_id, postagem_id) VALUES (?, ?)", (usuario_id, pid))
        except sqlite3.IntegrityError:
            c.execute("DELETE FROM curtidas WHERE usuario_id = ? AND postagem_id = ?", (usuario_id, pid))
        conn.commit()
        conn.close()
        return redirect(url_for("plataforma") + "#post-" + pid)

    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("SELECT nome, pontos, dna_chave, email FROM usuarios WHERE id = ?", (usuario_id,))
    usuario_dados = c.fetchone()
    if not usuario_dados:
        conn.close()
        session.clear()
        return redirect(url_for("inicio"))
    nome_usuario, total_pontos, dna_chave, email_usuario = usuario_dados

    c.execute("""SELECT p.id, p.texto, p.arquivo, p.data_postagem, u.nome,
               (SELECT COUNT(*) FROM curtidas c WHERE c.postagem_id = p.id) as total_curtidas,
               EXISTS(SELECT 1 FROM curtidas c WHERE c.postagem_id = p.id AND c.usuario_id = ?) as curtiu
               FROM postagens p JOIN usuarios u ON p.usuario_id = u.id ORDER BY p.data_postagem DESC""", (usuario_id,))
    postagens = c.fetchall()
    conn.close()

    posts_html = ""
    for p in postagens:
        pid, texto, arquivo, data, autor, curtidas, curtiu = p
        posts_html += f'''<div id="post-{pid}" class="bg-gray-800 p-4 rounded-lg border border-yellow-500/30 mb-4">
            <h4 class="font-bold text-yellow-400">{autor}</h4>
            <p class="text-sm text-gray-400">{data}</p>
            {f'<p class="my-3 whitespace-pre-wrap">{texto}</p>' if texto else ''}'''
        if arquivo:
            ext = arquivo.split(".")[-1].lower()
            if ext in ["jpg", "jpeg", "png", "gif"]:
                posts_html += f'<img src="/uploads/{arquivo}" class="max-w-full rounded-lg my-3">'
            elif ext in ["mp4", "mov", "avi", "webm"]:
                posts_html += f'<video controls class="max-w-full rounded-lg my-3"><source src="/uploads/{arquivo}" type="video/mp4"></video>'
        posts_html += f'''<div class="mt-3 pt-3 border-t border-gray-700">
            <a href="/plataforma?curtir={pid}#post-{pid}" class="text-{'red' if curtiu else 'gray'}-400">
                {curtidas} Curtida{'s' if curtidas != 1 else ''}
            </a>
        </div></div>'''
    
    if not posts_html:
        posts_html = '<p class="text-center text-gray-500 py-10">Ainda nao ha postagens. Seja o primeiro!</p>'

    botao_admin = f'<a href="/area_privada" class="bg-red-600 text-white px-4 py-2 rounded-lg text-sm ml-2">AREA PRIVADA</a>' if email_usuario.strip().lower() == EMAIL_DONO.lower() else ""

    return render_template_string(f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plataforma — JNB TECNOLOGIA</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-gray-100 min-h-screen">
    <div class="container mx-auto px-4 py-6 max-w-4xl">
        <div class="flex flex-wrap justify-between items-center border-b border-gray-700 pb-4 mb-6">
            <div>
                <h1 class="text-2xl font-bold text-yellow-500">JNB TECNOLOGIA</h1>
                <p class="text-gray-400">Bem-vindo, {nome_usuario}!</p>
            </div>
            <div class="text-right">
                <p class="text-sm text-gray-400">Pontos: <span class="text-xl font-bold text-yellow-500">{total_pontos}</span></p>
                <a href="/sair" class="text-red-400 text-sm ml-2">Sair</a> {botao_admin}
            </div>
        </div>

        <div class="flex flex-wrap gap-2 mb-6 border-b border-gray-700 pb-2">
            <a href="/plataforma" class="bg-yellow-600 text-black px-4 py-2 rounded-t-lg font-bold">Rede Social</a>
            <a href="/jogo_bentinho" class="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-t-lg">Jogo Bentinho</a>
            <a href="/jogo_cartas" class="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-t-lg">Jogo Cartas</a>
            <a href="/ensinar_ia" class="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-t-lg">Ensinar IA</a>
        </div>

        <div class="bg-gray-800 p-4 rounded-lg border border-yellow-500/30 mb-6">
            <form method="POST" enctype="multipart/form-data">
                <textarea name="texto_post" class="w-full bg-gray-900 p-3 rounded-lg border border-gray-700 text-white mb-3" placeholder="O que voce esta pensando?"></textarea>
                <div class="flex justify-between items-center">
                    <input type="file" name="arquivo" class="text-sm text-gray-400">
                    <button type="submit" class="bg-yellow-600 text-black font-bold px-6 py-2 rounded-lg">Publicar</button>
                </div>
            </form>
        </div>

        <div>
            {posts_html}
        </div>
    </div>
</body>
</html>""")


# PORTA E EXECUÇÃO
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
