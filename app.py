 import os
import random
import sqlite3
from datetime import datetime
from flask import Flask, request, session, redirect, url_for, make_response, render_template_string, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "chave_secreta_super_segura_jnb")
BANCO_DADOS = "plataforma.db"

# ==============================================================================
# CONFIGURAÇÃO INICIAL DO BANCO DE DADOS (Executa ao iniciar o app)
# ==============================================================================
def inicializar_banco():
    with sqlite3.connect(BANCO_DADOS) as conn:
        c = conn.cursor()
        # Tabela de Usuários (Pontos integrados com o Jogo do Bentinho)
        c.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                pontos INTEGER DEFAULT 0
            )
        """)
        # Tabela da Rede Social (Postagens da comunidade)
        c.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                conteudo TEXT NOT NULL,
                data_criacao TEXT NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)
        conn.commit()

inicializar_banco()

# Helper para checar se a sessão está ativa
def usuario_logado():
    return "usuario_id" in session

# ==============================================================================
# ROTAS DE AUTENTICAÇÃO BASE E TELA INICIAL
# ==============================================================================
@app.route("/")
def inicio():
    if usuario_logado():
        return redirect(url_for("plataforma"))
    return render_template_string("""
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="UTF-8"><title>Acesso - JNB</title>
            <script src="https://tailwindcss.com"></script>
        </head>
        <body class="bg-slate-950 text-slate-100 min-h-screen flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-800 p-8 rounded-xl max-w-sm w-full text-center space-y-4">
                <h1 class="text-3xl font-bold tracking-tight text-emerald-400">PLATAFORMA JNB</h1>
                <p class="text-sm text-slate-400">Faça login para acessar a rede, o painel de DNA e os jogos.</p>
                <form action="/login_teste" method="POST" class="space-y-3">
                    <input type="text" name="usuario" placeholder="Nome de usuário" class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-center" required>
                    <button type="submit" class="w-full bg-emerald-600 hover:bg-emerald-500 font-bold py-2 rounded-lg transition">Entrar / Criar Conta de Teste</button>
                </form>
            </div>
        </body>
        </html>
    """)

@app.route("/login_teste", methods=["POST"])
def login_teste():
    usuario = request.form.get("usuario", "").strip()
    if not usuario:
        return redirect(url_for("inicio"))
    
    with sqlite3.connect(BANCO_DADOS) as conn:
        c = conn.cursor()
        c.execute("SELECT id, pontos FROM usuarios WHERE usuario = ?", (usuario,))
        user = c.fetchone()
        if not user:
            c.execute("INSERT INTO usuarios (usuario, senha, pontos) VALUES (?, '1234', 0)", (usuario,))
            conn.commit()
            usuario_id = c.lastrowid
        else:
            usuario_id = user[0]
            
    session["usuario_id"] = usuario_id
    session["usuario_nome"] = usuario
    return redirect(url_for("plataforma"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("inicio"))

# ==============================================================================
# PAINEL CENTRAL DA PLATAFORMA
# ==============================================================================
@app.route("/plataforma")
def plataforma():
    if not usuario_logado():
        return redirect(url_for("inicio"))
        
    with sqlite3.connect(BANCO_DADOS) as conn:
        c = conn.cursor()
        c.execute("SELECT pontos FROM usuarios WHERE id = ?", (session["usuario_id"],))
        pontos = c.fetchone()[0]

    return render_template_string(f"""
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="UTF-8"><title>Plataforma Principal</title>
            <script src="https://tailwindcss.com"></script>
        </head>
        <body class="bg-slate-950 text-slate-100 min-h-screen p-6">
            <div class="max-w-4xl mx-auto space-y-8">
                <header class="flex justify-between items-center border-b border-slate-800 pb-4">
                    <div>
                        <h1 class="text-2xl font-bold">Olá, <span class="text-emerald-400">{session["usuario_nome"]}</span></h1>
                        <p class="text-xs text-slate-400">Seus Pontos Acumulados: <span class="text-yellow-400 font-bold">{pontos:,}</span></p>
                    </div>
                    <a href="/logout" class="bg-red-950 hover:bg-red-900 border border-red-800 text-red-400 px-4 py-2 rounded-lg text-sm transition">Sair</a>
                </header>
                
                <main class="grid md:grid-cols-3 gap-6">
                    <div class="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-3">
                        <h2 class="text-xl font-bold text-cyan-400">💬 Rede Social</h2>
                        <p class="text-sm text-slate-400">Interaja com a comunidade global da plataforma, envie ideias e compartilhe atualizações em tempo real.</p>
                        <a href="/rede_social" class="block text-center bg-cyan-700 hover:bg-cyan-600 font-bold py-2 rounded-lg text-sm transition">Entrar no Feed</a>
                    </div>
                    
                    <div class="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-3">
                        <h2 class="text-xl font-bold text-emerald-400">🧬 Codificador DNA</h2>
                        <p class="text-sm text-slate-400">Converta arquivos de texto simples e segredos em cadeias biológicas artificiais baseadas nos nucleotídeos ATGC.</p>
                        <a href="/dna_painel" class="block text-center bg-emerald-700 hover:bg-emerald-600 font-bold py-2 rounded-lg text-sm transition">Abrir Laboratório</a>
                    </div>

                    <div class="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-3">
                        <h2 class="text-xl font-bold text-yellow-500">🎮 Jogo do Bentinho</h2>
                        <p class="text-sm text-slate-400">Decifre os enigmas numéricos invertidos, suba pelas 4 fases e ganhe até 1 bilhão de pontos adicionais no placar.</p>
                        <a href="/jogo_bentinho" class="block text-center bg-yellow-600 text-black font-bold py-2 rounded-lg text-sm transition">Jogar Agora</a>
                    </div>
                </main>
            </div>
        </body>
        </html>
    """.replace(",", "."))

# ==============================================================================
# ROTA 1: REDE SOCIAL INDEPENDENTE (POSTAGENS)
# ==============================================================================
@app.route("/rede_social", methods=["GET", "POST"])
def rede_social():
    if not usuario_logado():
        return redirect(url_for("inicio"))
        
    if request.method == "POST":
        conteudo = request.form.get("conteudo", "").strip()
        if conteudo:
            with sqlite3.connect(BANCO_DADOS) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO posts (usuario_id, conteudo, data_criacao) VALUES (?, ?, ?)",
                          (session["usuario_id"], conteudo, datetime.now().strftime("%d/%m/%Y %H:%M")))
                conn.commit()
            flash("Publicação enviada para a rede!", "sucesso")
        return redirect(url_for("rede_social"))

    with sqlite3.connect(BANCO_DADOS) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT u.usuario, p.conteudo, p.data_criacao 
            FROM posts p 
            JOIN usuarios u ON p.usuario_id = u.id 
            ORDER BY p.id DESC
        """)
        posts = c.fetchall()

    return render_template_string("""
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="UTF-8"><title>Feed Global - Rede Social</title>
            <script src="https://tailwindcss.com"></script>
        </head>
        <body class="bg-slate-950 text-slate-100 min-h-screen p-4">
            <div class="max-w-xl mx-auto space-y-6">
                <div class="flex justify-between items-center"><h1 class="text-2xl font-bold text-cyan-400">CONEXÃO COMUNIDADE</h1><a href="/plataforma" class="text-sm text-slate-400 hover:underline"><- Menu</a></div>
                <form method="POST" class="bg-slate-900 border border-slate-800 p-4 rounded-xl space-y-3">
                    <textarea name="conteudo" rows="3" placeholder="No que você está pensando hoje?" class="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm focus:outline-none focus:border-cyan-500" required></textarea>
                    <button type="submit" class="w-full bg-cyan-600 hover:bg-cyan-500 font-bold py-2 rounded-lg text-sm transition">Compartilhar Publicação</button>
                </form>
                <div class="space-y-4">
                    {% for autor, texto, data in posts %}
                        <div class="bg-slate-900 border border-slate-800 p-4 rounded-xl space-y-2">
                            <div class="flex justify-between text-xs text-slate-400"><strong>@{{ autor }}</strong><span>{{ data }}</span></div>
