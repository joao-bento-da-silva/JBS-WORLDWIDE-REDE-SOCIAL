 # ==================================================
# © 2026 JNB TECNOLOGIA — DNA CORRIGIDO ✅
# CRIPTOGRAFA · DESCRIPTOGRAFA · DOWNLOAD .bnj
# PORTA 5000 — INTACTA NO FINAL ✅
# ==================================================

from flask import Flask, request, session, redirect, url_for, render_template_string, send_from_directory, make_response
import sqlite3, os, random, hashlib, base64
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

EMAIL_DONO = "seu_email_aqui@exemplo.com"
SENHA_MESTRA = "JNB@2026#SEGURA"

# ==================================================
# 🧬 FUNÇÕES DNA — CORRIGIDAS ✅
# ==================================================
def texto_para_dna(texto, chave):
    chave_bytes = hashlib.sha256(chave.encode()).digest()
    chave_bits = []
    for b in chave_bytes:
        for i in range(8):
            chave_bits.append((b >> i) & 1)
    bit_pos = 0
    dna = ""
    for c in texto.encode("utf-8"):
        for i in range(7, -1, -1):
            bit = (c >> i) & 1
            bit ^= chave_bits[bit_pos % len(chave_bits)]
            dna += "AT" if bit == 0 else "CG"
            bit_pos += 1
    return dna

def dna_para_texto(dna, chave):
    chave_bytes = hashlib.sha256(chave.encode()).digest()
    chave_bits = []
    for b in chave_bytes:
        for i in range(8):
            chave_bits.append((b >> i) & 1)
    bit_pos = 0
    bytes_res = bytearray()
    byte_atual = 0
    for i in range(0, len(dna), 2):
        par = dna[i:i+2].upper()
        bit = 0 if par in ("AT", "TA") else 1
        bit ^= chave_bits[bit_pos % len(chave_bits)]
        byte_atual = (byte_atual << 1) | bit
        bit_pos += 1
        if bit_pos % 8 == 0:
            bytes_res.append(byte_atual)
            byte_atual = 0
    try:
        return bytes_res.decode("utf-8")
    except:
        return "❌ Erro: chave ou DNA inválido!"

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

def usuario_logado():
    return "usuario_id" in session

def eh_dono():
    if not usuario_logado():
        return False
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("SELECT email FROM usuarios WHERE id = ?", (session["usuario_id"],))
    u = c.fetchone()
    conn.close()
    return u and u[0].lower() == EMAIL_DONO.lower()

def resposta_ia(pergunta):
    p = pergunta.lower().strip()
    if "brasil" in p and ("descobriu" in p or "ano" in p):
        return "O Brasil foi descoberto em 22 de abril de 1500 por Pedro Álvares Cabral."
    elif "quem é você" in p or "quem criou" in p:
        return "IA da JNB TECNOLOGIA — criada por João Bento da Silva."
    elif "bentinho" in p or "números" in p:
        return "🎮 0→0, 1→9, 2→8, 3→7, 4→6, 5→5, 6→4, 7→3, 8→2, 9→1."
    elif "cartas" in p:
        return "🃏 Y→Y, A→Z, Z→A, B→X, X→B, C→G, G→C, D→F, F→D, E→E."
    elif "dna" in p:
        return "🧬 Criptografe, baixe .bnj e descriptografe só com a chave!"
    elif p.startswith("oi") or p.startswith("olá"):
        return "Olá! Como posso ajudar?"
    else:
        return f"Entendi! Você perguntou: {pergunta}"

