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
BANCO_DADOS = os.path.join(BASE_DIR, "jnb_definitiva.db")

EMAIL_DONO = "seu_email_aqui@seu_dominio.com"
SENHA_MESTRA_ACESSO = "JNB@2026#DONO"

# ==============================================
# INICIALIZAÇÃO DO BANCO DE DADOS
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
# FUNÇÕES AUXILIARES
# ==============================================
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

def responder_ia(pergunta):
    p = pergunta.lower().strip()
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("SELECT pergunta, resposta FROM conhecimento_ia")
    base = {k.lower(): v for k, v in c.fetchall()}
    conn.close()

    for chave in base:
        if chave in p:
            return base[chave]
    for chave, resp in CONHECIMENTO_PADRAO.items():
        if chave in p:
            return resp
    return f"Ainda não aprendi isso! Você pode me ensinar na aba 'Ensinar IA'! Pergunta: \"{pergunta}\""

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
                msg = "Já tenho essa pergunta cadastrada!"
        else:
            msg = "Preencha pergunta e resposta!"
            
    return render_template_string('''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ensinar IA</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 p-6 max-w-2xl mx-auto">
    <a href="/plataforma" class="text-yellow-500 mb-4 inline-block">&larr; Voltar</a>
    <h1 class="text-3xl font-bold text-yellow-500 mb-6">ENSINAR A INTELIGÊNCIA ARTIFICIAL</h1>
    {% if msg %}
    <div class="p-4 rounded-lg mb-6 font-bold {{'bg-green-900/50 text-green-400' if 'Aprendi' in msg else 'bg-yellow-900/50 text-yellow-400'}}">
        {{msg}}
    </div>
    {% endif %}
    <form method="POST" class="bg-slate-800 p-6 rounded-lg border border-yellow-500/30">
        <label class="block mb-2 font-bold">Pergunta ou palavra-chave:</label>
        <input type="text" name="pergunta" class="w-full p-3 bg-slate-900 border border-slate-700 rounded-lg mb-4 text-white" required>
        <label class="block mb-2 font-bold">Resposta que a IA deve aprender:</label>
        <textarea name="resposta" class="w-full p-3 bg-slate-900 border border-slate-700 rounded-lg mb-4 text-white" rows="4" required></textarea>
        <button type="submit" class="bg-yellow-600 text-black font-bold px-6 py-3 rounded-lg">Salvar na IA</button>
    </form>
</body>
</html>''', msg=msg)

# ==============================================
# JOGO BENTINHO — CORRIGIDO
# ==============================================
@app.route("/jogo_bentinho", methods=["GET", "POST"])
def jogo_bentinho():
    if not usuario_logado():
        return redirect(url_for("inicio"))
        
    TABELA = {'0': '0', '1': '9', '2': '8', '3': '7', '4': '6', '5': '5', '6': '4', '7': '3', '8': '2', '9': '1'}
    PTS = {1: 250000, 2: 2500000, 3: 25000000, 4: 1000000000}
    TAM = {1: 3, 2: 6, 3: 8, 4: 9}

    if "bent_fase" not in session:
        session["bent_fase"] = 1
    if "bent_pontos" not in session:
        session["bent_pontos"] = 0

    fase = int(session["bent_fase"])

    if "bent_num" not in session or session.get("bent_fase_atual") != fase:
        session["bent_num"] = "".join(random.choice("0123456789") for _ in range(TAM[fase]))
        session["bent_alvo"] = "".join(TABELA[d] for d in session["bent_num"])
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
            except Exception:
                pass

            if fase < 4:
                session["bent_fase"] += 1
                session.pop("bent_num", None)
            else:
                msg = "PARABÉNS! VOCÊ VENCEU O SEGREDO DOS NÚMEROS!"
                session["bent_fase"] = 1
                session.pop("bent_num", None)
        else:
            msg = "Errou! Tente novamente."

    return render_template_string('''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Segredo dos Números</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 flex items-center justify-center min-h-screen p-4">
    <div class="bg-slate-800 p-8 rounded-xl border-2 border-yellow-500/50 max-w-lg w-full">
        <h1 class="text-3xl font-bold text-yellow-500 text-center mb-2">SEGREDO DOS NÚMEROS</h1>
        <p class="text-center text-slate-400 mb-6">Fase {{fase}}/4 · Pontos: {{pontos}}</p>
        
        {% if msg %}
        <div class="text-center p-4 rounded-lg mb-6 text-lg font-bold {{'bg-green-900/50 text-green-400' if 'ACERTOU' in msg or 'PARABÉNS' in msg else 'bg-red-900/50 text-red-400'}}">
            {{msg}}
        </div>
        {% endif %}
        
        <div class="bg-slate-900 border-2 border-yellow-500/40 rounded-lg p-6 text-center mb-6">
            <p class="text-slate-400 mb-2">Número Alvo:</p>
            <p class="text-4xl font-mono text-yellow-400 font-bold tracking-widest">{{numero}}</p>
        </div>
        
        <form method="POST" class="space-y-4">
            <input type="text" name="resposta" placeholder="Digite o número correspondente..." class="w-full bg-slate-900 border-2 border-yellow-500 rounded-lg text-center text-2xl text-yellow-400 p-3 font-mono" required>
            <div class="flex gap-3">
                <button type="submit" class="flex-1 bg-yellow-600 text-black font-bold py-3 rounded-lg text-lg">Decifrar</button>
                <button type="submit" name="acao" value="reiniciar" class="bg-slate-600 text-white px-6 py-3 rounded-lg">Reiniciar</button>
            </div>
        </form>
        <p class="text-center mt-6"><a href="/plataforma" class="text-yellow-500">&larr; Voltar para Plataforma</a></p>
    </div>
</body>
</html>''', fase=session["bent_fase"], pontos=session["bent_pontos"], numero=session.get("bent_num", ""), msg=msg)

