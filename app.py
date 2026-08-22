# © 2026 JNB TECNOLOGIA — PLATAFORMA COMPLETA 
# REDE SOCIAL ESTILO FACEBOOK · JOGO · IA · DNA/BNJ
# POSTAGEM TEXTO + FOTO + VÍDEO · CURTIDAS · FEED
# PORTA 5000 · TUDO FUNCIONANDO ✅
# ==================================================

from flask import Flask, request, session, redirect, url_for, render_template_string, send_from_directory
import sqlite3
import os
import random
import hashlib
import base64
from datetime import datetime
from werkzeug.utils import secure_filename

# Inicializar aplicativo
app = Flask(__name__)
app.secret_key = os.environ.get("CHAVE_UNIFICADA", "JNB_TECNOLOGIA_2026_SEGURA")
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 315360000

# Configuração de upload de arquivos
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4", "mov", "avi", "webm"}

BANCO_DADOS = "jnb_novo.db"

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# -------------------- BANCO DE DADOS --------------------
def init_db():
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    
    # Tabela de usuários
    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha_hash TEXT NOT NULL,
        pontos INTEGER DEFAULT 0,
        dna_chave TEXT
    )""")
    
    # Tabela de postagens
    c.execute("""
    CREATE TABLE IF NOT EXISTS postagens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        texto TEXT,
        arquivo TEXT,
        data_postagem TEXT NOT NULL,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )""")
    
    # Tabela de curtidas
    c.execute("""
    CREATE TABLE IF NOT EXISTS curtidas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        postagem_id INTEGER NOT NULL,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY(postagem_id) REFERENCES postagens(id),
        UNIQUE(usuario_id, postagem_id)
    )""")
    
    conn.commit()
    conn.close()

init_db()

def usuario_logado():
    return "usuario_id" in session


# -------------------- ROTAS --------------------
@app.route("/")
def inicio():
    if usuario_logado():
        return redirect(url_for("plataforma"))
    return render_template_string('''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JNB TECNOLOGIA — Acesso</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif;}
        body{background:linear-gradient(180deg,#0f172a,#1e293b);color:#e2e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center;}
        .caixa{background:rgba(15,23,42,0.8);border:1px solid #f59e0b;padding:40px;border-radius:12px;width:100%;max-width:400px;}
        h1{color:#f59e0b;text-align:center;margin-bottom:30px;}
        input{width:100%;padding:12px;margin:8px 0;background:#020617;border:1px solid #33415e;color:white;border-radius:6px;}
        button{width:100%;padding:12px;background:#f59e0b;color:#1e1b16;border:none;border-radius:6px;font-weight:bold;cursor:pointer;margin-top:15px;}
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
                session["usuario_id"] = usuario_id
                session["nome_usuario"] = nome
                conn.close()
                return redirect(url_for("plataforma"))
            except sqlite3.IntegrityError:
                return "E-mail já cadastrado. <a href='/'>Voltar</a>"
    return render_template_string('''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cadastrar — JNB TECNOLOGIA</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif;}
        body{background:linear-gradient(180deg,#0f172a,#1e293b);color:#e2e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center;}
        .caixa{background:rgba(15,23,42,0.8);border:1px solid #f59e0b;padding:40px;border-radius:12px;width:100%;max-width:400px;}
        h1{color:#f59e0b;text-align:center;margin-bottom:30px;}
        input{width:100%;padding:12px;margin:8px 0;background:#020617;border:1px solid #33415e;color:white;border-radius:6px;}
        button{width:100%;padding:12px;background:#f59e0b;color:#1e1b16;border:none;border-radius:6px;font-weight:bold;cursor:pointer;margin-top:15px;}
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
    return "E-mail ou senha inválidos. <a href='/'>Voltar</a>"

@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("inicio"))

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# -------------------- PLATAFORMA UNIFICADA --------------------
@app.route("/plataforma", methods=["GET", "POST"])
def plataforma():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    
    usuario_id = session["usuario_id"]

    # Postar nova postagem (texto + arquivo)
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


    # Curtir postagem
    if request.args.get("curtir"):
        postagem_id = request.args.get("curtir")
        conn = sqlite3.connect(BANCO_DADOS)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO curtidas (usuario_id, postagem_id) VALUES (?, ?)", (usuario_id, postagem_id))
            conn.commit()
        except sqlite3.IntegrityError:
            c.execute("DELETE FROM curtidas WHERE usuario_id = ? AND postagem_id = ?", (usuario_id, postagem_id))
            conn.commit()
        conn.close()
        return redirect(url_for("plataforma") + "#post-" + postagem_id)

    # Dados do usuário
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("SELECT nome, pontos, dna_chave FROM usuarios WHERE id = ?", (usuario_id,))
    nome_usuario, total_pontos, dna_chave = c.fetchone()
    
    # Buscar postagens com dados
    c.execute("""
        SELECT p.id, p.texto, p.arquivo, p.data_postagem, u.nome,
               (SELECT COUNT(*) FROM curtidas c WHERE c.postagem_id = p.id) as total_curtidas,
               EXISTS(SELECT 1 FROM curtidas c WHERE c.postagem_id = p.id AND c.usuario_id = ?) as curtiu
        FROM postagens p JOIN usuarios u ON p.usuario_id = u.id
        ORDER BY p.data_postagem DESC
    """, (usuario_id,))
    postagens = c.fetchall()
    conn.close()

    return render_template_string('''""
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plataforma — JNB TECNOLOGIA</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/font-awesome@4.7.0/css/font-awesome.min.css">
    <style>
        body { background: linear-gradient(180deg, #0f172a, #1e293b); color: #e2e8f0; min-height: 100vh; }
        .hidden { display: none !important; }
        .tab-btn { transition: all 0.3s ease; }
        .tab-content { animation: fadeIn 0.3s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
        .video-js { width: 100% !important; height: auto !important; }
    </style>
    <link href="https://vjs.zencdn.net/8.10.0/video-js.css" rel="stylesheet" />
</head>
<body>
    <div class="container max-w-6xl mx-auto p-4 md:p-6">
        <!-- Cabeçalho -->
        <div class="flex flex-col md:flex-row justify-between items-center border-b border-yellow-500/40 pb-4 mb-6">
            <div>
                <h1 class="text-2xl font-bold text-yellow-500 font-serif">🚀 JNB TECNOLOGIA</h1>
                <p class="text-sm text-gray-400">Bem-vindo, {{ nome_usuario }}!</p>
            </div>
            <div class="text-right mt-3 md:mt-0">
                <p class="text-xs text-gray-400">Total de Pontos</p>
                <div id="global-total-pontos" class="text-xl font-bold text-yellow-500">{{ total_pontos }}</div>
                <a href="/sair" class="text-xs text-red-400 hover:text-red-300">Sair <i class="fa fa-sign-out"></i></a>
            </div>
        </div>

        <!-- Navegação por Abas -->
        <div class="flex overflow-x-auto border-b border-gray-700 mb-6">
            <button id="btn-rede" class="tab-btn px-5 py-3 text-gray-400 border-b-2 border-yellow-500 text-white" onclick="switchTab('rede')">
                <i class="fa fa-share-alt mr-2"></i>Rede Social
            </button>
            <button id="btn-jogo" class="tab-btn px-5 py-3 text-gray-400 border-b-2 border-transparent hover:text-white hover:border-yellow-500" onclick="switchTab('jogo')">
                <i class="fa fa-puzzle-piece mr-2"></i>Jogo: Segredo dos Números
            </button>
            <button id="btn-ia" class="tab-btn px-5 py-3 text-gray-400 border-b-2 border-transparent hover:text-white hover:border-yellow-500" onclick="switchTab('ia')">
                <i class="fa fa-file-text mr-2"></i>IA & Documentos
            </button>
            <button id="btn-dna" class="tab-btn px-5 py-3 text-gray-400 border-b-2 border-transparent hover:text-white hover:border-yellow-500" onclick="switchTab('dna')">
                <i class="fa fa-dna mr-2"></i>DNA / BNJ
            </button>
        </div>

        <!-- Aba 1: Rede Social -->
        <div id="tab-rede" class="tab-content">
            <!-- Caixa de Postagem -->
            <div class="bg-gray-800/50 p-6 rounded-xl border border-yellow-500/30 mb-6">
                <h2 class="text-xl font-bold text-yellow-400 mb-4"><i class="fa fa-pencil-square mr-2"></i>O que você está pensando?</h2>
                <form method="POST" enctype="multipart/form-data">
                    <textarea name="texto_post" placeholder="Escreva algo..." class="w-full bg-gray-900 border border-gray-700 rounded-lg p-4 text-gray-200 focus:outline-none focus:border-yellow-500 mb-4" rows="3"></textarea>
                    <div class="flex flex-wrap items-center justify-between gap-3">
                        <div class="flex items-center gap-2">
                            <label class="cursor-pointer bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded-lg text-sm transition">
                                <i class="fa fa-paperclip mr-1"></i>Anexar Foto/Vídeo
                                <input type="file" name="arquivo" class="hidden" accept="image/*,video/*" onchange="previewFile(this)">
                            </label>
                            <span id="arquivo-nome" class="text-gray-400 text-sm"></span>
                        </div>
                        <button type="submit" class="bg-yellow-600 hover:bg-yellow-700 text-white px-6 py-2 rounded-lg font-bold transition">
                            <i class="fa fa-paper-plane mr-2"></i>Publicar
                        </button>
                    </div>
                </form>
            </div>

            <!-- Feed de Postagens -->
            <div class="space-y-6">
                {% if postagens %}
                {% for pid, texto, arquivo, data, autor, total_curtidas, curtiu in postagens %}
                <div id="post-{{ pid }}" class="bg-gray-800 rounded-xl border border-yellow-500/20 overflow-hidden shadow-lg">
                    <!-- Cabeçalho da postagem -->
                    <div class="p-4 border-b border-gray-700/50 flex items-center">
                        <div class="w-12 h-12 bg-yellow-500 rounded-full flex items-center justify-center font-bold text-white text-xl mr-4">{{ autor[0] }}</div>
                        <div>
                            <h4 class="font-bold text-white">{{ autor }}</h4>
                            <p class="text-gray-400 text-sm">{{ data }}</p>
                        </div>
                    </div>
                    
                    <!-- Conteúdo da postagem -->
                    <div class="p-4">
                        {% if texto %}
                        <p class="text-gray-100 text-base mb-4 whitespace-pre-wrap">{{ texto }}</p>
                        {% endif %}
                        
                        {% if arquivo %}
                            {% set ext = arquivo.split('.')[-1].lower() %}
                            {% if ext in ['jpg','jpeg','png','gif'] %}
                            <img src="/uploads/{{ arquivo }}" class="w-full rounded-lg max-h-96 object-cover mb-4">
                            {% elif ext in ['mp4','mov','avi','webm'] %}
                            <video controls class="w-full rounded-lg mb-4" preload="metadata">
                                <source src="/uploads/{{ arquivo }}" type="video/{{ ext }}">
                                Seu navegador não suporta vídeo.
                            </video>
                            {% endif %}
                        {% endif %}
                    </div>
                    
                    <!-- Ações: Curtir -->
                    <div class="px-4 py-3 bg-gray-900/50 border-t border-gray-700/50 flex items-center">
                        <a href="/plataforma?curtir={{ pid }}#post-{{ pid }}" class="flex items-center gap-2 px-4 py-2 rounded-lg transition {{ 'text-yellow-400 bg-yellow-900/30' if curtiu else 'text-gray-300 hover:bg-gray-700/50' }}">
                            <i class="fa fa-thumbs-up"></i>
                            <span>Curtir · {{ total_curtidas }}</span>
                        </a>
                    </div>
                </div>
                {% endfor %}
                {% else %}
                <div class="text-center py-20">
                    <i class="fa fa-newspaper-o text-gray-600 text-5xl mb-4"></i>
                    <p class="text-gray-500 text-xl">Ainda não há postagens. Seja o primeiro a compartilhar algo!</p>
                </div>
                {% endif %}
            </div>
        </div>

        <!-- ABA 2: Jogo, ABA 3: IA, ABA 4: DNA — mantidas iguais ao código anterior -->
        <div id="tab-jogo" class="tab-content hidden">
            <div class="bg-gray-800/50 p-8 rounded-xl border border-yellow-500/30 text-center">
                <h2 class="text-2xl font-bold text-yellow-500 mb-6">🎮 O SEGREDO DOS NÚMEROS</h2>
                <div class="flex flex-wrap justify-center gap-3 mb-8">
                    <button class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-bold transition" onclick="setGamePhase(1, 25)">Fase 1 (3 dígitos — 25pts)</button>
                    <button class="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg font-bold transition" onclick="setGamePhase(2, 50)">Fase 2 (6 dígitos — 50pts)</button>
                    <button class="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg font-bold transition" onclick="setGamePhase(3, 75)">Fase 3 (8 dígitos — 75pts)</button>
                    <button class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-bold transition" onclick="setGamePhase(4, 100)">Fase 4 (9 dígitos — 100pts)</button>
                </div>
                <div class="bg-gray-900 border border-yellow-500/40 rounded-lg p-6 mb-8 text-2xl font-mono text-yellow-300 tracking-widest">
                    🟠 = 4164 — 🔴 = 1462 — ⚫ = 9808 — ⚪ = 5561
                </div>
                <div class="mb-6">
                    <input type="text" id="game-input" placeholder="---" maxlength="9" class="bg-gray-900 border-2 border-yellow-600 text-yellow-200 font-mono text-3xl text-center px-6 py-3 rounded-lg focus:outline-none focus:border-yellow-400">
                    <button onclick="checkGameAnswer()" class="bg-yellow-600 hover:bg-yellow-700 text-white px-8 py-3 rounded-lg font-bold text-lg ml-4 transition">
                        <i class="fa fa-check"></i> Confirmar
                    </button>
                </div>
                <div id="game-feedback" class="hidden mt-6 p-4 rounded-lg"></div>
                <div class="text-gray-400 text-sm mt-6">
                    Pontos desta partida: <span id="feedback-pts" class="text-yellow-500 font-bold">0</span> | 
                    Total acumulado: <span id="feedback-total" class="text-yellow-500 font-bold">{{ total_pontos }}</span>
                </div>
            </div>
        </div>

        <div id="tab-ia" class="tab-content hidden">
            <div class="bg-gray-800/50 p-6 rounded-xl border border-yellow-500/30">
                <h2 class="text-xl font-bold text-yellow-400 mb-4"><i class="fa fa-robot mr-2"></i>IA — Gerador de Documentos</h2>
                <textarea id="ia-input" placeholder="Descreva o documento que você precisa... Ex: Contrato de prestação de serviços" class="w-full bg-gray-900 border border-gray-700 rounded-lg p-4 text-gray-200 focus:outline-none focus:border-yellow-500 mb-4" rows="4"></textarea>
                <button onclick="generateDocumentAI()" class="bg-yellow-600 hover:bg-yellow-700 text-white px-5 py-2 rounded-lg font-medium transition">
                    <i class="fa fa-file-text mr-2"></i>Gerar Documento
                </button>
                <div id="ia-result" class="mt-6 p-4 bg-gray-900 rounded-lg border border-gray-700 hidden"></div>
            </div>
        </div>

        <div id="tab-dna" class="tab-content hidden">
            <div class="bg-gray-800/50 p-6 rounded-xl border border-yellow-500/30">
                <h2 class="text-xl font-bold text-yellow-400 mb-4"><i class="fa fa-dna mr-2"></i>DNA / Conversor BNJ</h2>
                <p class="text-sm text-gray-400 mb-4">Sua chave única: <code class="bg-gray-900 px-2 py-1 rounded text-yellow-300">{{ dna_chave }}</code></p>
                <textarea id="dna-input" placeholder="Digite texto, número ou dado para converter em DNA..." class="w-full bg-gray-900 border border-gray-700 rounded-lg p-4 text-gray-200 focus:outline-none focus:border-yellow-500 mb-4" rows="3"></textarea>
                <button onclick="converterParaDNA()" class="bg-yellow-600 hover:bg-yellow-700 text-white px-5 py-2 rounded-lg font-medium transition mr-2">
                    Converter em DNA
                </button>
                <button onclick="decodificarDNA()" class="bg-gray-600 hover:bg-gray-700 text-white px-5 py-2 rounded-lg font-medium transition">
                    Decodificar DNA
                </button>
                <div id="dna-result" class="mt-6 p-4 bg-gray-900 rounded-lg border border-gray-700 hidden"></div>
            </div>
        </div>
    </div>

    <script src="https://vjs.zencdn.net/8.10.0/video.min.js"></script>
    <script>
        let currentPhase = 1;
        let pointsValue = 25;
        let totalPoints = {{ total_pontos }};
        const correctAnswers = {1: "146", 2: "416414", 3: "98085561", 4: "249322519"};
        const usuarioId = {{ session.usuario_id }};

        function switchTab(tab) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.add('hidden'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('border-yellow-500','text-white'));
            document.getElementById('tab-'+tab).classList.remove('hidden');
            document.getElementById('btn-'+tab).classList.add('border-yellow-500','text-white');
        }

        function previewFile(input) {
            const nome = input.files[0]?.name || "";
            document.getElementById('arquivo-nome').textContent = nome ? "📎 " + nome : "";
        }

        function setGamePhase(phase, pts) {
            currentPhase = phase;
            pointsValue = pts;
            const input = document.getElementById('game-input');
            input.value = "";
            if(phase === 1) input.placeholder = "---";
            if(phase === 2) input.placeholder = "------";
            if(phase === 3) input.placeholder = "--------";
            if(phase === 4) input.placeholder = "---------";
            document.getElementById('game-feedback').classList.add('hidden');
        }

        function checkGameAnswer() {
            const input = document.getElementById('game-input').value.trim();
            const feedback = document.getElementById('game-feedback');
            if(!input) return alert("Digite sua resposta!");

            if(input === correctAnswers[currentPhase]) {
                totalPoints += pointsValue;
                document.getElementById('global-total-pontos').textContent = totalPoints;
                document.getElementById('feedback-total').textContent = totalPoints;
                document.getElementById('feedback-pts').textContent = pointsValue;
                
                feedback.innerHTML = `<p class="text-center font-bold">✅ ACERTOU! +${pointsValue} PONTOS!</p>`;
                feedback.className = "mt-6 p-4 rounded-lg bg-green-900/30 border border-green-500 text-green-300";
                feedback.classList.remove('hidden');

                fetch("/atualizar_pontos", {
                    method: "POST",
                    headers: {"Content-Type": "application/x-www-form-urlencoded"},
                    body: `pontos=${pointsValue}`
                });
            } else {
                feedback.innerHTML = `<p class="text-center font-bold">❌ Resposta incorreta! Tente novamente.</p>`;
                feedback.className = "mt-6 p-4 rounded-lg bg-red-900/30 border border-red-500 text-red-300";
                feedback.classList.remove('hidden');
            }
            document.getElementById('game-input').value = "";
        }

        function generateDocumentAI() {
            const texto = document.getElementById('ia-input').value.trim();
            if(!texto) return alert("Descreva o documento primeiro!");
            const resultado = document.getElementById('ia-result');
            resultado.innerHTML = `<h4 class="font-bold text-yellow-400 mb-2">📄 Documento Gerado:</h4><p class="text-gray-300 text-sm">---<br>Modelo gerado para: ${texto}<br>Data: ${new Date().toLocaleString()}<br>Assinatura digital: JNB-${Math.random().toString(36).substr(2,10).toUpperCase()}<br>---</p>`;
            resultado.classList.remove('hidden');
        }

        function textoParaDNA(texto) {
            const mapa = {'A':'AT', 'T':'TA', 'C':'CG', 'G':'GC'};
            let dna = "";
            for(let c of texto.toUpperCase()) {
                const code = c.charCodeAt(0).toString(2).padStart(8,'0');
                for(let bit of code) dna += bit === '1' ? mapa['G'] : mapa['A'];
            }
            return dna;
        }

        function dnaParaTexto(dna) {
            let bin = "";
            for(let i=0; i<dna.length; i+=2) {
                const par = dna.substr(i,2);
                bin += par === 'GC' ? '1' : '0';
            }
            let texto = "";
            for(let i=0; i<bin.length; i+=8) {
                const byte = bin.substr(i,8);
                if(byte.length === 8) texto += String.fromCharCode(parseInt(byte,2));
            }
            return texto;
        }
function converterParaDNA() {
    const texto = document.getElementById('dna-input').value.trim();
    if(!texto) return alert("Digite algo para converter!");
    const res = document.getElementById('dna-result');
    const dna = textoParaDNA(texto);
    res.innerHTML = '<h4 class="font-bold text-yellow-400 mb-2">🧬 DNA Gerado:</h4><p class="text-xs break-all">' + dna + '</p>';
    res.classList.remove('hidden');
    
    const blob = new Blob([dna], { type: "text/plain;charset=utf-8" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "documento_dna.txt";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function decodificarDNA() {
    const dna = document.getElementById('dna-input').value.trim();
    if(!dna.includes('AT') && !dna.includes('TA')) return alert("Digite um DNA válido!");
    const res = document.getElementById('dna-result');
    try {
        const texto = dnaParaTexto(dna);
        res.innerHTML = '<h4 class="font-bold text-yellow-400 mb-2">🔓 Dados Decodificados:</h4><p class="text-sm">' + texto + '</p>';
    } catch (e) {
        res.innerHTML = '<p class="text-red-400">❌ DNA inválido ou corrompido!</p>';
    }
    res.classList.remove('hidden');
}

function lerArquivoDNA(event) {
    const file = event.target.files;
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById('dna-input').value = e.target.result.trim();
        decodificarDNA(); 
    };
    reader.readAsText(file);
}

window.onload = () => switchTab('rede');
</script>
</body>
</html>


        window.onload = () => switchTab('rede');
    </script>
</body>
</html>''', nome_usuario=nome_usuario, total_pontos=total_pontos, dna_chave=dna_chave, postagens=postagens, session=session)

@app.route("/atualizar_pontos", methods=["POST"])
def atualizar_pontos():
    if not usuario_logado():
        return "Não autorizado", 401
    pontos = int(request.form.get("pontos", 0))
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("UPDATE usuarios SET pontos = pontos + ? WHERE id = ?", (pontos, session["usuario_id"]))
    conn.commit()
    conn.close()
    return "OK"

# -------------------- RODAR SERVIDOR --------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
