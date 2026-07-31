 # ==================================================
# © 2026 JBS TECNOLOGIA — REDE SOCIAL PROFISSIONAL
# VERSÃO CORRIGIDA — SEM ERROS DE ALINHAMENTO
# ==================================================

from flask import Flask, request, session, redirect, url_for, render_template_string, send_from_directory
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ==================== SEGURANÇA ====================
app.secret_key = os.environ.get("CHAVE_INTERNA_SEGURANCA", "192837465510918273647582910283")
CHAVE_MESTRA_DNA = os.environ.get("CHAVE_MESTRA_DNA", "21054551774858609435694112838216077829")

# ==================== CONFIGURAÇÕES ====================
IDADE_MINIMA = 13
PASTA_ARQUIVOS = "publicacoes"
os.makedirs(PASTA_ARQUIVOS, exist_ok=True)
FORMATOS_PERMITIDOS = {"png", "jpg", "jpeg", "gif", "webp", "mp4", "mov"}

# ==================== BANCO DE DADOS ====================
def conectar_banco():
    conn = sqlite3.connect("jbs_rede.db")
    conn.row_factory = sqlite3.Row
    return conn

def iniciar_banco():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        nascimento TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        data_cadastro TEXT NOT NULL
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS publicacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        nome_usuario TEXT NOT NULL,
        texto TEXT,
        arquivo TEXT,
        tipo_arquivo TEXT,
        data TEXT NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )''')
    conn.commit()
    conn.close()

iniciar_banco()

def logado():
    return "usuario_id" in session

# ==================== PÁGINA INICIAL ====================
@app.route("/")
def inicio():
    if logado():
        return redirect(url_for("feed"))
    return render_template_string('''
    <!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>JBS REDE</title>
    <style>
    *{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI', Roboto, sans-serif}
    body{background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);color:#f8fafc;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;position:relative;overflow:hidden}
    body::before{content:"";position:absolute;width:600px;height:600px;background:rgba(59,130,246,0.08);border-radius:50%;top:-200px;right:-150px}
    body::after{content:"";position:absolute;width:500px;height:500px;background:rgba(16,185,129,0.06);border-radius:50%;bottom:-150px;left:-100px}
    .caixa{width:100%;max-width:440px;background:rgba(15,23,42,0.85);backdrop-filter:blur(12px);border-radius:24px;padding:55px 40px;text-align:center;border:1px solid rgba(59,130,246,0.15);box-shadow:0 20px 60px rgba(0,0,0,0.35);position:relative;z-index:1}
    .logo{font-size:42px;font-weight:800;background:linear-gradient(90deg,#3b82f6,#10b981);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:12px}
    .slogan{color:#94a3b8;font-size:17px;margin-bottom:40px;line-height:1.6}
    .botao{display:block;width:100%;padding:16px;border-radius:14px;text-decoration:none;font-weight:600;margin:12px 0;border:none;font-size:16px;transition:all 0.3s ease;letter-spacing:0.3px}
    .principal{background:linear-gradient(90deg,#2563eb,#3b82f6);color:#fff;box-shadow:0 4px 15px rgba(37,99,235,0.3)}
    .principal:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(37,99,235,0.4)}
    .secundario{background:transparent;color:#cbd5e1;border:1px solid rgba(148,163,184,0.3)}
    .secundario:hover{background:rgba(59,130,246,0.1);border-color:#3b82f6;color:#bfdbfe}
    </style></head><body>
    <div class="caixa">
        <div class="logo">JBS REDE</div>
        <p class="slogan">Conectando pessoas e ideias</p>
        <a href="/cadastrar" class="botao principal">Criar nova conta</a>
        <a href="/entrar" class="botao secundario">Entrar na minha conta</a>
    </div></body></html>
    ''')

# ==================== CADASTRO ====================
@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    erro = ""
    if request.method == "POST":
        nome = request.form["nome"].strip()
        nascimento = request.form["nascimento"].strip()
        email = request.form["email"].strip().lower()
        senha = request.form["senha"].strip()
        
        if not nome or not nascimento or not email or not senha:
            erro = "Preencha todos os campos"
        else:
            try:
                d, m, a = map(int, nascimento.split("/"))
                data_nasc = datetime(a, m, d).date()
                idade = datetime.today().year - data_nasc.year - ((datetime.today().month, datetime.today().day) < (data_nasc.month, data_nasc.day))
                if idade < IDADE_MINIMA:
                    erro = f"É preciso ter pelo menos {IDADE_MINIMA} anos"
                else:
                    conn = conectar_banco()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO usuarios (nome, nascimento, email, senha, data_cadastro) VALUES (?, ?, ?, ?, ?)",
                                  (nome, nascimento, email, senha, datetime.now().strftime("%d/%m/%Y %H:%M")))
                    conn.commit()
                    conn.close()
                    return redirect(url_for("entrar", ok="Conta criada com sucesso!"))
            except sqlite3.IntegrityError:
                erro = "Este e-mail já está cadastrado"
            except:
                erro = "Data inválida — use: dia/mês/ano"
    
    return render_template_string(f'''
    <!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Criar Conta — JBS REDE</title>
    <style>
    *{{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI'}}
    body{{background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);color:#f8fafc;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}}
    .caixa{{width:100%;max-width:420px;background:rgba(15,23,42,0.85);backdrop-filter:blur(12px);border-radius:24px;padding:45px 35px;border:1px solid rgba(59,130,246,0.15)}}
    h2{{text-align:center;margin-bottom:25px;color:#3b82f6}}
    .erro{{background:rgba(220,38,38,0.15);color:#fca5a5;padding:12px;border-radius:10px;margin-bottom:15px;text-align:center}}
    input{{width:100%;padding:14px;margin:8px 0;background:#0f172a;border:1px solid #374151;border-radius:12px;color:#fff;font-size:15px}}
    input:focus{{outline:none;border-color:#3b82f6}}
    .botao{{width:100%;padding:14px;background:linear-gradient(90deg,#2563eb,#3b82f6);border:none;border-radius:12px;color:#fff;font-size:16px;font-weight:600;margin-top:8px}}
    .link{{text-align:center;margin-top:20px}}
    .link a{{color:#94a3b8;text-decoration:none}}
    </style></head><body>
    <div class="caixa">
        <h2>Criar Conta</h2>
        {f'<div class="erro">{erro}</div>' if erro else ''}
        <form method="POST">
            <input type="text" name="nome" placeholder="Nome completo" required>
            <input type="text" name="nascimento" placeholder="Nascimento: dia/mês/ano" required>
            <input type="email" name="email" placeholder="Seu melhor e-mail" required>
            <input type="password" name="senha" placeholder="Senha (mínimo 6 caracteres)" required minlength="6">
            <button class="botao">Criar minha conta</button>
            <div class="link"><a href="/entrar">Já tenho conta</a></div>
            <div class="link"><a href="/">Voltar</a></div>
        </form>
    </div></body></html>
    ''')

# ==================== LOGIN ====================
@app.route("/entrar", methods=["GET", "POST"])
def entrar():
    ok = request.args.get("ok", "")
    erro = ""
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        senha = request.form["senha"].strip()
        conn = conectar_banco()
        usuario = conn.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?", (email, senha)).fetchone()
        conn.close()
        if usuario:
            session["usuario_id"] = usuario["id"]
            session["nome"] = usuario["nome"]
            return redirect(url_for("feed"))
        else:
            erro = "E-mail ou senha incorretos"
    
    return render_template_string(f'''
    <!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Entrar — JBS REDE</title>
    <style>
    *{{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI'}}
    body{{background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);color:#f8fafc;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}}
    .caixa{{width:100%;max-width:420px;background:rgba(15,23,42,0.85);backdrop-filter:blur(12px);border-radius:24px;padding:45px 35px;border:1px solid rgba(59,130,246,0.15)}}
    h2{{text-align:center;margin-bottom:25px;color:#3b82f6}}
    .ok{{background:rgba(16,185,129,0.15);color:#86efac;padding:12px;border-radius:10px;margin-bottom:15px;text-align:center}}
    .erro{{background:rgba(220,38,38,0.15);color:#fca5a5;padding:12px;border-radius:10px;margin-bottom:15px;text-align:center}}
    input{{width:100%;padding:14px;margin:8px 0;background:#0f172a;border:1px solid #374151;border-radius:12px;color:#fff}}
    .botao{{width:100%;padding:14px;background:linear-gradient(90deg,#2563eb,#3b82f6);border:none;border-radius:12px;color:#fff;font-weight:600}}
    .link{{text-align:center;margin-top:20px}}
    .link a{{color:#94a3b8}}
    </style></head><body>
    <div class="caixa">
        <h2>Entrar</h2>
        {f'<div class="ok">{ok}</div>' if ok else ''}
        {f'<div class="erro">{erro}</div>' if erro else ''}
        <form method="POST">
            <input type="email" name="email" placeholder="Seu e-mail" required>
            <input type="password" name="senha" placeholder="Sua senha" required>
            <button class="botao">Acessar</button>
            <div class="link"><a href="/cadastrar">Criar nova conta</a></div>
            <div class="link"><a href="/">Voltar</a></div>
        </form>
    </div></body></html>
    ''')

# ==================== FEED ====================
@app.route("/feed", methods=["GET", "POST"])
def feed():
    if not logado():
        return redirect(url_for("inicio"))
    
    if request.method == "POST":
        texto = request.form.get("texto", "").strip()
        arquivo = request.files.get("arquivo")
        nome_arq = tipo_arq = None
        
        if arquivo and arquivo.filename:
            ext = arquivo.filename.rsplit(".", 1)[1].lower() if "." in arquivo.filename else ""
            if ext in FORMATOS_PERMITIDOS:
                nome_arq = secure_filename(f"{datetime.now().timestamp()}_{arquivo.filename}")
                arquivo.save(os.path.join(PASTA_ARQUIVOS, nome_arq))
                tipo_arq = ext
        
        if texto or nome_arq:
            conn = conectar_banco()
            conn.execute("INSERT INTO publicacoes (usuario_id, nome_usuario, texto, arquivo, tipo_arquivo, data) VALUES (?, ?, ?, ?, ?, ?)",
                        (session["usuario_id"], session["nome"], texto, nome_arq, tipo_arq, datetime.now().strftime("%d/%m/%Y %H:%M")))
            conn.commit()
            conn.close()
        return redirect(url_for("feed"))
    
    conn = conectar_banco()
    posts = conn.execute("SELECT * FROM publicacoes ORDER BY id DESC").fetchall()
    conn.close()
    
    html_posts = ""
    for p in posts:
        html_posts += f"<div style='background:rgba(15,23,42,0.85);border-radius:16px;padding:20px;margin-bottom:15px;border:1px solid rgba(59,130,246,0.15)'>"
        html_posts += f"<strong style='color:#3b82f6;font-size:16px'>{p['nome_usuario']}</strong><br><small style='color:#6b7280'>{p['data']}</small>"
        if p["texto"]: html_posts += f"<p style='margin:10px 0;color:#e2e8f0'>{p['texto']}</p>"
        if p["arquivo"]:
            if p["tipo"] in ["png","jpg","jpeg","gif","webp"]:
                html_posts += f"<img src='/midia/{p['arquivo']}' style='max-width:100%;border-radius:10px;margin-top:8px'>"
            else:
                html_posts += f"<video controls src='/midia/{p['arquivo']}' style='max-width:100%;border-radius:10px;margin-top:8px'></video>"
        html_posts += "</div>"
    
    return render_template_string(f'''
    <!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Feed — JBS REDE</title>
    <style>
    *{{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI'}}
    body{{background:#0f172a;color:#e2e8f0;padding:20px;max-width:650px;margin:0 auto}}
    .topo{{display:flex;justify-content:space-between;align-items:center;padding-bottom:15px;border-bottom:1px solid #1e293b;margin-bottom:20px}}
    .topo h1{{font-size:24px;color:#3b82f6}}
    .sair{{color:#94a3b8;text-decoration:none}}
    .nova{{background:rgba(15,23,42,0.85);border-radius:16px;padding:18px;margin-bottom:20px;border:1px solid rgba(59,130,246,0.15)}}
    textarea, input{{width:100%;padding:12px;margin:6px 0;background:#0f172a;border:1px solid #374151;border-radius:10px;color:#fff}}
    button{{padding:10px 22px;background:linear-gradient(90deg,#2563eb,#3b82f6);border:none;border-radius:10px;color:#fff;font-weight:600}}
    </style></head><body>
    <div class="topo">
        <h1>JBS REDE</h1>
        <a href="/sair" class="sair">Sair</a>
    </div>
    <div class="nova">
        <form method="POST" enctype="multipart/form-data">
            <textarea name="texto" rows="3" placeholder="O que você está pensando?"></textarea>
            <input type="file" name="arquivo" accept="image/*,video/*">
            <button>Publicar</button>
        </form>
    </div>
    {html_posts}
    </body></html>
    ''')

# ==================== ARQUIVOS ====================
@app.route("/midia/<nome>")
def ver_midia(nome):
    return send_from_directory(PASTA_ARQUIVOS, nome)

# ==================== SAIR ====================
@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("inicio"))

# ==================== EXECUÇÃO ====================
if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta)