@app.route("/")
def inicio():
    if usuario_logado():
        return redirect(url_for("plataforma"))
    return render_template_string("""
<!DOCTYPE html><html lang="pt-br"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>JNB TECNOLOGIA</title>
<style>*{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif;}body{background:linear-gradient(180deg,#0f172a,#1e293b);color:#e2e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center;}.caixa{background:rgba(15,23,42,.8);padding:40px;border-radius:12px;border:1px solid #f59e0b;width:90%;max-width:400px;}h1{color:#f59e0b;text-align:center;margin-bottom:30px;}input{width:100%;padding:12px;margin:8px 0;background:#020617;border:1px solid #334155;color:#fff;border-radius:6px;}button{width:100%;padding:12px;background:#f59e0b;color:#1e1b16;border:none;border-radius:6px;font-weight:bold;cursor:pointer;}.link{text-align:center;margin-top:15px;font-size:14px;color:#94a3b8;}.link a{color:#f59e0b;text-decoration:none;}</style></head><body>
<div class="caixa"><h1>JNB TECNOLOGIA</h1>
<form action="/entrar" method="POST"><input type="email" name="email" placeholder="E-mail" required><input type="password" name="senha" placeholder="Senha" required><button type="submit">Entrar</button></form>
<div class="link">Não tem conta? <a href="/cadastrar">Cadastre-se</a></div></div></body></html>""")

@app.route("/cadastrar", methods=["GET","POST"])
def cadastrar():
    if request.method == "POST":
        nome = request.form.get("nome","").strip()
        email = request.form.get("email","").strip()
        senha = request.form.get("senha","").strip()
        if nome and email and senha:
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            dna_chave = base64.b64encode(os.urandom(24)).decode()
            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                conn = sqlite3.connect(BANCO_DADOS)
                c = conn.cursor()
                c.execute("INSERT INTO usuarios (nome,email,senha_hash,dna_chave,data_cadastro) VALUES (?,?,?,?,?)",
                          (nome,email,senha_hash,dna_chave,agora))
                conn.commit()
                conn.close()
                return redirect(url_for("inicio"))
            except sqlite3.IntegrityError:
                return "E-mail já cadastrado!"
    return render_template_string("""
<!DOCTYPE html><html lang="pt-br"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Cadastrar — JNB TECNOLOGIA</title>
<style>*{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif;}body{background:linear-gradient(180deg,#0f172a,#1e293b);color:#e2e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center;}.caixa{background:rgba(15,23,42,.8);padding:40px;border-radius:12px;border:1px solid #f59e0b;width:90%;max-width:400px;}h1{color:#f59e0b;text-align:center;margin-bottom:30px;}input{width:100%;padding:12px;margin:8px 0;background:#020617;border:1px solid #334155;color:#fff;border-radius:6px;}button{width:100%;padding:12px;background:#f59e0b;color:#1e1b16;border:none;border-radius:6px;font-weight:bold;cursor:pointer;}.link{text-align:center;margin-top:15px;font-size:14px;color:#94a3b8;}.link a{color:#f59e0b;text-decoration:none;}</style></head><body>
<div class="caixa"><h1>Cadastrar ✅</h1>
<form method="POST"><input type="text" name="nome" placeholder="Seu nome" required><input type="email" name="email" placeholder="E-mail" required><input type="password" name="senha" placeholder="Senha" required><button type="submit">Cadastrar</button></form>
<div class="link">Já tem conta? <a href="/">Entrar</a></div></div></body></html>""")

@app.route("/entrar", methods=["POST"])
def entrar():
    email = request.form.get("email","").strip()
    senha = request.form.get("senha","").strip()
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("SELECT id FROM usuarios WHERE email = ? AND senha_hash = ?", (email, senha_hash))
    u = c.fetchone()
    conn.close()
    if u:
        session["usuario_id"] = u[0]
        return redirect(url_for("plataforma"))
    return "E-mail ou senha inválidos!"

@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("inicio"))

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/area_privada")
def area_privada():
    if not usuario_logado() or not eh_dono():
        return "Acesso negado!"
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM usuarios")
    total_usuarios = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM postagens")
    total_postagens = c.fetchone()[0]
    conn.close()
    return f"""
<!DOCTYPE html><html lang="pt-br"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Área Privada</title>
<style>body{{background:#0f172a;color:#fff;padding:20px;}}.caixa{{background:#1e293b;padding:20px;border-radius:10px;border:1px solid #f59e0b;}}h1{{color:#f59e0b;}}</style></head><body>
<div class="caixa"><h1>🔒 ÁREA PRIVADA — DONO</h1>
<p>Total de usuários: {total_usuarios}</p><p>Total de postagens: {total_postagens}</p>
<br><a href="/plataforma" style="color:#f59e0b;">← Voltar</a></div></body></html>"""

