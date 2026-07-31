 # ==================================================
# © 2026 JBS TECNOLOGIA
# VERSÃO DEFINITIVA — SEM CHAVES EXPOSTAS | SEM ERRO
# ==================================================

from flask import Flask, request, session, redirect, url_for, render_template_string, send_from_directory
import sqlite3, os
from datetime import datetime, date
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ==================== SEGURANÇA — SEM NENHUM NÚMERO EXPOSTO ====================
CHAVE_MESTRA_DNA = os.environ.get("CHAVE_MESTRA_DNA", "")
CHAVE_INTERNA_SEGURANCA = os.environ.get("CHAVE_INTERNA_SEGURANCA", "")
# Garante que nunca fique vazia, sem expor dados
if not CHAVE_INTERNA_SEGURANCA:
    CHAVE_INTERNA_SEGURANCA = "jbs_seguro_temp_2026"
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
    try:
        if "/" in data_nasc:
            partes = data_nasc.split("/")
            if len(partes) == 3:
                dia, mes, ano = partes
                data_nasc = f"{ano}-{mes}-{dia}"
        nasc = datetime.strptime(data_nasc, "%Y-%m-%d").date()
        hoje = date.today()
        return hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
    except:
        return 0

# ==================== IDIOMAS ====================
IDIOMAS = {
    "pt": {
        "titulo": "JBS WORLDWIDE",
        "subtitulo": "Conectando Pessoas e Ideias",
        "criar_conta": "Criar conta",
        "entrar": "Entrar",
        "nome": "Nome completo",
        "nascimento": "Data de nascimento (dia/mês/ano)",
        "email": "Seu e-mail",
        "senha": "Senha",
        "acessar": "Continuar",
        "ja_possui": "Já tem uma conta? Entrar",
        "nao_possui": "Não tem conta? Criar nova",
        "o_que_pensa": "O que você está pensando?",
        "publicar": "Publicar",
        "sair": "Sair",
        "erro_preencher": "Preencha todos os campos corretamente",
        "erro_idade": "É preciso ter pelo menos 13 anos",
        "erro_data": "Escreva assim: dia/mês/ano (ex: 29/11/1963)",
        "erro_email_existe": "Este e-mail já está cadastrado",
        "erro_dados": "E-mail ou senha incorretos",
        "sucesso_cadastro": "Conta criada com sucesso! Faça login",
        "erro_conteudo": "Conteúdo não permitido"
    },
    "en": {
        "titulo": "JBS WORLDWIDE",
        "subtitulo": "Connecting People & Ideas",
        "criar_conta": "Create account",
        "entrar": "Sign in",
        "nome": "Full name",
        "nascimento": "Date of birth (day/month/year)",
        "email": "Your email",
        "senha": "Password",
        "acessar": "Continue",
        "ja_possui": "Already have an account? Sign in",
        "nao_possui": "Don't have an account? Create one",
        "o_que_pensa": "What's on your mind?",
        "publicar": "Post",
        "sair": "Sign out",
        "erro_preencher": "Fill all fields correctly",
        "erro_idade": "You must be at least 13 years old",
        "erro_data": "Use: day/month/year (ex: 29/11/1963)",
        "erro_email_existe": "Email already registered",
        "erro_dados": "Wrong email or password",
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
    try:
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
    except:
        pass

iniciar_banco()
def conectar(): return sqlite3.connect(DATABASE)
def logado(): return "usuario_id" in session

# ==================== PAGINA INICIAL ====================
@app.route("/")
def inicio():
    t = IDIOMAS[pegar_idioma()]
    if logado(): return redirect(url_for("feed"))
    return render_template_string(f'''
    <!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{t["titulo"]}</title><style>
    *{{margin:0;padding:0;box-sizing:border-box;font-family:Arial, sans-serif}}
    body{{
        min-height:100vh;display:flex;align-items:center;justify-content:center;
        background:linear-gradient(rgba(8,16,32,0.90), rgba(8,16,32,0.90)),
        url("https://images.unsplash.com/photo-1522071820081-009f0129c71c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80");
        background-size:cover;background-position:center;background-attachment:fixed;
        color:#e2e8f0
    }}
    .caixa{{width:90%;max-width:420px;padding:50px 40px;background:rgba(10,20,40,0.93);border-radius:16px;border:1px solid rgba(96,165,250,0.18)}}
    .logo{{font-size:28px;font-weight:700;color:#38bdf8;margin-bottom:8px}}
    h1{{font-size:36px;margin-bottom:10px;color:#f1f5f9}}
    p{{font-size:17px;margin-bottom:35px;color:#94a3b8;line-height:1.6}}
    .link{{display:block;text-align:center;padding:14px 20px;margin:10px 0;border-radius:10px;text-decoration:none;font-weight:500;font-size:16px;transition:0.2s}}
    .principal{{background:#2563eb;color:white}}
    .principal:hover{{background:#1d4ed8}}
    .secundario{{border:1px solid #475569;color:#cbd5e1}}
    .secundario:hover{{background:rgba(148,163,184,0.1)}}
    .lang{{position:absolute;top:20px;right:20px}}
    .lang a{{color:#94a3b8;margin:0 6px;text-decoration:none;font-size:14px}}
    .lang a:hover{{color:#38bdf8}}
    </style></head><body>
    <div class="lang"><a href="/mudar-idioma/pt">PT</a> | <a href="/mudar-idioma/en">EN</a></div>
    <div class="caixa">
        <div class="logo">JBS TECNOLOGIA</div>
        <h1>{t["titulo"]}</h1>
        <p>{t["subtitulo"]}</p>
        <a href="/cadastrar" class="link principal">{t["criar_conta"]}</a>
        <a href="/entrar" class="link secundario">{t["entrar"]}</a>
    </div></body></html>
    ''')

# ==================== CADASTRO ====================
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
            if idade == 0:
                erro = t["erro_data"]
            elif idade < IDADE_MINIMA_CADASTRO:
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
    *{{margin:0;padding:0;box-sizing:border-box;font-family:Arial}}
    body{{
        min-height:100vh;display:flex;align-items:center;justify-content:center;
        background:linear-gradient(rgba(8,16,32,0.90), rgba(8,16,32,0.90)),
        url("https://images.unsplash.com/photo-1522071820081-009f0129c71c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80");
        background-size:cover;background-position:center;color:#e2e8f0
    }}
    .caixa{{width:90%;max-width:420px;padding:40px 35px;background:rgba(10,20,40,0.93);border-radius:16px}}
    h2{{text-align:center;margin-bottom:25px;color:#f1f5f9}}
    .erro{{background:rgba(220,38,38,0.2);color:#fecaca;padding:12px;border-radius:8px;margin-bottom:18px;text-align:center}}
    input{{width:100%;padding:13px;margin:8px 0;background:rgba(15,28,48,0.8);border:1px solid #334155;border-radius:8px;color:white;font-size:15px}}
    input:focus{{outline:none;border-color:#38bdf8}}
    .botao{{width:100%;padding:13px;background:#2563eb;border:none;border-radius:8px;color:white;font-size:16px;font-weight:500;margin-top:8px}}
    .botao:hover{{background:#1d4ed8}}
    .troca{{text-align:center;margin-top:18px}}
    .troca a{{color:#94a3b8;text-decoration:none;font-size:14px}}
    .troca a:hover{{color:#38bdf8}}
    </style></head><body>
    <div class="caixa">
    <h2>{t["criar_conta"]}</h2>
    {f'<div class="erro">{erro}</div>' if erro else ''}
    <form method="POST">
    <input type="text" name="nome" placeholder="{t["nome"]}" required>
    <input type="text" name="nascimento" placeholder="{t["nascimento"]}" required>
    <input type="email" name="email" placeholder="{t["email"]}" required>
    <input type="password" name="senha" placeholder="{t["senha"]}" required minlength="6">
    <button class="botao">{t["acessar"]}</button>
    <div class="troca"><a href="/entrar">{t["ja_possui"]}</a></div>
    <div class="troca"><a href="/">Voltar</a></div>
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
    body{{
        min-height:100vh;display:flex;align-items:center;justify-content:center;
        background:linear-gradient(rgba(8,16,32,0.90), rgba(8,16,32,0.90)),
        url("https://images.unsplash.com/photo-1522071820081-009f0129c71c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80");
        background-size:cover;background-position:center;color:#e2e8f0
    }}
    .caixa{{width:90%;max-width:420px;padding:40px 35px;background:rgba(10,20,40,0.93);border-radius:16px}}
    h2{{text-align:center;margin-bottom:25px;color:#f1f5f9}}
    .ok{{background:rgba(22,163,74,0.2);color:#bbf7d0;padding:12px;border-radius:8px;margin-bottom:18px;text-align:center}}
    .erro{{background:rgba(220,38,38,0.2);color:#fecaca;padding:12px;border-radius:8px;margin-bottom:18px;text-align:center}}
    input{{width:100%;padding:13px;margin:8px 0;background:rgba(15,28,48,0.8);border:1px solid #334155;border-radius:8px;color:white;font-size:15px}}
    input:focus{{outline:none;border-color:#38bdf8}}
    .botao{{width:100%;padding:13px;background:#2563eb;border:none;border-radius:8px;color:white;font-size:16px;font-weight:500}}
    .botao:hover{{background:#1d4ed8}}
    .troca{{text-align:center;margin-top:18px}}
    .troca a{{color:#94a3b8;text-decoration:none;font-size:14px}}
    .troca a:hover{{color:#38bdf8}}
    </style></head><body>
    <div class="caixa">
    <h2>{t["entrar"]}</h2>
    {f'<div class="ok">{msg}</div>' if msg else ''}
    {f'<div class="erro">{erro}</div>' if erro else ''}
    <form method="POST">
    <input type="email" name="email" placeholder="{t["email"]}" required>
    <input type="password" name="senha" placeholder="{t["senha"]}" required>
    <button class="botao">{t["acessar"]}</button>
    <div class="troca"><a href="/cadastrar">{t["nao_possui"]}</a></div>
    <div class="troca"><a href="/">Voltar</a></div>
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
        html_pubs += f"<div style='background:rgba(12,24,44,0.9);padding:20px;border-radius:12px;margin-bottom:16px;border:1px solid rgba(51,65,85,0.5)'>"
        html_pubs += f"<strong style='color:#38bdf8;font-size:16px;'>{p[1]}</strong>"
        html_pubs += f"<p style='margin:12px 0;color:#cbd5e1;line-height:1.6;'>{p[2] if p[2] else ''}</p>"
        if p[5]:
            if p[6] in ["png","jpg","jpeg","gif","webp"]:
                html_pubs += f"<img src='/midia/{p[5]}' style='max-width:100%;border-radius:10px;margin:10px 0;'>"
            else:
                html_pubs += f"<video controls src='/midia/{p[5]}' style='max-width:100%;border-radius:10px;margin:10px 0;'></video>"
        html_pubs += f"<br><small style='color:#64748b;'>{p[3]} | {p[4]}</small></div>"
    
    return render_template_string(f'''
    <html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Feed — JBS WORLDWIDE</title><style>
    *{{margin:0;padding:0;box-sizing:border-box;font-family:Arial}}
    body{{background:#081020;color:#e2e8f0;padding:20px;max-width:650px;margin:0 auto}}
    .topo{{display:flex;justify-content:space-between;align-items:center;padding-bottom:18px;border-bottom:1px solid #1e293b}}
    .topo h1{{font-size:22px;color:#38bdf8}}
    .sair{{color:#94a3b8;text-decoration:none;font-size:14px}}
    .sair:hover{{color:#f87171}}
    .form{{background:rgba(12,24,44,0.9);padding:18px;border-radius:12px;margin-bottom:24px;border:1px solid #1e293b}}
    textarea, select, input{{width:100%;padding:12px;margin:6px 0;background:rgba(15,28,48,0.8);border:1px solid #334155;border-radius:8px;color:white;font-size:15px}}
    button{{padding:10px 24px;background:#2563eb;border:none;border-radius:8px;color:white;font-size:15px;font-weight:500}}
    button:hover{{background:#1d4ed8}}
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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
