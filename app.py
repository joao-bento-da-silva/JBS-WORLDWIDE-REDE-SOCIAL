 # ==================================================
# © 2026 JBS TECHNOLOGY
# JBS WORLDWIDE — VERSÃO FINAL DEFINITIVA
# CHAVES EXATAS | IDADE | CENSURA | VISIBILIDADE
# NÃO ALTERA NADA DO QUE JÁ ESTÁ FUNCIONANDO
# ==================================================

from flask import Flask, request, session, redirect, url_for, render_template_string, send_from_directory
import sqlite3, os
from datetime import datetime, date
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ==================== SEGURANÇA — EXATAMENTE COMO NO SEU ORIGINAL ====================
CHAVE_MESTRA_DNA = os.environ.get("CHAVE_MESTRA_DNA")
CHAVE_INTERNA_SEGURANCA = os.environ.get("CHAVE_INTERNA_SEGURANCA")
app.secret_key = CHAVE_INTERNA_SEGURANCA
DATABASE = "jbs_worldwide.db"

# ==================== REGRAS GERAIS ====================
IDADE_MINIMA_CADASTRO = 13
UPLOAD_FOLDER = "arquivos_midia"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
TIPOS_PERMITIDOS = {"png", "jpg", "jpeg", "gif", "webp", "mp4", "webm", "mov"}

VISIBILIDADE = [
    ("publico", "🌐 Todos podem ver"),
    ("amigos", "👥 Apenas amigos"),
    ("privado", "🔒 Apenas eu")
]