# ==================================================
# 🧬 ROTAS DNA — CORRIGIDAS ✅
# ==================================================
@app.route("/dna_criptografar", methods=["POST"])
def rota_dna_criptografar():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    texto = request.form.get("texto_original", "").strip()
    chave = request.form.get("chave_usuario", "").strip()
    if not texto or not chave:
        return "Preencha o texto e a chave!", 400
    return texto_para_dna(texto, chave)

@app.route("/dna_descriptografar", methods=["POST"])
def rota_dna_descriptografar():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    dna_texto = request.form.get("dna_codificado", "").strip()
    chave = request.form.get("chave_usuario", "").strip()
    if not dna_texto or not chave:
        return "Preencha o DNA e a chave!", 400
    return dna_para_texto(dna_texto, chave)

@app.route("/baixar_dna", methods=["POST"])
def rota_baixar_dna():
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

@app.route("/responder_ia", methods=["POST"])
def responder_ia_rota():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    pergunta = request.form.get("pergunta", "").strip()
    if not pergunta:
        return "Digite uma pergunta!"
    resp = resposta_ia(pergunta)
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("INSERT INTO conversas_ia (usuario_id,pergunta,resposta,data_hora) VALUES (?,?,?,?)",
              (session["usuario_id"], pergunta, resp, agora))
    conn.commit()
    conn.close()
    return resp

@app.route("/jogo_bentinho", methods=["GET","POST"])
def jogo_bentinho():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    TABELA = {'0':'0','1':'9','2':'8','3':'7','4':'6','5':'5','6':'4','7':'3','8':'2','9':'1'}
    if "bent_fase" not in session: session["bent_fase"] = 1
    if "bent_pontos" not in session: session["bent_pontos"] = 0
    if request.method == "POST":
        if request.form.get("acao") == "reiniciar":
            session["bent_fase"] = 1
            session["bent_pontos"] = 0
        else:
            resp = request.form.get("resposta", "").strip()
            num = request.form.get("numero_gerado", "")
            esperado = "".join(TABELA[d] for d in num)
            if resp == esperado:
                pts = {1:250000,2:2500000,3:25000000,4:1000000000}[session["bent_fase"]]
                session["bent_pontos"] += pts
                if session["bent_fase"] < 4:
                    session["bent_fase"] += 1
                else:
                    session["bent_fase"] = 1
            else:
                session["bent_fase"] = 1
    tam = {1:3,2:6,3:8,4:9}[session["bent_fase"]]
    numero = "".join(random.choice("0123456789") for _ in range(tam))
    return render_template_string(f"""
<!DOCTYPE html><html lang="pt-br"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>🎮 Jogo Bentinho</title>
<style>body{{background:linear-gradient(180deg,#0f172a,#1e293b);color:#e2e8f0;min-height:100vh;padding:20px;}}.caixa{{background:#1e293b;padding:30px;border-radius:12px;border:2px solid #f59e0b;max-width:500px;margin:0 auto;}}h1{{color:#f59e0b;text-align:center;}}.num{{font-size:48px;font-family:monospace;text-align:center;color:#f59e0b;margin:20px 0;}}input{{width:100%;padding:12px;font-size:20px;text-align:center;background:#0f172a;border:2px solid #f59e0b;color:#f59e0b;border-radius:8px;margin:10px 0;}}button{{width:100%;padding:12px;background:#f59e0b;color:#000;border:none;border-radius:8px;font-weight:bold;font-size:18px;cursor:pointer;margin:5px 0;}}a{{color:#f59e0b;display:block;text-align:center;margin-top:20px;}}</style></head><body>
<div class="caixa"><h1>🎮 SEGREDO DOS NÚMEROS</h1>
<p style="text-align:center;">Fase {session['bent_fase']}/4 · Pontos: {session['bent_pontos']:,}</p>
<div class="num">{numero}</div>
<form method="POST"><input type="hidden" name="numero_gerado" value="{numero}">
<input type="text" name="resposta" placeholder="Digite o número convertido..." required>
<button type="submit">✅ Enviar</button>
<button type="submit" name="acao" value="reiniciar" style="background:#475569;color:#fff;">🔄 Reiniciar</button>
</form>
<a href="/plataforma">← Voltar</a></div></body></html>""")

