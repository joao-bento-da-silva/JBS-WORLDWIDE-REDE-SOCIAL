 # ==================================================
# © 2026 JBS TECNOLOGIA
# VERSÃO FINAL — DESIGN OFICIAL + CADASTRO CORRIGIDO
# ==================================================

from flask import Flask, request, session, redirect, url_for, render_template_string, send_from_directory
import sqlite3, os
from datetime import datetime, date
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ==================== SEGURANCA ====================
CHAVE_MESTRA_DNA = os.environ.get("CHAVE_MESTRA_DNA")
CHAVE_INTERNA_SEGURANCA = os.environ.get("CHAVE_INTERNA_SEGURANCA")
app.secret_key = CHAVE_INTERNA_SEGURANCA
DATABASE = "jbs_worldwide.db"

# ==================== REGRAS ====================
IDADE_MINIMA_CADASTRO = 13
UPLOAD_FOLDER = "arquivos_midia"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
TIPOS_PERMITIDOS = {"png", "jpg", "jpeg", "gif", "webp", "mp4", "webm", "mov"}

VISIBILIDADE = [
    ("publico", "Todos podem ver"),
    ("amigos", "Apenas amigos"),
    ("privado", "Apenas eu")
]

FAIXA_ETARIA = [
    ("todos", "Para todas as idades"),
    ("maior16", "A partir de 16 anos"),
    ("maior18", "Apenas maiores de 18 anos")
]

PALAVRAS_PROIBIDAS = ["palavra1", "palavra2", "palavra3"]

def verificar_conteudo(texto):
    if not texto: return True
    texto = texto.lower()
    for p in PALAVRAS_PROIBIDAS:
        if p.lower() in texto: return False
    return True

def calcular_idade(data_nasc):
    nasc = datetime.strptime(data_nasc, "%Y-%m-%d").date()
    hoje = date.today()
    return hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))

# ==================== IDIOMAS ====================
IDIOMAS = {
    "pt": {
        "titulo": "JBS WORLDWIDE",
        "subtitulo": "Inovacao e Credibilidade",
        "criar_conta": "Criar Nova Conta",
        "entrar": "Entrar",
        "nome": "Nome completo",
        "nascimento": "Data de nascimento",
        "email": "Seu e-mail",
        "senha": "Crie uma senha",
        "acessar": "Acessar Conta",
        "ja_possui": "Ja tenho conta",
        "nao_possui": "Nao tenho conta ainda",
        "o_que_pensa": "O que voce esta pensando?",
        "publicar": "Publicar",
        "sair": "Sair",
        "erro_preencher": "Preencha todos os campos corretamente",
        "erro_idade": "E preciso ter pelo menos 13 anos para criar conta",
        "erro_email_existe": "Este e-mail ja esta cadastrado",
        "erro_dados": "E-mail ou senha incorretos",
        "sucesso_cadastro": "Conta criada! Faca login para continuar",
        "erro_conteudo": "Conteudo nao permitido"
    },
    "en": {
        "titulo": "JBS WORLDWIDE",
        "subtitulo": "Innovation and Trust",
        "criar_conta": "Create New Account",
        "entrar": "Sign In",
        "nome": "Full name",
        "nascimento": "Date of birth",
        "email": "Your email",
        "senha": "Create a password",
        "acessar": "Sign In",
        "ja_possui": "Already have an account",
        "nao_possui": "Do not have an account yet",
        "o_que_pensa": "What is on your mind?",
        "publicar": "Post",
        "sair": "Sign Out",
        "erro_preencher": "Please fill all fields correctly",
        "erro_idade": "You must be at least 13 years old",
        "erro_email_existe": "This email is already registered",
        "erro_dados": "Incorrect email or password",
        "sucesso_cadastro": "Account created! Sign in",
        "erro_conteudo": "Content not allowed"
    }
}

def pegar_idioma():
    return session.get("idioma", request.accept_languages.best_match(["pt","en"]) or "pt")

@app.route("/mudar-idioma/<lang>")
def mudar(lang):
    if lang in IDIOMAS: session["idioma"] = lang
    return redirect(request.referrer or url_for("inicio"))

# ==================== BANCO ====================
def iniciar_banco():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            nascimento TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute('''CREATE TABLE publicacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            texto TEXT,
            arquivo TEXT,
            tipo_arquivo TEXT,
            visibilidade TEXT DEFAULT 'publico',
            faixa_etaria TEXT DEFAULT 'todos',
            data_publicacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )''')
        conn.commit()
        conn.close()

iniciar_banco()
def conectar(): return sqlite3.connect(DATABASE)
def logado(): return "usuario_id" in session