# ==============================================
# JOGO DAS CARTAS
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
            return redirect(url_for("jogo_cartas"))
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
                    except Exception:
                        pass
                    if fase < 4:
                        session["cartas_fase"] += 1
                        session.pop("cartas_alvo", None)
                    else:
                        msg = "PARABÉNS! VOCÊ VENCEU TODAS AS FASES!"
                        session["cartas_fase"] = 1
                        session.pop("cartas_alvo", None)
                else:
                    msg = "Errou! Tente novamente."
                    session["cartas_resposta"] = []

    alvo_html = "".join([f"<span class='bg-yellow-500 text-black px-4 py-2 rounded-lg font-bold text-xl m-1'>{c}</span>" for c in alvo])
    resp_html = "".join([f"<span class='bg-green-500 text-black px-4 py-2 rounded-lg font-bold text-xl m-1'>{c}</span>" for c in resposta]) if resposta else "<p class='text-slate-400'>Clique nas cartas abaixo...</p>"
    disp_html = "".join([f"<button type='submit' name='selecionar' value='{c}' class='bg-slate-700 hover:bg-slate-600 text-white border border-yellow-500 px-4 py-2 rounded-lg font-bold text-xl m-1'>{c}</button>" for c in CARTAS])

    return render_template_string(f'''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jogo das Cartas</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 p-6 max-w-2xl mx-auto">
    <a href="/plataforma" class="text-yellow-500">&larr; Voltar</a>
    <h1 class="text-3xl font-bold text-yellow-500 text-center my-4">JOGO DAS CARTAS</h1>
    <p class="text-center mb-4">Fase {fase}/4 · Pontos: {pontos}</p>

    {f'<div class="text-center p-3 rounded-lg mb-4 text-lg font-bold bg-slate-800 text-yellow-400">{msg}</div>' if msg else ''}

    <div class="bg-slate-800 p-4 rounded-lg mb-4">
        <p class="text-slate-400 text-sm mb-2 text-center">Cartas Alvo:</p>
        <div class="flex flex-wrap justify-center">{alvo_html}</div>
    </div>

    <div class="bg-slate-800 p-4 rounded-lg mb-4">
        <p class="text-slate-400 text-sm mb-2 text-center">Sua Resposta:</p>
        <div class="flex flex-wrap justify-center">{resp_html}</div>
    </div>

    <form method="POST" class="bg-slate-800 p-4 rounded-lg mb-4">
        <div class="flex flex-wrap justify-center">{disp_html}</div>
    </form>

    <div class="flex gap-4 justify-center">
        <form method="POST"><button type="submit" name="verificar" value="1" class="bg-green-600 px-6 py-2 rounded-lg font-bold">Verificar</button></form>
        <form method="POST"><button type="submit" name="nova" value="1" class="bg-yellow-600 text-black px-6 py-2 rounded-lg font-bold">Reiniciar</button></form>
    </div>
</body>
</html>''')