@app.route("/jogo_cartas", methods=["GET","POST"])
def jogo_cartas():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    REGRAS = {'Y':'Y','A':'Z','Z':'A','B':'X','X':'B','C':'G','G':'C','D':'F','F':'D','E':'E'}
    CARTAS = list(REGRAS.keys())
    if "cartas_fase" not in session: session["cartas_fase"] = 1
    if "cartas_pontos" not in session: session["cartas_pontos"] = 0
    qtd = {1:3,2:5,3:7,4:10}[session["cartas_fase"]]
    if request.method == "POST":
        escolha = request.form.get("escolha","")
        alvo = request.form.get("alvo","")
        if alvo and escolha:
            if REGRAS[escolha] == alvo:
                session["cartas_pontos"] += {1:100,2:300,3:500,4:1000}[session["cartas_fase"]]
                if session["cartas_fase"] < 4:
                    session["cartas_fase"] += 1
            else:
                session["cartas_fase"] = 1
        return redirect(url_for("jogo_cartas"))
    alvo = random.choice(list(REGRAS.values()))
    session["cartas_alvo"] = alvo
    botoes = "".join(f'<button type="submit" name="escolha" value="{c}" style="padding:15px 25px;margin:5px;font-size:24px;border-radius:8px;background:#f59e0b;color:#000;border:none;font-weight:bold;cursor:pointer;">{c}</button>' for c in CARTAS)
    return f"""
<!DOCTYPE html><html lang="pt-br"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>🃏 Jogo das Cartas</title>
<style>body{{background:linear-gradient(180deg,#0f172a,#1e293b);color:#fff;min-height:100vh;padding:20px;text-align:center;}}.caixa{{background:#1e293b;padding:30px;border-radius:12px;border:2px solid #f59e0b;max-width:500px;margin:0 auto;}}h1{{color:#f59e0b;}}.alvo{{font-size:48px;color:#22c55e;margin:20px 0;}}a{{color:#f59e0b;display:block;margin-top:20px;}}</style></head><body>
<div class="caixa"><h1>🃏 JOGO DAS CARTAS</h1>
<p>Fase {session['cartas_fase']}/4 · Pontos: {session['cartas_pontos']}</p>
<p>Qual carta corresponde a:</p>
<div class="alvo">{alvo}</div>
<form method="POST"><input type="hidden" name="alvo" value="{alvo}">{botoes}</form>
<a href="/plataforma">← Voltar</a></div></body></html>"""

