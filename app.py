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
    conn = sqlite3