FAIXA_ETARIA = [
    ("todos", "✅ Para todas as idades"),
    ("maior16", "🔞 A partir de 16 anos"),
    ("maior18", "🔞 Apenas maiores de 18 anos")
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
        "subtitulo": "Conectando pessoas, ideias e sonhos em todo o mundo",
        "criar_conta": "Criar Nova Conta",
        "entrar": "Entrar",
        "nome": "Nome completo",
        "nascimento": "Data de nascimento",
        "email": "Seu e-mail",
        "senha": "Crie uma senha",
        "acessar": "Acessar Conta",
        "ja_possui": "Já tenho conta",
        "nao_possui": "Não tenho conta ainda",
        "o_que_pensa": "O que você está pensando?",
        "publicar": "Publicar",
        "sair": "Sair",
        "erro_preencher": "Preencha todos os campos corretamente",
        "erro_idade": "É preciso ter pelo menos 13 anos para criar conta",
        "erro_email_existe": "Este e-mail já está cadastrado",
        "erro_dados": "E-mail ou senha incorretos",
        "sucesso_cadastro": "Conta criada! Faça login para continuar",
        "erro_conteudo": "Conteúdo não permitido pela moderação"
    },
    "en": {
        "titulo": "JBS WORLDWIDE",
        "subtitulo": "Connecting people, ideas and dreams across the globe",
        "criar_conta": "Create New Account",
        "entrar": "Sign In",
        "nome": "Full name",
        "nascimento": "Date of birth",
        "email": "Your email",
        "senha": "Create a password",
        "acessar": "Sign In",
        "ja_possui": "Already have an account",
        "nao_possui": "Don't have an account yet",
        "o_que_pensa": "What's on your mind?",
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

# ==================== BANCO DE DADOS ====================
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
        c.execute('''CREATE TABLE curtidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            publicacao_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            UNIQUE(publicacao_id, usuario_id)
        )''')
        conn.commit()
        conn.close()

iniciar_banco()
def conectar(): return sqlite3.connect(DATABASE)
def logado(): return "usuario_id" in session

# ==================== PÁGINA INICIAL ====================
@app.route("/")
def inicio():
    t = IDIOMAS[pegar_idioma()]
    if logado(): return redirect(url_for("feed"))
    return render_template_string(f'''
    <!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{t["titulo"]}</title><style>
    *{{margin:0;padding:0;box-sizing:border-box;font-family:Arial}}
    body{{background:#020617;color:white;min-height:100vh;display:flex;align-items:center;justify-content:center}}
    .caixa{{text-align:center;max-width:500px;width:90%}}
    h1{{font-size:50px;color:#84cc16;margin-bottom:15px}}
    p{{font-size:18px;margin-bottom:30px;line-height:1.6}}
    .botao{{display:block;width:280px;padding:15px;margin:10px auto;border-radius:10px;text-decoration:none;font-weight:bold;font-size:17px}}
    .primario{{background:#84cc16;color:#020617}}
    .secundario{{border:2px solid #84cc16;color:#84cc16}}
    .lang{{position:absolute;top:20px;right:20px}}
    .lang a{{color:#84cc16;margin:0 5px;text-decoration:none}}
    </style></head><body>
    <div class="lang"><a href="/mudar-idioma/pt">PT</a> | <a href="/mudar-idioma/en">EN</a></div>
    <div class="caixa">
        <h1>{t["titulo"]}</h1><p>{t["subtitulo"]}</p>
        <a href="/cadastrar" class="botao primario">{t["criar_conta"]}</a>
        <a href="/entrar" class="botao secundario">{t["entrar"]}</a>
    </div></body></html>
    ''')

# ==================== CADASTRO COM IDADE ====================
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
    return render_template_string(f'''
    <html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{t["criar_conta"]}</title><style>
    body{{background:#0f172a;color:white;min-height:100vh;display:flex;align-items:center;justify-content:center}}
    .caixa{{width:90%;max-width:420px;background:#1e293b;padding:30px;border-radius:12px}}
    h2{{text-align:center;color:#84cc16;margin-bottom:20px}}
    .erro{{background:#991b1b;padding:10px;border-radius:8;margin-bottom:15px}}
    input{{width:100%;padding:14px;margin:8px 0;background:#334155;border:1px solid #475569;border-radius:8px;color:white}}
    button{{width:100%;padding:14px;background:#84cc16;border:none;border-radius:8px;font-weight:bold;font-size:17px}}
    a{{display:block;text-align:center;color:#94a3b8;margin-top:15px;text-decoration:none}}
    </style></head><body><div class="caixa">
    <h2>{t["criar_conta"]}</h2>{f"<div class='erro'>{erro}</div>" if erro else ""}
    <form method="POST">
    <input type="text" name="nome" placeholder="{t["nome"]}" required>
    <input type="date" name="nascimento" required>
    <input type="email" name="email" placeholder="{t["email"]}" required>
    <input type="password" name="senha" placeholder="{t["senha"]}" required minlength="6">
    <button>{t["criar_conta"]}</button>
    <a href="/entrar">{t["ja_possui"]}</a><a href="/">← Voltar</a>
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
    body{{background:#0f172a;color:white;min-height:100vh;display:flex;align-items:center;justify-content:center}}
    .caixa{{width:90%;max-width:420px;background:#1e293b;padding:30px;border-radius:12px}}
    h2{{text-align:center;color:#84cc16;margin-bottom:20px}}
    .ok{{background:#14532d;padding:10px;border-radius:8;margin-bottom:15px}}
    .erro{{background:#991b1b;padding:10px;border-radius:8;margin-bottom:15px}}
    input{{width:100%;padding:14px;margin:8px 0;background:#334155;border:1px solid #475569;border-radius:8px;color:white}}
    button{{width:100%;padding:14px;background:#84cc16;border:none;border-radius:8px;font-weight:bold}}
    a{{display:block;text-align:center;color:#94a3b8;margin-top:15px;text-decoration:none}}
    </style></head><body><div class="caixa">
    <h2>{t["entrar"]}</h2>{f"<div class='ok'>{msg}</div>" if msg else ""}{f"<div class='erro'>{erro}</div>" if erro else ""}
    <form method="POST">
    <input type="email" name="email" placeholder="{t["email"]}" required>
    <input type="password" name="senha" placeholder="Senha" required>
    <button>{t["acessar"]}</button>
    <a href="/cadastrar">{t["nao_possui"]}</a><a href="/">← Voltar</a>
    </form></div></body></html>
    ''')

# ==================== FEED COMPLETO ====================
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
        html_pubs += f"<div style='background:#1e293b;padding:18px;border-radius:10px;margin-bottom:18px;'>"
        html_pubs += f"<strong style='color:#84cc16;'>{p[1]}</strong>"
        html_pubs += f"<p style='margin:12px 0;'>{p[2] if p[2] else ''}</p>"
        if p[5]:
            if p[6] in ["png","jpg","jpeg","gif","webp"]:
                html_pubs += f"<img src='/midia/{p[5]}' style='max-width:100%;border-radius:8px;'>"
            else:
                html_pubs += f"<video controls src='/midia/{p[5]}' style='max-width:100%;border-radius:8px;'></video>"
        html_pubs += f"<br><small style='color:#94a3b8;'>Quem vê: {p[3]} | Faixa etária: {p[4]}</small></div>"
    
    return render_template_string(f'''
    <html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Feed — JBS WORLDWIDE</title><style>
    *{{margin:0;padding:0;box-sizing:border-box;font-family:Arial}}
    body{{background:#0f172a;color:white;padding:20px;max-width:720px;margin:0 auto}}
    .topo{{display:flex;justify-content:space-between;align-items:center;padding-bottom:20px;border-bottom:1px solid #334155}}
    .topo h1{{color:#84cc16}}
    .sair{{color:#ef4444;text-decoration:none;font-weight:bold}}
    .form{{background:#1e293b;padding:20px;border-radius:10px;margin:25px 0}}
    textarea, select, input{{width:100%;padding:12px;margin:8px 0;background:#334155;border:none;border-radius:8px;color:white;font-size:15px}}
    button{{padding:12px 25px;background:#84cc16;border:none;border-radius:8px;font-weight:bold;color:#020617}}
    </style></head><body>
    <div class="topo"><h1>JBS WORLDWIDE</h1><a href="/sair" class="sair">{t["sair"]}</a></div>
    <div class="form">
    <form method="POST" enctype="multipart/form-data">
    <textarea name="texto" rows="3" placeholder="{t["o_que_pensa"]}"></textarea>
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
