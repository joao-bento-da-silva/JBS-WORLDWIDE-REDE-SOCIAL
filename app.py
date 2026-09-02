 # ==================================================
# © 2026 JNB TECNOLOGIA — POSTAGENS CORRIGIDAS ✅
# ERRO DO FORMULÁRIO RESOLVIDO — enctype ADICIONADO!
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
BANCO_DADOS = "jnb_novo.db"

# 🔒 SEU E-MAIL AQUI
EMAIL_DONO = "seu_email@aqui.com"
SENHA_MESTRA_ACESSO = "JNB@2026#DONO"

def usuario_logado():
    return "usuario_id" in session

def eh_dono():
    if not usuario_logado(): return False
    try:
        conn = sqlite3.connect(BANCO_DADOS)
        c = conn.cursor()
        c.execute("SELECT email FROM usuarios WHERE id = ?", (session["usuario_id"],))
        u = c.fetchone()
        conn.close()
        return u and u[0].strip().lower() == EMAIL_DONO.lower()
    except: return False

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
        senha_hash TEXT NOT NULL, pontos INTEGER DEFAULT 0, dna_chave TEXT NOT NULL, data_cadastro TEXT NOT NULL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS postagens (
        id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER NOT NULL,
        texto TEXT, arquivo TEXT, data_postagem TEXT NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS curtidas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER NOT NULL, postagem_id INTEGER NOT NULL,
        UNIQUE(usuario_id, postagem_id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS conversas_ia (
        id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER NOT NULL,
        pergunta TEXT NOT NULL, resposta TEXT NOT NULL, data_hora TEXT NOT NULL
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
    if usuario_logado(): return redirect(url_for("plataforma"))
    return render_template_string('''<!DOCTYPE html>
<html lang="pt-br"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>JNB TECNOLOGIA</title>
<style>*{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif;}
body{background:linear-gradient(180deg,#0f172a,#1e293b);color:#e2e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center;}
.caixa{background:rgba(15,23,42,0.8);padding:40px;border-radius:12px;border:1px solid #f59e0b;width:90%;max-width:400px;}
h1{color:#f59e0b;text-align:center;margin-bottom:30px;}
input{width:100%;padding:12px;margin:8px 0;background:#020617;border:1px solid #334155;color:white;border-radius:6px;}
button{width:100%;padding:12px;background:#f59e0b;color:#1e1b16;border:none;border-radius:6px;font-weight:bold;cursor:pointer;}
.link{text-align:center;margin-top:15px;font-size:14px;color:#94a3b8;}
.link a{color:#f59e0b;text-decoration:none;}</style></head><body>
<div class="caixa"><h1>JNB TECNOLOGIA</h1>
<form action="/entrar" method="POST"><input type="email" name="email" placeholder="E-mail" required><input type="password" name="senha" placeholder="Senha" required><button type="submit">Entrar</button></form>
<div class="link">Não tem conta? <a href="/cadastrar">Cadastre-se — Permanente ✅</a></div></div></body></html>''')

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
                uid = c.lastrowid
                conn.close()
                session["usuario_id"] = uid
                session["nome_usuario"] = nome
                return redirect(url_for("plataforma"))
            except sqlite3.IntegrityError:
                return '''<div style="text-align:center;padding:50px;background:#0f172a;color:white;"><h2 style="color:red;">E-mail já cadastrado!</h2><a href="/cadastrar" style="color:#f59e0b;">Voltar</a></div>'''
    return render_template_string('''<!DOCTYPE html><html lang="pt-br"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Cadastrar</title>
<style>*{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif;}
body{background:linear-gradient(180deg,#0f172a,#1e293b);color:#e2e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center;}
.caixa{background:rgba(15,23,42,0.8);padding:40px;border-radius:12px;border:1px solid #f59e0b;width:90%;max-width:400px;}
h1{color:#f59e0b;text-align:center;margin-bottom:30px;}
input{width:100%;padding:12px;margin:8px 0;background:#020617;border:1px solid #334155;color:white;border-radius:6px;}
button{width:100%;padding:12px;background:#f59e0b;color:#1e1b16;border:none;border-radius:6px;font-weight:bold;cursor:pointer;}
.link{text-align:center;margin-top:15px;font-size:14px;color:#94a3b8;}
.link a{color:#f59e0b;text-decoration:none;}</style></head><body>
<div class="caixa"><h1>Cadastrar ✅ Permanente</h1>
<form method="POST"><input type="text" name="nome" placeholder="Seu nome" required><input type="email" name="email" placeholder="E-mail" required><input type="password" name="senha" placeholder="Senha" required><button type="submit">Cadastrar</button></form>
<div class="link">Já tem conta? <a href="/">Entrar</a></div></div></body></html>''')

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
    return '''<div style="text-align:center;padding:50px;background:#0f172a;color:white;"><h2 style="color:red;">E-mail ou senha inválidos!</h2><a href="/" style="color:#f59e0b;font-size:18px;">Voltar</a></div>'''

@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("inicio"))

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/area_privada", methods=["GET", "POST"])
def area_privada():
    if not usuario_logado(): return redirect(url_for("inicio"))
    if not eh_dono(): return '''<div style="text-align:center;padding:50px;background:#0f172a;color:white;"><h2 style="color:red;">🚫 ACESSO NEGADO</h2><a href="/plataforma" style="color:#f59e0b;">Voltar</a></div>'''
    if request.method == "POST":
        if request.form.get("senha_mestra") == SENHA_MESTRA_ACESSO: return redirect(url_for("painel_dono"))
        return '''<div style="text-align:center;padding:50px;background:#0f172a;color:white;"><h2 style="color:red;">❌ Senha incorreta!</h2><a href="/area_privada" style="color:#f59e0b;">Tentar novamente</a></div>'''
    return render_template_string('''<!DOCTYPE html><html lang="pt-br"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>🔒 Área Privada</title>
<style>body{background:linear-gradient(180deg,#0f172a,#1e293b);color:white;min-height:100vh;display:flex;align-items:center;justify-content:center;font-family:Arial,sans-serif;}
.caixa{background:rgba(15,23,42,0.9);padding:40px;border-radius:12px;border:2px solid #f59e0b;max-width:400px;width:90%;text-align:center;}
h1{color:#f59e0b;margin-bottom:20px;}
input{width:100%;padding:12px;margin:8px 0;background:#020617;border:1px solid #334155;color:white;border-radius:6px;}
button{width:100%;padding:12px;background:#f59e0b;color:black;border:none;border-radius:6px;font-weight:bold;cursor:pointer;}
a{color:#f59e0b;text-decoration:none;display:block;margin-top:20px;}</style></head><body>
<div class="caixa"><h1>🔒 ÁREA PRIVADA</h1><p style="margin-bottom:20px;">Confirme a senha mestra</p>
<form method="POST"><input type="password" name="senha_mestra" placeholder="Senha Mestra" required><button type="submit">🔓 Desbloquear</button></form><a href="/plataforma">← Voltar</a></div></body></html>''')

@app.route("/painel_dono")
def painel_dono():
    if not usuario_logado() or not eh_dono(): return redirect(url_for("inicio"))
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM usuarios")
    total_usuarios = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM postagens")
    total_postagens = c.fetchone()[0]
    conn.close()
    return render_template_string(f'''<!DOCTYPE html><html lang="pt-br"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>⚙️ Painel do Dono</title>
<style>body{{background:linear-gradient(180deg,#0f172a,#1e293b);color:#e2e8f0;min-height:100vh;font-family:Arial,sans-serif;padding:20px;max-width:800px;margin:0 auto;}}
h1{{color:#f59e0b;}}.card{{background:#1e293b;padding:20px;border-radius:10px;border:1px solid #f59e0b/30;flex:1;min-width:200px;}}
.row{{display:flex;gap:20px;flex-wrap:wrap;}}a{{color:#f59e0b;text-decoration:none;display:inline-block;margin-bottom:20px;}}</style></head><body>
<a href="/plataforma">← Voltar</a><h1>⚙️ PAINEL DO DONO</h1><div class="row">
<div class="card"><p style="color:#94a3b8;">Total de Usuários</p><p style="font-size:28px;font-weight:bold;color:#f59e0b;">{total_usuarios}</p></div>
<div class="card"><p style="color:#94a3b8;">Total de Postagens</p><p style="font-size:28px;font-weight:bold;color:#f59e0b;">{total_postagens}</p></div></div></body></html>''')

@app.route("/responder_ia", methods=["POST"])
def responder_ia_rota():
    if not usuario_logado(): return redirect(url_for("inicio"))
    pergunta = request.form.get("pergunta", "").strip()
    if not pergunta: return "Digite uma pergunta!"
    resposta = responder_ia(pergunta)
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("INSERT INTO conversas_ia (usuario_id, pergunta, resposta, data_hora) VALUES (?, ?, ?, ?)",
              (session["usuario_id"], pergunta, resposta, data_hora))
    conn.commit()
    conn.close()
    return resposta

@app.route("/jogo_cartas", methods=["GET", "POST"])
def jogo_cartas():
    if not usuario_logado(): return redirect(url_for("inicio"))
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
            if len(resposta) != len(alvo): msg = "❌ Selecione todas!"
            else:
                correta = [REGRAS[c] for c in alvo]
                if resposta == correta:
                    pontos += valor
                    session["cartas_pontos"] = pontos
                    msg = f"✅ ACERTOU! +{valor} PONTOS!"
                    try:
                        conn = sqlite3.connect(BANCO_DADOS)
                        c = conn.cursor()
                        c.execute("UPDATE usuarios SET pontos = pontos + ? WHERE id = ?", (valor, session["usuario_id"]))
                        conn.commit()
                        conn.close()
                    except: pass
                    if fase < 4: session["cartas_fase"] += 1; session.pop("cartas_alvo", None)
                    else: msg = "🏆 VENCEU!"; session["cartas_fase"] = 1; session.pop("cartas_alvo", None)
                else: msg = "❌ Errou!"; session["cartas_resposta"] = []
    alvo_html = "".join([f"<span style='background:#f59e0b;color:black;padding:12px 18px;border-radius:8px;margin:5px;font-size:24px;font-weight:bold;'>{c}</span>" for c in alvo])
    resp_html = "".join([f"<span style='background:#22c55e;color:black;padding:12px 18px;border-radius:8px;margin:5px;font-size:24px;font-weight:bold;'>{c}</span>" for c in resposta]) if resposta else "<p style='color:#94a3b8;'>Clique nas cartas...</p>"
    disp_html = "".join([f"<button type='submit' name='selecionar' value='{c}' style='background:#33415e;color:white;padding:12px 18px;border-radius:8px;margin:5px;font-size:24px;font-weight:bold;border:2px solid #f59e0b;cursor:pointer;'>{c}</button>" for c in CARTAS])
    return render_template_string(f'''<!DOCTYPE html><html lang="pt-br"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>🃏 Jogo das Cartas</title>
<style>body{{background:linear-gradient(180deg,#0f172a,#1e293b);color:#e2e8f0;min-height:100vh;font-family:Arial,sans-serif;padding:20px;max-width:800px;margin:0 auto;}}
a{{color:#f59e0b;text-decoration:none;}}h1{{color:#f59e0b;text-align:center;}}.box{{background:#1e293b;padding:20px;border-radius:10px;border:1px solid #f59e0b/30;margin:15px 0;}}
.msg{{padding:12px;border-radius:8px;text-align:center;font-weight:bold;margin:10px 0;}}.ok{{background:#166534;color:#bbf7d0;}}.erro{{background:#991b1b;color:#fecaca;}}
.btn{{padding:12px 20px;border:none;border-radius:8px;font-weight:bold;cursor:pointer;font-size:16px;}}.btn-green{{background:#16a34a;color:white;}}.btn-yellow{{background:#f59e0b;color:black;}}.btn-gray{{background:#475569;color:white;}}
.flex{{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;}}.btns{{display:flex;gap:15px;justify-content:center;margin-top:20px;}}</style></head><body>
<a href="/plataforma">← Voltar</a><h1>🃏 Jogo das Cartas</h1><p style="text-align:center;">Fase {fase}/4 · Pontos: {pontos}</p>
{ f'<div class="msg {"ok" if "✅" in msg or "🏆" in msg else "erro"}">{msg}</div>' if msg else '' }
<div class="box"><p style="text-align:center;color:#94a3b8;margin-bottom:10px;">🎯 Cartas Alvo:</p><div class="flex">{alvo_html}</div></div>
<div class="box"><p style="text-align:center;color:#94a3b8;margin-bottom:10px;">✅ Sua Resposta:</p><div class="flex">{resp_html}</div></div>
<form method="POST" class="box"><p style="text-align:center;color:#94a3b8;margin-bottom:10px;">🃏 Clique para selecionar:</p><div class="flex">{disp_html}</div></form>
<div class="btns"><form method="POST"><button type="submit" name="verificar" class="btn btn-green">✅ Verificar</button></form><form method="POST"><button type="submit" name="nova" class="btn btn-yellow">🔄 Novas</button></form></div></body></html>''')

@app.route("/jogo_bentinho", methods=["GET", "POST"])
def jogo_bentinho():
    if not usuario_logado():
        return redirect(url_for("inicio"))
    if not acesso_liberado():
        return render_template_string(LAYOUT, usuario_logado=usuario_logado, acesso_liberado=acesso_liberado, conteudo=bloqueio_servico("Jogo Bentinho", 0.00, "Descubra o segredo dos números!"))

    TABELA_SECRETA = {'0':'0','1':'9','2':'8','3':'7','4':'6','5':'5','6':'4','7':'3','8':'2','9':'1'}
    def converter(n): return "".join(TABELA_SECRETA[d] for d in n if d in TABELA_SECRETA)

    if "bent_fase" not in session or session.get("bent_fase") not in [1,2,3,4]:
        session["bent_fase"] = 1
    if "bent_pontos" not in session:
        session["bent_pontos"] = 0

    fase = session["bent_fase"]
    tamanho = {1:3,2:6,3:8,4:9}[fase]
    pontos_por_fase = {1:250000,2:2500000,3:25000000,4:1000000000}

    if "bent_numero" not in session or session.get("bent_ultima_fase") != fase:
        session["bent_numero"] = "".join(random.choice("0123456789") for _ in range(tamanho))
        session["bent_resposta"] = converter(session["bent_numero"])
        session["bent_ultima_fase"] = fase

    numero_exibido = session["bent_numero"]
    resposta_correta = session["bent_resposta"]
    mensagem = ""
    classe_msg = ""

    if request.method == "POST":
        if request.form.get("acao") == "sair":
            for chave in ["bent_fase","bent_pontos","bent_numero","bent_resposta","bent_ultima_fase"]:
                session.pop(chave, None)
            return redirect(url_for("pagina_jogos"))
        if request.form.get("acao") == "reiniciar":
            session["bent_fase"] = 1
            session["bent_pontos"] = 0
            session.pop("bent_numero", None)
            return redirect(url_for("jogo_bentinho"))
        resposta_usuario = request.form.get("resposta", "").strip()
        if resposta_usuario == resposta_correta:
            pts = pontos_por_fase[fase]
            session["bent_pontos"] += pts
            mensagem = "ACERTOU! +{:,} PONTOS!".format(pts)
            classe_msg = "ok"
            try:
                if "usuario_id" in session:
                    conn = sqlite3.connect("banco.db")
                    cur = conn.cursor()
                    cur.execute("UPDATE usuarios SET pontos = pontos + ? WHERE id = ?", (pts, session["usuario_id"]))
                    conn.commit()
                    conn.close()
            except:
                pass
            if fase < 4:
                session["bent_fase"] = fase + 1
                session.pop("bent_numero", None)
            else:
                mensagem = "PARABENS! VOCE VENCEU! 1000000000 DE PONTOS!"
                classe_msg = "ok"
                session["bent_fase"] = 1
                session.pop("bent_numero", None)
        else:
            mensagem = "ERROU! Descubra o segredo dos numeros!"
            classe_msg = "erro"

    estilo = "<style>.bent-box{background:#1e293b;padding:25px;border-radius:15px;border:2px solid #f59e0b;max-width:420px;margin:30px auto;}.bent-h2{color:#f59e0b;text-align:center;margin-top:0;}.bent-sub{text-align:center;color:#94a3b8;margin-bottom:20px;}.bent-num{font-size:40px;font-family:monospace;color:#facc15;text-align:center;padding:20px;background:#0f172a;border-radius:10px;margin:20px 0;letter-spacing:6px;}.bent-input{width:100%;padding:14px;font-size:22px;text-align:center;background:#0f172a;border:2px solid #f59e0b;border-radius:10px;color:#facc15;font-family:monospace;box-sizing:border-box;}.bent-flex{display:flex;gap:10px;margin-top:15px;flex-wrap:wrap;}.bent-btn{padding:12px 8px;border:none;border-radius:10px;font-weight:bold;cursor:pointer;flex:1;min-width:100px;font-size:15px;}.bent-btn-y{background:#f59e0b;color:#000;}.bent-btn-g{background:#475569;color:#fff;}.bent-btn-r{background:#b91c1c;color:#fff;}.bent-msg{padding:12px;border-radius:10px;text-align:center;font-weight:bold;margin:15px 0;}.bent-msg-ok{background:#166534;color:#bbf7d0;}.bent-msg-erro{background:#991b1b;color:#fecaca;}</style>"

    bloco_mensagem = ""
    if mensagem:
        bloco_mensagem = '<div class="bent-msg bent-msg-' + classe_msg + '">' + mensagem + '</div>'

    conteudo_completo = estilo + '<div class="bent-box"><h2 class="bent-h2">SEGREDO DOS NUMEROS</h2><p class="bent-sub">Fase ' + str(fase) + '/4 · Pontos: ' + str(session["bent_pontos"]) + '</p>' + bloco_mensagem + '<div class="bent-num">' + numero_exibido + '</div><form method="POST"><input type="text" name="resposta" class="bent-input" placeholder="Digite o numero correto" required autocomplete="off"><div class="bent-flex"><button type="submit" class="bent-btn bent-btn-y">Enviar</button><button type="submit" name="acao" value="reiniciar" class="bent-btn bent-btn-g">Reiniciar</button><button type="submit" name="acao" value="sair" class="bent-btn bent-btn-r">Sair</button></div></form></div>'

    return render_template_string(LAYOUT, usuario_logado=usuario_logado, acesso_liberado=acesso_liberado, conteudo=conteudo_completo)


@app.route("/baixar_dna", methods=["POST"])
def baixar_dna():
    ...

    if not usuario_logado(): return redirect(url_for("inicio"))
    dna_texto = request.form.get("dna_texto", "").strip()
    if not dna_texto: return "Nenhum DNA para baixar", 400
    conteudo = f"JNB-DNA-ENCRYPTED\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{dna_texto}"
    resp = make_response(conteudo)
    resp.headers["Content-Disposition"] = f"attachment; filename=documento_dna_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bnj"
    resp.headers["Content-Type"] = "application/octet-stream"
    return resp

# ==============================================
# 📤 PLATAFORMA + POSTAGENS — CORRIGIDO! ✅
# ==============================================
@app.route("/plataforma", methods=["GET", "POST"])
def plataforma():
    if not usuario_logado(): return redirect(url_for("inicio"))
    usuario_id = session["usuario_id"]
    
    # ✅ POSTAGEM — CORRIGIDA COM ENCTYPE!
    if request.method == "POST" and "texto_post" in request.form:
        texto = request.form.get("texto_post", "").strip()
        arquivo = request.files.get("arquivo")
        nome_arq = None
        
        if arquivo and arquivo.filename and arquivo.filename != "":
            if allowed_file(arquivo.filename):
                nome_arq = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{arquivo.filename}")
                caminho = os.path.join(app.config["UPLOAD_FOLDER"], nome_arq)
                arquivo.save(caminho)
            else:
                return render_template_string('''<!DOCTYPE html><body style="background:#0f172a;color:white;text-align:center;padding:50px;font-family:Arial;">
                    <h2 style="color:red;">❌ Formato inválido!</h2><p>Use: JPG, PNG, GIF, MP4, MOV, AVI, WEBM</p>
                    <a href="/plataforma" style="color:#f59e0b;font-size:20px;">← Voltar</a></body></html>''')
        
        if texto or nome_arq:
            try:
                conn = sqlite3.connect(BANCO_DADOS)
                c = conn.cursor()
                c.execute("INSERT INTO postagens (usuario_id, texto, arquivo, data_postagem) VALUES (?, ?, ?, ?)",
                          (usuario_id, texto, nome_arq, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
                return redirect(url_for("plataforma") + "?sucesso=1")
            except Exception as e:
                return f"Erro: {str(e)}"
        else:
            return render_template_string('''<!DOCTYPE html><body style="background:#0f172a;color:white;text-align:center;padding:50px;font-family:Arial;">
                <h2 style="color:orange;">⚠️ Escreva algo ou escolha um arquivo!</h2>
                <a href="/plataforma" style="color:#f59e0b;font-size:20px;">← Voltar</a></body></html>''')
    
    # ✅ MENSAGEM DE SUCESSO
    mensagem_sucesso = ""
    if request.args.get("sucesso") == "1":
        mensagem_sucesso = '<div style="background:#166534;color:#bbf7d0;padding:12px;border-radius:8px;margin:15px 0;font-weight:bold;text-align:center;">✅ Postado com sucesso!</div>'
    
    # ✅ CURTIR
    if "curtir" in request.args:
        pid = request.args.get("curtir")
        conn = sqlite3.connect(BANCO_DADOS)
        c = conn.cursor()
        try: c.execute("INSERT INTO curtidas (usuario_id, postagem_id) VALUES (?, ?)", (usuario_id, pid))
        except sqlite3.IntegrityError: c.execute("DELETE FROM curtidas WHERE usuario_id = ? AND postagem_id = ?", (usuario_id, pid))
        conn.commit()
        conn.close()
        return redirect(url_for("plataforma") + "#post-" + pid)
    
    # ✅ DADOS DO USUÁRIO
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("SELECT nome, pontos, dna_chave, email FROM usuarios WHERE id = ?", (usuario_id,))
    usuario_dados = c.fetchone()
    if not usuario_dados:
        conn.close(); session.clear()
        return redirect(url_for("inicio"))
    nome_usuario, total_pontos, dna_chave, email_usuario = usuario_dados
    
    # ✅ BUSCAR POSTAGENS
    c.execute("""SELECT p.id, p.texto, p.arquivo, p.data_postagem, u.nome,
               (SELECT COUNT(*) FROM curtidas c WHERE c.postagem_id = p.id) as total_curtidas,
               EXISTS(SELECT 1 FROM curtidas c WHERE c.postagem_id = p.id AND c.usuario_id = ?) as curtiu
               FROM postagens p JOIN usuarios u ON p.usuario_id = u.id ORDER BY p.data_postagem DESC""", (usuario_id,))
    postagens = c.fetchall()
    conn.close()
    
    # ✅ RENDERIZAR POSTAGENS
    posts_html = ""
    for p in postagens:
        pid, texto, arquivo, data, autor, curtidas, curtiu = p
        posts_html += f'''<div id="post-{pid}" style="background:#1e293b;padding:15px;border-radius:10px;border:1px solid #f59e0b/30;margin-bottom:15px;">
            <h4 style="color:#f59e0b;font-weight:bold;margin-bottom:5px;">{autor}</h4><p style="color:#94a3b8;font-size:12px;margin-bottom:10px;">{data}</p>'''
        if texto: posts_html += f'<p style="margin-bottom:10px;white-space:pre-wrap;">{texto}</p>'
        if arquivo:
            ext = arquivo.split(".")[-1].lower()
            if ext in ["jpg", "jpeg", "png", "gif"]:
                posts_html += f'<img src="/uploads/{arquivo}" style="max-width:100%;border-radius:8px;margin:10px 0;">'
            elif ext in ["mp4", "mov", "avi", "webm"]:
                posts_html += f'<video controls style="max-width:100%;border-radius:8px;margin:10px 0;"><source src="/uploads/{arquivo}" type="video/mp4"></video>'
        posts_html += f'''<div style="margin-top:12px;padding-top:12px;border-top:1px solid #334155;">
            <a href="/plataforma?curtir={pid}#post-{pid}" style="color:{'#ef4444' if curtiu else '#94a3b8'};text-decoration:none;">👍 {curtidas} Curtida{'s' if curtidas != 1 else ''}</a>
        </div></div>'''
    if not posts_html:
        posts_html = '<p style="text-align:center;color:#94a3b8;padding:30px;">Ainda não há postagens. Seja o primeiro!</p>'
    
    botao_admin = f'<a href="/area_privada" style="background:#dc2626;color:white;padding:8px 12px;border-radius:6px;text-decoration:none;font-size:14px;margin-left:10px;">🔒 Área Privada</a>' if email_usuario.strip().lower() == EMAIL_DONO.lower() else ""
    
    # ✅ TEMPLATE PRINCIPAL — ENCTYPE ADICIONADO NO FORMULÁRIO!
    return render_template_string(f'''<!DOCTYPE html><html lang="pt-br"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Plataforma — JNB TECNOLOGIA</title>
<style>body{{background:linear-gradient(180deg,#0f172a,#1e293b);color:#e2e8f0;min-height:100vh;font-family:Arial,sans-serif;margin:0;padding:20px;max-width:800px;margin:0 auto;}}
.top{{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #334155;padding-bottom:20px;margin-bottom:20px;flex-wrap:wrap;}}
h1{{color:#f59e0b;font-size:24px;margin:0;}}.pontos{{text-align:right;}}.pontos p{{margin:0;color:#94a3b8;font-size:14px;}}.pontos span{{color:#f59e0b;font-weight:bold;font-size:22px;}}
.tabs{{display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap;}}
.tab{{padding:10px 16px;border:none;border-radius:8px 8px 0 0;cursor:pointer;font-size:15px;}}.tab.ativo{{background:#f59e0b;color:black;font-weight:bold;}}.tab.inativo{{background:#334155;color:#cbd5e1;}}
.painel{{display:block;}}.painel.escondido{{display:none;}}
.form-box{{background:#1e293b;padding:15px;border-radius:10px;border:1px solid #f59e0b/30;margin-bottom:20px;}}
textarea{{width:100%;padding:12px;background:#0f172a;border:1px solid #334155;border-radius:8px;color:white;font-size:15px;min-height:100px;margin-bottom:12px;}}
.file-label{{background:#334155;padding:10px 14px;border-radius:6px;cursor:pointer;display:inline-block;margin-right:10px;}}button{{background:#f59e0b;color:black;border:none;padding:10px 20px;border-radius:6px;font-weight:bold;cursor:pointer;font-size:15px;}}
.alerta{{background:#7f1d1d;color:#fecaca;padding:12px;border-radius:8px;margin-bottom:20px;}}
.jogos-grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px;}}.jogo-card{{background:#1e293b;padding:25px;border-radius:10px;border:1px solid #f59e0b/30;text-align:center;}}
.jogo-card h3{{color:#f59e0b;font-size:22px;margin-bottom:10px;}}.jogo-card p{{color:#94a3b8;margin-bottom:20px;}}.jogo-btn{{background:#f59e0b;color:black;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:bold;display:inline-block;}}
.ia-box{{background:#1e293b;padding:20px;border-radius:10px;border:1px solid #f59e0b/30;}}.ia-chat{{background:#0f172a;padding:15px;border-radius:8px;height:250px;overflow-y:auto;margin-bottom:15px;}}
.ia-input{{width:100%;padding:12px;background:#0f172a;border:1px solid #334155;border-radius:8px;color:white;font-size:15px;margin-bottom:10px;}}
.dna-box{{background:#1e293b;padding:20px;border-radius:10px;border:1px solid #f59e0b/30;}}.dna-chave{{background:#0f172a;padding:8px 12px;border-radius:6px;color:#facc15;font-family:monospace;}}
a{{color:#f59e0b;text-decoration:none;}}.sair{{color:#f87171;margin-left:10px;}}</style></head><body>

<div class="top">
    <div><h1>⚡ JNB TECNOLOGIA</h1><p style="color:#94a3b8;margin:5px 0 0 0;">Bem-vindo, {nome_usuario}!</p></div>
    <div class="pontos"><p>Pontos</p><span>{total_pontos}</span><br><a href="/sair" class="sair">Sair</a>{botao_admin}</div>
</div>

<div class="tabs">
    <button class="tab ativo" onclick="abrirAba('rede', this)">Rede Social</button>
    <button class="tab inativo" onclick="abrirAba('jogo', this)">🎮 Jogos</button>
    <button class="tab inativo" onclick="abrirAba('ia', this)">🤖 IA</button>
    <button class="tab inativo" onclick="abrirAba('dna', this)">🧬 DNA</button>
</div>

<!-- 📤 ABA REDE SOCIAL — ENCTYPE ADICIONADO! ✅ -->
<div id="aba-rede" class="painel">
    {mensagem_sucesso}
    <div class="alerta">⚠️ Proibido: nudez, conteúdo sexual, violência, ódio, ilegal. Postagens inadequadas serão apagadas e usuário banido.</div>
    <div class="form-box">
        <form method="POST" enctype="multipart/form-data">  <!-- ✅ AQUI TAVA O ERRO — ENCTYPE ADICIONADO! -->
            <textarea name="texto_post" placeholder="Compartilhe algo..."></textarea>
            <div style="display:flex;align-items:center;flex-wrap:wrap;gap:10px;">
                <label class="file-label">📷 Foto/Vídeo<input type="file" name="arquivo" accept="image/*,video/*" style="display:none;"></label>
                <button type="submit">📤 Publicar ✅ Permanente</button>
            </div>
        </form>
    </div>
    {posts_html}
</div>

<div id="aba-jogo" class="painel escondido">
    <div class="jogos-grid">
        <div class="jogo-card"><h3>🎮 Jogo Bentinho</h3><p>4 fases · Até 1.000.000.000 de pontos!</p><a href="/jogo_bentinho" class="jogo-btn">▶️ Jogar</a></div>
        <div class="jogo-card"><h3>🃏 Jogo das Cartas</h3><p>4 fases · Até 1.000 pontos!</p><a href="/jogo_cartas" class="jogo-btn">▶️ Jogar</a></div>
    </div>
</div>

<div id="aba-ia" class="painel escondido">
    <div class="ia-box">
        <h3 style="color:#f59e0b;margin-top:0;">🤖 IA — Pergunte!</h3>
        <div id="ia-chat" class="ia-chat"></div>
        <form onsubmit="enviarIA(event)">
            <input type="text" id="pergunta-ia" class="ia-input" placeholder="Faça sua pergunta..." required>
            <button type="submit">Enviar</button>
        </form>
    </div>
</div>

<div id="aba-dna" class="painel escondido">
    <div class="dna-box">
        <h3 style="color:#f59e0b;margin-top:0;">🧬 DNA — Criptografia</h3>
        <p style="color:#94a3b8;">Sua chave única: <span class="dna-chave">{dna_chave}</span></p>
        <form method="POST" action="/baixar_dna">
            <textarea name="dna_texto" placeholder="Cole o texto criptografado aqui..." style="width:100%;padding:12px;background:#0f172a;border:1px solid #334155;border-radius:8px;color:white;font-size:15px;min-height:120px;margin:15px 0;"></textarea>
            <button type="submit">📥 Baixar .bnj — Salvar no celular</button>
        </form>
    </div>
</div>

<script>
function abrirAba(nome, botao) {{
    document.querySelectorAll('.painel').forEach(p => p.classList.add('escondido'));
    document.querySelectorAll('.tab').forEach(t => {{t.classList.remove('ativo');t.classList.add('inativo');}});
    document.getElementById('aba-' + nome).classList.remove('escondido');
    botao.classList.remove('inativo');
    botao.classList.add('ativo');
}}
async function enviarIA(e) {{
    e.preventDefault();
    const pergunta = document.getElementById('pergunta-ia').value;
    if(!pergunta) return;
    const chat = document.getElementById('ia-chat');
    chat.innerHTML += `<div style="background:#1e293b;padding:8px;border-radius:6px;margin-bottom:8px;"><strong style="color:#f59e0b;">Você:</strong> ${{pergunta}}</div>`;
    document.getElementById('pergunta-ia').value = '';
    const resp = await fetch('/responder_ia', {{method:'POST', body:new URLSearchParams({{pergunta}})}});
    const texto = await resp.text();
    chat.innerHTML += `<div style="background:#1e293b;padding:8px;border-radius:6px;margin-bottom:8px;"><strong style="color:#22c55e;">IA:</strong> ${{texto}}</div>`;
    chat.scrollTop = chat.scrollHeight;
}}
</script>

</body></html>''')

# ✅ PORTA 5000 — GARANTIDA!
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