# ==============================================
# AUTENTICAÇÃO E REDE SOCIAL
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
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 flex items-center justify-center min-h-screen">
    <div class="bg-slate-800 p-8 rounded-xl border border-yellow-500/50 w-90 max-w-md">
        <h1 class="text-3xl font-bold text-yellow-500 text-center mb-6">JNB TECNOLOGIA</h1>
        <form action="/entrar" method="POST" class="space-y-4">
            <input type="email" name="email" placeholder="E-mail" class="w-full p-3 bg-slate-900 border border-slate-700 rounded-lg text-white" required>
            <input type="password" name="senha" placeholder="Senha" class="w-full p-3 bg-slate-900 border border-slate-700 rounded-lg text-white" required>
            <button type="submit" class="w-full bg-yellow-600 hover:bg-yellow-500 text-black font-bold p-3 rounded-lg">Entrar</button>
        </form>
        <p class="text-center mt-4 text-slate-400 text-sm">Não tem conta? <a href="/cadastrar" class="text-yellow-500">Cadastre-se</a></p>
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
                session["usuario_id"] = c.lastrowid
                session["nome_usuario"] = nome
                conn.close()
                return redirect(url_for("plataforma"))
            except sqlite3.IntegrityError:
                return "<h2 style='color:red;text-align:center;'>E-mail já cadastrado!</h2>"
    return render_template_string("""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cadastro</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 flex items-center justify-center min-h-screen">
    <div class="bg-slate-800 p-8 rounded-xl border border-yellow-500/50 w-90 max-w-md">
        <h1 class="text-2xl font-bold text-yellow-500 text-center mb-6">CADASTRO PERMANENTE</h1>
        <form method="POST" class="space-y-4">
            <input type="text" name="nome" placeholder="Seu Nome" class="w-full p-3 bg-slate-900 border border-slate-700 rounded-lg text-white" required>
            <input type="email" name="email" placeholder="E-mail" class="w-full p-3 bg-slate-900 border border-slate-700 rounded-lg text-white" required>
            <input type="password" name="senha" placeholder="Senha" class="w-full p-3 bg-slate-900 border border-slate-700 rounded-lg text-white" required>
            <button type="submit" class="w-full bg-yellow-600 hover:bg-yellow-500 text-black font-bold p-3 rounded-lg">Cadastrar</button>
        </form>
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
    return "<h2 style='color:red;text-align:center;'>Dados de login incorretos.</h2>"

@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("inicio"))

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

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
            nome_arq = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{arquivo.filename}")
            arquivo.save(os.path.join(app.config["UPLOAD_FOLDER"], nome_arq))
            
        if texto or nome_arq:
            conn = sqlite3.connect(BANCO_DADOS)
            c = conn.cursor()
            c.execute("INSERT INTO postagens (usuario_id, texto, arquivo, data_postagem) VALUES (?, ?, ?, ?)",
                      (usuario_id, texto, nome_arq, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
        return redirect(url_for("plataforma"))

    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("SELECT nome, pontos FROM usuarios WHERE id = ?", (usuario_id,))
    nome_usuario, total_pontos = c.fetchone()

    c.execute("""SELECT p.id, p.texto, p.arquivo, p.data_postagem, u.nome
                 FROM postagens p JOIN usuarios u ON p.usuario_id = u.id 
                 ORDER BY p.data_postagem DESC""")
    postagens = c.fetchall()
    conn.close()

    posts_html = ""
    for p in postagens:
        pid, texto, arquivo, data, autor = p
        posts_html += f'''<div class="bg-slate-800 p-4 rounded-lg border border-yellow-500/30 mb-4">
            <h4 class="font-bold text-yellow-400">{autor}</h4>
            <p class="text-xs text-slate-400 mb-2">{data}</p>
            {f'<p class="mb-3">{texto}</p>' if texto else ''}'''
        if arquivo:
            ext = arquivo.rsplit(".", 1)[1].lower()
            if ext in ["jpg", "jpeg", "png", "gif"]:
                posts_html += f'<img src="/uploads/{arquivo}" class="max-w-full h-auto rounded-lg my-2 max-h-96">'
            elif ext in ["mp4", "mov", "avi", "webm"]:
                posts_html += f'<video controls class="w-full rounded-lg my-2 max-h-96"><source src="/uploads/{arquivo}"></video>'
        posts_html += '</div>'

    return render_template_string(f'''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plataforma — JNB TECNOLOGIA</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen p-4 max-w-4xl mx-auto">
    <div class="flex justify-between items-center border-b border-slate-700 pb-4 mb-6">
        <div>
            <h1 class="text-2xl font-bold text-yellow-500">JNB TECNOLOGIA</h1>
            <p class="text-slate-400">Olá, {nome_usuario}!</p>
        </div>
        <div>
            <span class="text-yellow-500 font-bold text-lg">Pontos: {total_pontos}</span>
            <a href="/sair" class="ml-4 text-red-400 hover:underline">Sair</a>
        </div>
    </div>

    <div class="flex flex-wrap gap-2 mb-6 border-b border-slate-700 pb-3">
        <a href="/plataforma" class="bg-yellow-600 text-black font-bold px-4 py-2 rounded">Feed</a>
        <a href="/dna" class="bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded text-yellow-400 font-bold">DNA (ATGC)</a>
        <a href="/jogo_bentinho" class="bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded">Segredo dos Números</a>
        <a href="/jogo_cartas" class="bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded">Jogo Cartas</a>
        <a href="/ensinar_ia" class="bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded">Ensinar IA</a>
    </div>

    <div class="bg-slate-800 p-4 rounded-lg border border-yellow-500/30 mb-6">
        <form method="POST" enctype="multipart/form-data" class="space-y-3">
            <textarea name="texto_post" placeholder="O que você deseja publicar?" class="w-full bg-slate-900 border border-slate-700 p-3 rounded-lg text-white" rows="3"></textarea>
            <div class="flex justify-between items-center">
                <input type="file" name="arquivo" accept="image/*,video/*" class="text-sm text-slate-400">
                <button type="submit" class="bg-yellow-600 text-black font-bold px-6 py-2 rounded-lg hover:bg-yellow-500">Publicar</button>
            </div>
        </form>
    </div>

    <div>{posts_html if posts_html else '<p class="text-center text-slate-500">Nenhuma postagem ainda.</p>'}</div>
</body>
</html>''')

# ==============================================
# EXECUÇÃO DO SERVIDOR
# ==============================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