# ==================== PAGINA INICIAL — DESIGN OFICIAL ====================
@app.route("/")
def inicio():
    t = IDIOMAS[pegar_idioma()]
    if logado(): return redirect(url_for("feed"))
    return render_template_string(f'''
    <!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{t["titulo"]}</title><style>
    *{{margin:0;padding:0;box-sizing:border-box;font-family:Arial}}
    body{{background:linear-gradient(135deg,#020617 0%,#051020 40%,#03141a 100%);color:white;min-height:100vh;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden}}
    body::before{{content:"";position:absolute;inset:0;background-image:radial-gradient(circle at 25% 25%, rgba(34,197,94,0.06) 0%, transparent 55%),radial-gradient(circle at 75% 75%, rgba(59,130,246,0.08) 0%, transparent 55%);z-index:0}}
    .caixa{{position:relative;z-index:1;text-align:center;max-width:540px;width:90%;padding:45px 35px;background:rgba(8,18,35,0.9);border-radius:18px;border:1px solid rgba(34,197,94,0.25);box-shadow:0 0 50px rgba(59,130,246,0.12), 0 0 50px rgba(34,197,94,0.12)}}
    .logo{{font-size:30px;font-weight:800;color:#22c55e;margin-bottom:12px;letter-spacing:3px;text-align:left}}
    h1{{font-size:52px;color:#22c55e;margin-bottom:18px}}
    p{{font-size:19px;margin-bottom:40px;line-height:1.8;color:#cbd5e1}}
    .botao{{display:block;width:100%;padding:18px;margin:14px auto;border-radius:14px;text-decoration:none;font-weight:bold;font-size:19px;transition:all 0.3s ease}}
    .primario{{background:linear-gradient(90deg,#22c55e,#15803d);color:#020617;border:none;box-shadow:0 4px 20px rgba(34,197,94,0.35)}}
    .primario:hover{{transform:translateY(-3px);box-shadow:0 8px 25px rgba(34,197,94,0.45)}}
    .secundario{{border:2px solid #22c55e;color:#22c55e;background:transparent}}
    .secundario:hover{{background:rgba(34,197,94,0.1)}}
    .lang{{position:absolute;top:25px;right:25px;z-index:2}}
    .lang a{{color:#60a5fa;margin:0 8px;text-decoration:none;font-weight:500}}
    </style></head><body>
    <div class="lang"><a href="/mudar-idioma/pt">PT</a> | <a href="/mudar-idioma/en">EN</a></div>
    <div class="caixa">
        <div class="logo">JBS TECNOLOGIA</div>
        <h1>{t["titulo"]}</h1>
        <p>{t["subtitulo"]}</p>
        <a href="/cadastrar" class="botao primario">{t["criar_conta"]}</a>
        <a href="/entrar" class="botao secundario">{t["entrar"]}</a>
    </div></body></html>
    ''')

# ==================== CADASTRO — CORRIGIDO 100% ====================
@app.route("/cadastrar", methods=["GET","POST"])
def cadastrar():
    t = IDIOMAS[pegar_idioma()]; erro=""
    if request.method == "POST":
        n = request.form["nome"].strip()
        nas = request.form["nascimento"].strip()
        e = request.form["email"].strip().lower()
        s = request.form["senha"].strip()
        
        if not n or not nas or not e or not s:
            erro = t["erro_preencher"]
        else:
            try:
                idade = calcular_idade(nas)
                if idade < IDADE_MINIMA_CADASTRO:
                    erro = t["erro_idade"]
                else:
                    conn = conectar()
                    try:
                        conn.execute("INSERT INTO usuarios VALUES (NULL,?,?,?, ?, CURRENT_TIMESTAMP)", (n,nas,e,s))
                        conn.commit()
                        return redirect(url_for("entrar", msg=t["sucesso_cadastro"]))
                    except:
                        erro = t["erro_email_existe"]
                    conn.close()
            except:
                erro = "Data invalida! Escolha no calendario"
    
    return render_template_string(f'''
    <html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{t["criar_conta"]}</title><style>
    *{{margin:0;padding:0;box-sizing:border-box;font-family:Arial}}
    body{{background:linear-gradient(135deg,#020617 0%,#051020 40%,#03141a 100%);color:white;min-height:100vh;display:flex;align-items:center;justify-content:center}}
    .caixa{{width:90%;max-width:480px;background:rgba(8,18,35,0.9);padding:40px;border-radius:18px;border:1px solid rgba(34,197,94,0.25);box-shadow:0 0 50px rgba(59,130,246,0.12)}}
    h2{{text-align:center;color:#22c55e;margin-bottom:28px;font-size:28px}}
    .erro{{background:#b91c1c;color:white;padding:16px;border-radius:12px;margin-bottom:22px;text-align:center;font-weight:bold;border:1px solid rgba(220,38,38,0.35)}}
    input{{width:100%;padding:16px;margin:12px 0;background:rgba(10,30,55,0.8);border:1px solid rgba(96,165,250,0.3);border-radius:12px;color:white;font-size:17px}}
    input:focus{{outline:none;border-color:#22c55e;box-shadow:0 0 10px rgba(34,197,94,0.35)}}
    button{{width:100%;padding:16px;background:linear-gradient(90deg,#22c55e,#15803d);border:none;border-radius:12px;font-weight:bold;font-size:19px;color:#020617;box-shadow:0 4px 20px rgba(34,197,94,0.35);margin-top:10px}}
    a{{display:block;text-align:center;color:#60a5fa;margin-top:20px;text-decoration:none;font-size:16px}}
    </style></head><body><div class="caixa">
    <h2>{t["criar_conta"]}</h2>
    {f'<div class="erro">{erro}</div>' if erro else ''}
    <form method="POST">
    <input type="text" name="nome" placeholder="{t["nome"]}" required>
    <input type="date" name="nascimento" required>
    <input type="email" name="email" placeholder="{t["email"]}" required>
    <input type="password" name="senha" placeholder="{t["senha"]}" required minlength="6">
    <button>{t["criar_conta"]}</button>
    <a href="/entrar">{t["ja_possui"]}</a>
    <a href="/">Voltar</a>
    </form></div></body></html>
    ''')

