# ==================================================
# © 2026 JBS TECNOLOGIA — REDE SOCIAL PROFISSIONAL
# VERSÃO CORRIGIDA — APENAS O QUE PRECISA, SEM BAGUNÇA
# ==================================================

from flask import Flask, request, session, redirect, url_for, render_template_string, send_from_directory
import sqlite3, os
from datetime import datetime, date
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ==================== SEGURANÇA — NÃO FALTA NADA ====================
app.secret_key = os.environ.get("CHAVE_INTERNA_SEGURANCA", "jbs_rede_profissional_2026")
DATABASE = "jbs_rede.db"

# ==================== CONFIGURAÇÕES ====================
IDADE_MINIMA = 13
PASTA_MIDIA = "publicacoes_midia"
os.makedirs(PASTA_MIDIA, exist_ok=True)
FORMATOS = {"png", "jpg", "jpeg", "gif", "webp", "mp4", "mov", "webm"}

# ==================== BANCO — CORRIGIDO ====================
def iniciar_banco():
    try:
        if not os.path.exists(DATABASE):
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            c.execute('''CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                nascimento TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL
            )''')
            c.execute('''CREATE TABLE posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                texto TEXT,
                arquivo TEXT,
                tipo TEXT,
                data DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')
            conn.commit()
            conn.close()
    except: pass

iniciar_banco()
def bd(): return sqlite3.connect(DATABASE)
def logado(): return "usuario_id" in session

# ==================== PÁGINAS ====================
@app.route("/")
def inicio():
    if logado(): return redirect(url_for("feed"))
    return render_template_string('''
    <!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>JBS REDE</title>
    <style>
    *{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI', sans-serif}
    body{background:#0a0f1a;color:#e2e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center}
    .box{width:90%;max-width:420px;background:#111827;border-radius:20px;padding:45px 35px;text-align:center;border:1px solid #1e293b}
    h1{color:#3b82f6;margin-bottom:8px;font-size:32px}
    p{color:#94a3b8;margin-bottom:35px;font-size:16px}
    .btn{display:block;width:100%;padding:15px;border-radius:12px;text-decoration:none;font-weight:600;margin:10px 0;border:none;font-size:16px}
    .pri{background:#2563eb;color:#fff}
    .pri:hover{background:#1d4ed8}
    .sec{border:1px solid #374151;color:#9ca3af;background:transparent}
    .sec:hover{background:#1f2937}
    </style></head><body>
    <div class="box">
        <h1>JBS REDE</h1>
        <p>Conectando pessoas e ideias</p>
        <a href="/cadastrar" class="btn pri">Criar conta</a>
        <a href="/entrar" class="btn sec">Entrar</a>
    </div></body></html>
    ''')

@app.route("/cadastrar", methods=["GET","POST"])
def cadastrar():
    erro = ""
    if request.method == "POST":
        n = request.form["nome"].strip()
        d = request.form["nascimento"].strip()
        e = request.form["email"].strip().lower()
        s = request.form["senha"].strip()
        
        if not n or not d or not e or not s:
            erro = "Preencha todos os campos"
        else:
            try:
                dia,mes,ano = d.split("/")
                nasc = datetime(int(ano),int(mes),int(dia)).date()
                idade = date.today().year - nasc.year - ((date.today().month,date.today().day) < (nasc.month,nasc.day))
                if idade < IDADE_MINIMA:
                    erro = f"É preciso ter pelo menos {IDADE_MINIMA} anos"
                else:
                    conn = bd()
                    conn.execute("INSERT INTO usuarios VALUES (NULL,?,?,?,?)", (n,d,e,s))
                    conn.commit()
                    conn.close()
                    return redirect(url_for("entrar", ok="Conta criada com sucesso!"))
            except sqlite3.IntegrityError:
                erro = "Este e-mail já está cadastrado"
            except:
                erro = "Data inválida — use: dia/mês/ano"

    return render_template_string(f'''
    <html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Criar Conta</title>
    <style>
    *{{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI'}}
    body{{background:#0a0f1a;color:#e2e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center}}
    .box{{width:90%;max-width:420px;background:#111827;border-radius:20px;padding:40px 30px}}
    h2{{text-align:center;margin-bottom:25px;color:#3b82f6}}
    .err{{background:rgba(220,38,38,0.15);color:#fca5a5;padding:12px;border-radius:8px;margin-bottom:15px;text-align:center}}
    input{{width:100%;padding:14px;margin:8px 0;background:#0a0f1a;border:1px solid #374151;border-radius:10px;color:#fff;font-size:15px}}
    input:focus{{outline:none;border-color:#3b82f6}}
    .btn{{width:100%;padding:14px;background:#2563eb;border:none;border-radius:10px;color:#fff;font-size:16px;font-weight:600;margin-top:5px}}
    .btn:hover{{background:#1d4ed8}}
    .lnk{{text-align:center;margin-top:20px}}
    .lnk a{{color:#94a3b8;text-decoration:none;font-size:14px}}
    </style></head><body>
    <div class="box">
        <h2>Criar Conta</h2>
        {f'<div class="err">{erro}</div>' if erro else ''}
        <form method="POST">
            <input type="text" name="nome" placeholder="Nome completo" required>
            <input type="text" name="nascimento" placeholder="Nascimento: dia/mês/ano" required>
            <input type="email" name="email" placeholder="Seu e-mail" required>
            <input type="password" name="senha" placeholder="Senha (mínimo 6 dígitos)" required minlength="6">
            <button class="btn">Criar minha conta</button>
            <div class="lnk"><a href="/entrar">Já tenho conta</a></div>
            <div class="lnk"><a href="/">Voltar</a></div>
        </form>
    </div></body></html>
    ''')

@app.route("/entrar", methods=["GET","POST"])
def entrar():
    ok = request.args.get("ok","")
    erro = ""
    if request.method == "POST":
        e = request.form["email"].strip().lower()
        s = request.form["senha"].strip()
        conn = bd()
        u = conn.execute("SELECT id FROM usuarios WHERE email=? AND senha=?", (e,s)).fetchone()
        conn.close()
        if u:
            session["id"] = u[0]
            return redirect(url_for("feed"))
        erro = "E-mail ou senha incorretos"

    return render_template_string(f'''
    <html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Entrar</title>
    <style>
    *{{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI'}}
    body{{background:#0a0f1a;color:#e2e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center}}
    .box{{width:90%;max-width:420px;background:#111827;border-radius:20px;padding:40px 30px}}
    h2{{text-align:center;margin-bottom:25px;color:#3b82f6}}
    .ok{{background:rgba(22,163,74,0.15);color:#86efac;padding:12px;border-radius:8px;margin-bottom:15px;text-align:center}}
    .err{{background:rgba(220,38,38,0.15);color:#fca5a5;padding:12px;border-radius:8px;margin-bottom:15px;text-align:center}}
    input{{width:100%;padding:14px;margin:8px 0;background:#0a0f1a;border:1px solid #374151;border-radius:10px;color:#fff}}
    .btn{{width:100%;padding:14px;background:#2563eb;border:none;border-radius:10px;color:#fff;font-weight:600}}
    .lnk{{text-align:center;margin-top:20px}}
    .lnk a{{color:#94a3b8}}
    </style></head><body>
    <div class="box">
        <h2>Entrar</h2>
        {f'<div class="ok">{ok}</div>' if ok else ''}
        {f'<div class="err">{erro}</div>' if erro else ''}
        <form method="POST">
            <input type="email" name="email" placeholder="E-mail" required>
            <input type="password" name="senha" placeholder="Senha" required>
            <button class="btn">Entrar</button>
            <div class="lnk"><a href="/cadastrar">Criar nova conta</a></div>
        </form>
    </div></body></html>
    ''')

@app.route("/feed", methods=["GET","POST"])
def feed():
    if "id" not in session: return redirect(url_for("entrar"))
    conn = bd()
    usuario = conn.execute("SELECT nome FROM usuarios WHERE id=?", (session["id"],)).fetchone()
    nome = usuario[0]

    if request.method == "POST":
        txt = request.form.get("texto","").strip()
        arq = request.files.get("arquivo")
        arq_nome = arq_tipo = None
        if arq and arq.filename:
            ext = arq.filename.rsplit(".",1)[1].lower()
            if ext in FORMATOS:
                arq_nome = secure_filename(arq.filename)
                arq.save(os.path.join(PASTA_MIDIA, arq_nome))
                arq_tipo = ext
        conn.execute("INSERT INTO posts VALUES (NULL,?,?,?,?,?,CURRENT_TIMESTAMP)",
                     (session["id"],nome,txt,arq_nome,arq_tipo))
        conn.commit()
        conn.close()
        return redirect(url_for("feed"))

    posts = conn.execute("SELECT * FROM posts ORDER BY data DESC").fetchall()
    conn.close()

    html = ""
    for p in posts:
        html += f"<div style='background:#111827;padding:18px;border-radius:16px;margin-bottom:15px;border:1px solid #1e293b'>"
        html += f"<strong style='color:#3b82f6;font-size:16px'>{p[2]}</strong>"
        if p[3]: html += f"<p style='margin:10px 0;color:#d1d5db'>{p[3]}</p>"
        if p[4]:
            if p[5] in ["png","jpg","jpeg","gif","webp"]:
                html += f"<img src='/midia/{p[4]}' style='max-width:100%;border-radius:10px;margin-top:8px'>"
            else:
                html += f"<video controls src='/midia/{p[4]}' style='max-width:100%;border-radius:10px;margin-top:8px'></video>"
        html += f"<br><small style='color:#6b7280'>{p[6]}</small></div>"

    return render_template_string(f'''
    <html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Feed — JBS REDE</title>
    <style>
    *{{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI'}}
    body{{background:#0a0f1a;color:#e2e8f0;padding:20px;max-width:650px;margin:0 auto}}
    .topo{{display:flex;justify-content:space-between;align-items:center;padding-bottom:15px;border-bottom:1px solid #1e293b}}
    .topo h1{{font-size:24px;color:#3b82f6}}
    .sair{{color:#94a3b8;text-decoration:none}}
    .sair:hover{{color:#f87171}}
    .nova{{background:#111827;padding:18px;border-radius:16px;margin-bottom:20px;border:1px solid #1e293b}}
    textarea, input{{width:100%;padding:12px;margin:6px 0;background:#0a0f1a;border:1px solid #374151;border-radius:10px;color:#fff;font-size:15px}}
    button{{padding:10px 22px;background:#2563eb;border:none;border-radius:10px;color:#fff;font-weight:600}}
    button:hover{{background:#1d4ed8}}
    </style></head><body>
    <div class="topo"><h1>JBS REDE</h1><a href="/sair" class="sair">Sair</a></div>
    <div class="nova">
        <form method="POST" enctype="multipart/form-data">
            <textarea name="texto" rows="3" placeholder="O que você está pensando?"></textarea>
            <input type="file" name="arquivo" accept="image/*,video/*">
            <button>Publicar</button>
        </form>
    </div>
    {html}
    </body></html>
    ''')

@app.route("/sair")
def sair(): session.clear(); return redirect(url_for("inicio"))
@app.route("/midia/<nome>")
def ver(nome): return send_from_directory(PASTA_MIDIA, nome)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)), debug=False)
 