@app.route("/plataforma", methods=["GET","POST"])
def plataforma():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("SELECT id,nome,pontos,dna_chave,email FROM usuarios WHERE id = ?", (session["usuario_id"],))
    u = c.fetchone()
    conn.close()
    if not u:
        session.clear()
        return redirect(url_for("inicio"))
    usuario_id, nome, pontos, dna_chave, email = u
    botao_admin = '<a href="/area_privada" style="background:#dc2626;color:#fff;padding:5px 10px;border-radius:5px;text-decoration:none;font-size:12px;margin-left:10px;">🔒 Dono</a>' if email.lower() == EMAIL_DONO.lower() else ''
    return f"""
<!DOCTYPE html><html lang="pt-br"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Plataforma — JNB TECNOLOGIA</title>
<style>*{{margin:0;padding:0;box-sizing:border-box;}}body{{background:#0f172a;color:#e2e8f0;font-family:Arial,sans-serif;min-height:100vh;}}.topo{{background:#1e293b;padding:15px 20px;display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #f59e0b;}}.topo h1{{color:#f59e0b;font-size:22px;}}.topo .dados{{text-align:right;}}.topo .pontos{{color:#f59e0b;font-weight:bold;}}.abas{{display:flex;gap:5px;padding:10px;background:#1e293b;flex-wrap:wrap;}}.aba{{padding:10px 15px;border:none;border-radius:6px 6px 0 0;cursor:pointer;font-weight:bold;}}.aba.ativa{{background:#f59e0b;color:#000;}}.aba.inativa{{background:#334155;color:#cbd5e1;}}.conteudo{{padding:20px;max-width:800px;margin:0 auto;}}.bloco{{background:#1e293b;padding:20px;border-radius:10px;border:1px solid #334155;margin-bottom:20px;}}.bloco h2{{color:#f59e0b;margin-bottom:15px;font-size:18px;}}textarea,input{{width:100%;padding:10px;background:#0f172a;border:1px solid #475569;color:#fff;border-radius:6px;margin-bottom:10px;}}button{{padding:10px 20px;border:none;border-radius:6px;font-weight:bold;cursor:pointer;}}.btn-verde{{background:#22c55e;color:#fff;}}.btn-azul{{background:#3b82f6;color:#fff;}}.btn-vermelho{{background:#ef4444;color:#fff;}}.oculto{{display:none !important;}}.post{{background:#0f172a;padding:15px;border-radius:8px;margin-bottom:10px;}}.curtir{{color:#94a3b8;text-decoration:none;}}.curtir:hover{{color:#f59e0b;}}</style></head><body>

<div class="topo"><h1>⚡ JNB TECNOLOGIA</h1><div class="dados"><p>Olá, {nome} {botao_admin}</p><p class="pontos">Pontos: {pontos:,}</p><a href="/sair" style="color:#f87171;font-size:14px;">Sair</a></div></div>

<div class="abas">
<button class="aba ativa" onclick="mudaAba('rede')">Rede Social</button>
<button class="aba inativa" onclick="mudaAba('jogos')">🎮 Jogos</button>
<button class="aba inativa" onclick="mudaAba('ia')">🤖 IA</button>
<button class="aba inativa" onclick="mudaAba('dna')">🧬 DNA</button>
</div>

<div class="conteudo">

<!-- REDE SOCIAL -->
<div id="aba-rede" class="bloco">
<h2>📢 Nova Postagem</h2>
<form method="POST" enctype="multipart/form-data">
<textarea name="texto_post" placeholder="Compartilhe algo..." rows="3"></textarea>
<input type="file" name="arquivo" accept="image/*,video/*">
<button type="submit" class="btn-verde">📤 Publicar</button>
</form>
</div>

<!-- JOGOS -->
<div id="aba-jogos" class="bloco oculto">
<h2>🎮 Área de Jogos</h2>
<p style="margin-bottom:15px;">Escolha o jogo:</p>
<a href="/jogo_bentinho" style="display:block;padding:15px;background:#f59e0b;color:#000;text-decoration:none;border-radius:8px;margin-bottom:10px;font-weight:bold;">🎮 Jogo Bentinho — Desafio dos Números</a>
<a href="/jogo_cartas" style="display:block;padding:15px;background:#3b82f6;color:#fff;text-decoration:none;border-radius:8px;font-weight:bold;">🃏 Jogo das Cartas — Desafio de Lógica</a>
</div>

<!-- IA -->
<div id="aba-ia" class="bloco oculto">
<h2>🤖 Assistente IA</h2>
<div id="conversa" style="background:#0f172a;padding:15px;border-radius:8px;height:300px;overflow-y:auto;margin-bottom:15px;"></div>
<form onsubmit="enviarIA(event)">
<input type="text" id="pergunta" placeholder="Faça sua pergunta..." required>
<button type="submit" class="btn-azul">Enviar</button>
</form>
</div>

<!-- 🧬 DNA — CORRIGIDO ✅ -->
<div id="aba-dna" class="bloco oculto">
<h2>🧬 Criptografia de Documentos</h2>
<p style="color:#94a3b8;margin-bottom:15px;">Sua chave única: <code style="background:#0f172a;padding:3px 8px;border-radius:4px;color:#f59e0b;">{dna_chave}</code></p>

<h3 style="color:#22c55e;margin:15px 0 5px 0;">🔒 Criptografar</h3>
<form onsubmit="cripto(event)">
<textarea id="txt_original" placeholder="Digite ou cole o texto..." rows="4" required></textarea>
<input type="text" id="chave_c" value="{dna_chave}" required>
<button type="submit" class="btn-verde">🔒 Criptografar</button>
</form>
<div style="margin-top:15px;">
<p style="color:#22c55e;font-weight:bold;">✅ Resultado — DNA:</p>
<textarea id="dna_result" readonly rows="6" placeholder="Aqui aparece o resultado..."></textarea>
<form action="/baixar_dna" method="POST">
<input type="hidden" id="dna_baixar" name="dna_texto">
<button type="submit" class="btn-azul">📥 Baixar .bnj</button>
</form>
</div>

<h3 style="color:#ef4444;margin:25px 0 5px 0;">🔓 Descriptografar</h3>
<form onsubmit="descripto(event)">
<textarea id="dna_entrada" placeholder="Cole o DNA criptografado..." rows="6" required></textarea>
<input type="text" id="chave_d" placeholder="Sua chave secreta" required>
<button type="submit" class="btn-vermelho">🔓 Descriptografar</button>
</form>
<div style="margin-top:15px;">
<p style="color:#22c55e;font-weight:bold;">✅ Texto Original:</p>
<textarea id="txt_final" readonly rows="6" placeholder="Aqui aparece o texto original..."></textarea>
</div>
</div>

</div>

<script>
function mudaAba(nome){{
document.querySelectorAll('.aba').forEach(b=>{{b.classList.remove('ativa');b.classList.add('inativa');}});
document.querySelectorAll('[id^="aba-"]').forEach(b=>{{b.classList.add('oculto');}});
event.target.classList.add('ativa');event.target.classList.remove('inativa');
document.getElementById('aba-'+nome).classList.remove('oculto');
}}

async function enviarIA(e){{
e.preventDefault();
const p = document.getElementById('pergunta').value;
const div = document.getElementById('conversa');
div.innerHTML += '<div style="margin:8px 0;"><strong style="color:#f59e0b;">Você:</strong> '+p+'</div>';
document.getElementById('pergunta').value = '';
const r = await fetch('/responder_ia',{{
method:'POST',headers:{{'Content-Type':'application/x-www-form-urlencoded'}},
body:'pergunta='+encodeURIComponent(p)
}});
const res = await r.text();
div.innerHTML += '<div style="margin:8px 0;"><strong style="color:#22c55e;">IA:</strong> '+res+'</div>';
div.scrollTop = div.scrollHeight;
}}

async function cripto(e){{
e.preventDefault();
const t = document.getElementById('txt_original').value;
const c = document.getElementById('chave_c').value;
const r = await fetch('/dna_criptografar',{{
method:'POST',headers:{{'Content-Type':'application/x-www-form-urlencoded'}},
body:'texto_original='+encodeURIComponent(t)+'&chave_usuario='+encodeURIComponent(c)
}});
const d = await r.text();
document.getElementById('dna_result').value = d;
document.getElementById('dna_baixar').value = d;
}}

async function descripto(e){{
e.preventDefault();
const d = document.getElementById('dna_entrada').value;
const c = document.getElementById('chave_d').value;
const r = await fetch('/dna_descriptografar',{{
method:'POST',headers:{{'Content-Type':'application/x-www-form-urlencoded'}},
body:'dna_codificado='+encodeURIComponent(d)+'&chave_usuario='+encodeURIComponent(c)
}});
document.getElementById('txt_final').value = await r.text();
}}
</script>
</body></html>"""

# ==================================================
# ✅ PORTA 5000 — INTACTA, NÃO MEXI!
# ==================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