# ==================== LOGIN ====================
@app.route("/entrar", methods=["GET","POST"])
def entrar():
    t = IDIOMAS[pegar_idioma()]; msg=request.args.get("msg",""); erro=""
    if request.method == "POST":
        e = request.form["email"].strip().lower()
        s = request.form["senha"].strip()
        conn = conectar()
        u = conn.execute("SELECT id FROM usuarios WHERE email=? AND senha=?", (e,s)).fetchone()
        conn.close()
        if u:
            session["usuario_id"] = u[0]
            return redirect(url_for("feed"))
        erro = t["erro_dados"]
    return render_template_string(f'''
    <html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{t["entrar"]}</title><style>
    *{{margin:0;padding:0;box-sizing:border-box;font-family:Arial}}
    body{{background:linear-gradient(135deg,#020617 0%,#051020 40%,#03141a 100%);color:white;min-height:100vh;display:flex;align-items:center;justify-content:center}}
    .caixa{{width:90%;max-width:480px;background:rgba(8,18,35,0.9);padding:40px;border-radius:18px;border:1px solid rgba(34,197,94,0.25);box-shadow:0 0 50px rgba(59,130,246,0.12)}}
    h2{{text-align:center;color:#22c55e;margin-bottom:28px;font-size:28px}}
    .ok{{background:#166534;color:white;padding:16px;border-radius:12px;margin-bottom:22px;text-align:center;border:1px solid rgba(22,163,74,0.35)}}
    .erro{{background:#b91c1c;color:white;padding:16px;border-radius:12px;margin-bottom:22px;text-align:center;border:1px solid rgba(220,38,38,0.35)}}
    input{{width:100%;padding:16px;margin:12px 0;background:rgba(10,30,55,0.8);border:1px solid rgba(96,165,250,0.3);border-radius:12px;color:white;font-size:17px}}
    button{{width:100%;padding:16px;background:linear-gradient(90deg,#22c55e,#15803d);border:none;border-radius:12px;font-weight:bold;font-size:19px;color:#020617;box-shadow:0 4px 20px rgba(34,197,94,0.35);margin-top:10px}}
    a{{display:block;text-align:center;color:#60a5fa;margin-top:20px;text-decoration:none}}
    </style></head><body><div class="caixa">
    <h2>{t["entrar"]}</h2>
    {f'<div class="ok">{msg}</div>' if msg else ''}
    {f'<div class="erro">{erro}</div>' if erro else ''}
    <form method="POST">
    <input type="email" name="email" placeholder="{t["email"]}" required>
    <input type="password" name="senha" placeholder="Senha" required>
    <button>{t["acessar"]}</button>
    <a href="/cadastrar">{t["nao_possui"]}</a>
    <a href="/">Voltar</a>
    </form></div></body></html>
    ''')

# ==================== FEED ====================
@app.route("/feed", methods=["GET","POST"])
def feed():
    if not logado(): return redirect(url_for("entrar"))
    t = IDIOMAS[pegar_idioma()]
    if request.method == "POST":
        texto = request.form.get("texto","").strip()
        vis = request.form.get("visibilidade","publico")
        faixa = request.form.get("faixa_etaria","todos")
        arq = request.files.get("arquivo")
        nome_arq = tipo_arq = None
        
        if not verificar_conteudo(texto):
            return redirect(url_for("feed", erro=t["erro_conteudo"]))
        
        if arq and arq.filename:
            ext = arq.filename.rsplit(".",1)[1].lower()
            if ext in TIPOS_PERMITIDOS:
                nome_arq = secure_filename(arq.filename)
                arq.save(os.path.join(UPLOAD_FOLDER, nome_arq))
                tipo_arq = ext
        
        conn = conectar()
        conn.execute("INSERT INTO publicacoes VALUES (NULL,?,?,?,?,?, CURRENT_TIMESTAMP)",
                     (session["usuario_id"],texto,vis,faixa,nome_arq,tipo_arq))
        conn.commit()
        conn.close()
        return redirect(url_for("feed"))
    
    conn = conectar()
    pubs = conn.execute('''
        SELECT p.*, u.nome FROM publicacoes p 
        JOIN usuarios u ON p.usuario_id = u.id
        WHERE p.visibilidade = 'publico' OR p.usuario_id = ?
        ORDER BY p.data_publicacao DESC
    ''', (session["usuario_id"],)).fetchall()
    conn.close()
    
    html_pubs = ""
    for p in pubs:
        html_pubs += f"<div style='background:rgba(8,18,35,0.9);padding:22px;border-radius:16px;margin-bottom:22px;border:1px solid rgba(96,165,250,0.25);box-shadow:0 2px 15px rgba(0,0,0,0.3)'>"
        html_pubs += f"<strong style='color:#22c55e;font-size:18px;'>{p[1]}</strong>"
        html_pubs += f"<p style='margin:16px 0;color:#e2e8f0;line-height:1.7;'>{p[2] if p[2] else ''}</p>"
        if p[5]:
            if p[6] in ["png","jpg","jpeg","gif","webp"]:
                html_pubs += f"<img src='/midia/{p[5]}' style='max-width:100%;border-radius:12px;margin:12px 0;'>"
            else:
                html_pubs += f"<video controls src='/midia/{p[5]}' style='max-width:100%;border-radius:12px;margin:12px 0;'></video>"
        html_pubs += f"<br><small style='color:#94a3b8;'>Quem ve: {p[3]} | Faixa etaria: {p[4]}</small></div>"
    
    return render_template_string(f'''
    <html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Feed — JBS WORLDWIDE</title><style>
    *{{margin:0;padding:0;box-sizing:border-box;font-family:Arial}}
    body{{background:linear-gradient(135deg,#020617 0%,#051020 40%,#03141a 100%);color:white;padding:25px;max-width:780px;margin:0 auto}}
    .topo{{display:flex;justify-content:space-between;align-items:center;padding-bottom:22px;border-bottom:1px solid rgba(34,197,94,0.25)}}
    .topo h1{{color:#22c55e;font-size:26px}}
    .sair{{color:#ef4444;text-decoration:none;font-weight:bold;font-size:17px}}
    .form{{background:rgba(8,18,35,0.9);padding:22px;border-radius:16px;margin:28px 0;border:1px solid rgba(34,197,94,0.25)}}
    textarea, select, input{{width:100%;padding:14px;margin:10px 0;background:rgba(10,30,55,0.8);border:1px solid rgba(96,165,250,0.3);border-radius:10px;color:white;font-size:16px}}
    button{{padding:14px 28px;background:linear-gradient(90deg,#22c55e,#15803d);border:none;border-radius:10px;font-weight:bold;font-size:17px;color:#020617;box-shadow:0 4px 15px rgba(34,197,94,0.35)}}
    </style></head><body>
    <div class="topo"><h1>JBS WORLDWIDE</h1><a href="/sair" class="sair">{t["sair"]}</a></div>
    <div class="form">
    <form method="POST" enctype="multipart/form-data">
    <textarea name="texto" rows="4" placeholder="{t["o_que_pensa"]}"></textarea>
    <select name="visibilidade">
    {"".join([f"<option value='{v[0]}'>{v[1]}</option>" for v in VISIBILIDADE])}
    </select>
    <select name="faixa_etaria">
    {"".join([f"<option value='{f[0]}'>{f[1]}</option>" for f in FAIXA_ETARIA])}
    </select>
    <input type="file" name="arquivo" accept="image/*,video/*">
    <button type="submit">{t["publicar"]}</button>
    </form></div>
    {html_pubs}
    </body></html>
    ''')

@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("inicio"))

@app.route("/midia/<nome>")
def midia(nome):
    return send_from_directory(UPLOAD_FOLDER, nome)

if __name__ == "__main__":
    app.run(debug=False)
