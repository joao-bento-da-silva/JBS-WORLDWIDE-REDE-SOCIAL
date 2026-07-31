
# ==================================================
# © 2026 JBS TECNOLOGIA / JBS WORLDWIDE
# TODOS OS DIREITOS RESERVADOS
# CRIADOR: JBS TECNOLOGIA
# PROJETO EXCLUSIVO — REPRODUÇÃO PROIBIDA
# ==================================================

from flask import Flask, request, session, redirect, url_for, render_template_string, send_from_directory
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ==================== SEGURANÇA — CHAVES NO RENDER ====================
SECRET_KEY = os.environ.get("JBS_WORLD_KEY", "21054551774858609435694112838216077829")
app.secret_key = SECRET_KEY
DATABASE = "jbs_worldwide.db"

# ==================== ARMAZENAMENTO DE MÍDIA ====================
UPLOAD_FOLDER = "arquivos_midia"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024
TIPOS_PERMITIDOS = {"png", "jpg", "jpeg", "gif", "webp", "mp4", "webm", "mov"}

# ==================== DADOS DE RECEBIMENTO — PROTEGIDOS ====================
AGENCIA_ITAÚ = os.environ.get("AGENCIA_ITAÚ", "")
CONTA_ITAÚ = os.environ.get("CONTA_ITAÚ", "")
TITULAR_CONTA = os.environ.get("TITULAR_CONTA", "")
CHAVE_PIX = os.environ.get("CHAVE_PIX", "")
LINK_ASSINATURA_PREMIUM = ""

# ==================== SISTEMA DE IDIOMAS ====================
IDIOMAS = {
    "pt": {
        "titulo": "JBS WORLDWIDE",
        "subtitulo": "Conectando pessoas, ideias e sonhos em todo o mundo",
        "criar_conta": "Criar Nova Conta",
        "entrar": "Entrar",
        "nome_completo": "Nome completo",
        "email": "Seu e-mail",
        "senha": "Crie uma senha",
        "acessar": "Acessar Conta",
        "ja_possui": "Já tenho conta",
        "nao_possui": "Não tenho conta ainda",
        "o_que_pensa": "O que você está pensando?",
        "publicar": "Publicar",
        "curtir": "Curtidas",
        "comentar": "Comentar",
        "sair": "Sair",
        "plano_gratis": "Plano Grátis",
        "plano_premium": "Plano Premium",
        "assinar_premium": "Assinar Premium",
        "erro_preencher": "Preencha todos os campos corretamente",
        "erro_email_existe": "Este e-mail já está cadastrado",
        "erro_dados": "E-mail ou senha incorretos",
        "sucesso_cadastro": "Conta criada! Faça login para continuar"
    },
    "en": {
        "titulo": "JBS WORLDWIDE",
        "subtitulo": "Connecting people, ideas and dreams across the globe",
        "criar_conta": "Create New Account",
        "entrar": "Sign In",
        "nome_completo": "Full name",
        "email": "Your email",
        "senha": "Create a password",
        "acessar": "Sign In",
        "ja_possui": "Already have an account",
        "nao_possui": "Don't have an account yet",
        "o_que_pensa": "What's on your mind?",
        "publicar": "Post",
        "curtir": "Likes",
        "comentar": "Comment",
        "sair": "Sign Out",
        "plano_gratis": "Free Plan",
        "plano_premium": "Premium Plan",
        "assinar_premium": "Get Premium",
        "erro_preencher": "Please fill all fields correctly",
        "erro_email_existe": "This email is already registered",
        "erro_dados": "Incorrect email or password",
        "sucesso_cadastro": "Account created! Sign in to continue"
    }
}

def pegar_idioma():
    if "idioma" in session:
        return session["idioma"]
    idiomas_nav = request.accept_languages.best_match(["pt", "en"])
    return idiomas_nav if idiomas_nav else "pt"

@app.route("/mudar-idioma/<lang>")
def mudar_idioma(lang):
    if lang in IDIOMAS:
        session["idioma"] = lang
    return redirect(request.referrer or url_for("inicio"))

# ==================== BANCO DE DADOS ====================
def iniciar_banco():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                plano TEXT DEFAULT 'gratis',
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE publicacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                texto TEXT,
                arquivo TEXT,
                tipo_arquivo TEXT,
                destacada INTEGER DEFAULT 0,
                data_publicacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        ''')
        c.execute('''
            CREATE TABLE curtidas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                publicacao_id INTEGER NOT NULL,
                usuario_id INTEGER NOT NULL,
                FOREIGN KEY (publicacao_id) REFERENCES publicacoes(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                UNIQUE(publicacao_id, usuario_id)
            )
        ''')
        c.execute('''
            CREATE TABLE comentarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                publicacao_id INTEGER NOT NULL,
                usuario_id INTEGER NOT NULL,
                texto TEXT NOT NULL,
                data_comentario DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (publicacao_id) REFERENCES publicacoes(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        ''')
        conn.commit()
        conn.close()

iniciar_banco()

# ==================== FUNÇÕES AUXILIARES ====================
def conectar_banco():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def logado():
    return "usuario_id" in session

# ==================== PÁGINA INICIAL ====================
@app.route("/")
def inicio():
    lang = pegar_idioma()
    t = IDIOMAS[lang]
    
    if logado():
        return redirect(url_for("feed"))
    
    return render_template_string(f'''
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{t["titulo"]}</title>
        <style>
            *{{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI', Arial, sans-serif;}}
            body{{background:linear-gradient(135deg,#020617 0%,#0f172a 50%,#1e293b 100%);color:white;min-height:100vh;display:flex;align-items:center;justify-content:center;position:relative;}}
            .fundo{{position:absolute;top:0;left:0;width:100%;height:100%;background-image:url("https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=1920&q=80");background-size:cover;opacity:0.12;}}
            .caixa{{position:relative;z-index:2;max-width:1100px;width:90%;display:grid;grid-template-columns:1fr 1fr;gap:50px;align-items:center;}}
            .marca h1{{font-size:52px;color:#84cc16;margin-bottom:15px;}}
            .marca p{{font-size:20px;color:#cbd5e1;line-height:1.6;}}
            .area-botoes{{background:rgba(15,23,42,0.92);padding:40px 30px;border-radius:16px;border:1px solid rgba(132,204,22,0.25);}}
            .botao{{display:block;width:100%;padding:15px;margin:10px 0;border-radius:10px;text-decoration:none;text-align:center;font-weight:bold;font-size:17px;}}
            .botao.primario{{background:#84cc16;color:#020617;}}
            .botao.secundario{{background:transparent;color:#84cc16;border:2px solid #84cc16;}}
            .troca-idioma{{position:absolute;top:20px;right:20px;background:#1e293b;padding:8px 15px;border-radius:8px;font-size:14px;}}
            .troca-idioma a{{color:#84cc16;text-decoration:none;margin:0 5px;}}
            @media(max-width:820px){{.caixa{{grid-template-columns:1fr;gap:30px;text-align:center;}}}}
        </style>
    </head>
    <body>
        <div class="fundo"></div>
        <div class="troca-idioma">
            <a href="/mudar-idioma/pt">PT</a> | <a href="/mudar-idioma/en">EN</a>
        </div>
        <div class="caixa">
            <div class="marca">
                <h1>{t["titulo"]}</h1>
                <p>{t["subtitulo"]}</p>
            </div>
            <div class="area-botoes">
                <a href="/cadastrar" class="botao primario">{t["criar_conta"]}</a>
                <a href="/entrar" class="botao secundario">{t["entrar"]}</a>
            </div>
        </div>
    </body>
    </html>
    ''')

# ==================== CADASTRO ====================
@app.route("/cadastrar", methods=["GET","POST"])
def cadastrar():
    lang = pegar_idioma()
    t = IDIOMAS[lang]
    erro = ""
    
    if request.method == "POST":
        nome = request.form["nome"].strip()
        email = request.form["email"].strip().lower()
        senha = request.form["senha"].strip()
        
        if not nome or not email or not senha:
            erro = t["erro_preencher"]
        else:
            conn = conectar_banco()
            try:
                conn.execute("INSERT INTO usuarios (nome,email,senha) VALUES (?,?,?)", (nome,email,senha))
                conn.commit()
                return redirect(url_for("entrar", msg=t["sucesso_cadastro"]))
            except sqlite3.IntegrityError:
                erro = t["erro_email_existe"]
            finally:
                conn.close()
    
    return render_template_string(f'''
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{t["criar_conta"]} — JBS WORLDWIDE</title>
        <style>
            *{{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI', Arial, sans-serif;}}
            body{{background:#0f172a;color:white;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;}}
            .caixa{{width:100%;max-width:420px;background:#1e293b;padding:30px;border-radius:12px;}}
            h2{{text-align:center;margin-bottom:25px;color:#84cc16;}}
            .erro{{background:rgba(153,27,27,0.8);color:#fecaca;padding:10px;border-radius:8px;margin-bottom:15px;text-align:center;}}
            input{{width:100%;padding:14px;margin:8px 0 18px;background:#334155;border:1px solid #475569;border-radius:8px;color:white;font-size:16px;}}
            button{{width:100%;padding:14px;background:#84cc16;color:#0f172a;border:none;border-radius:8px;font-weight:bold;font-size:17px;}}
            a{{color:#94a3b8;text-decoration:none;display:block;text-align:center;margin-top:15px;}}
        </style>
    </head>
    <body>
        <div class="caixa">
            <h2>{t["criar_conta"]}</h2>
            {f'<div class="erro">{erro}</div>' if erro else ''}
            <form method="POST">
                <input type="text" name="nome" placeholder="{t["nome_completo"]}" required>
                <input type="email" name="email" placeholder="{t["email"]}" required>
                <input type="password" name="senha" placeholder="{t["senha"]}" required minlength="6">
                <button type="submit">{t["criar_conta"]}</button>
                <a href="/entrar">{t["ja_possui"]}</a>
                <a href="/">← Voltar</a>
            </form>
        </div>
    </body>
    </html>
    ''')

# ==================== LOGIN ====================
@app.route("/entrar", methods=["GET","POST"])
def entrar():
    lang = pegar_idioma()
    t = IDIOMAS[lang]
    msg = request.args.get("msg","")
    erro = ""
    
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        senha = request.form["senha"].strip()
        conn = conectar_banco()
        usuario = conn.execute("SELECT id FROM usuarios WHERE email=? AND senha=?", (email,senha)).fetchone()
        conn.close()
        if usuario:
            session["usuario_id"] = usuario["id"]
            return redirect(url_for("feed"))
        erro = t["erro_dados"]
    
    return render_template_string(f'''
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{t["entrar"]} — JBS WORLDWIDE</title>
        <style>
            *{{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI', Arial, sans-serif;}}
            body{{background:#0f172a;color:white;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;}}
            .caixa{{width:100%;max-width:420px;background:#1e293b;padding:30px;border-radius:12px;}}
            h2{{text-align:center;margin-bottom:25px;color:#84cc16;}}
            .sucesso{{background:rgba(20,83,45,0.8);color:#86efac;padding:10px;border-radius:8px;margin-bottom:15px;text-align:center;}}
            .erro{{background:rgba(153,27,27,0.8);color:#fecaca;padding:10px;border-radius:8px;margin-bottom:15px;text-align:center;}}
            input{{width:100%;padding:14px;margin:8px 0 18px;background:#334155;border:1px solid #475569;border-radius:8px;color:white;font-size:16px;}}
            button{{width:100%;padding:14px;background:#84cc16;color:#0f172a;border:none;border-radius:8px;font-weight:bold;font-size:17px;}}
            a{{color:#94a3b8;text-decoration:none;display:block;text-align:center;margin-top:15px;}}
        </style>
    </head>
    <body>
        <div class="caixa">
            <h2>{t["entrar"]}</h2>
            {f'<div class="sucesso">{msg}</div>' if msg else ''}
            {f'<div class="erro">{erro}</div>' if erro else ''}
            <form method="POST">
                <input type="email" name="email" placeholder="{t["email"]}" required>
                <input type="password" name="senha" placeholder="Senha" required>
                <button type="submit">{t["acessar"]}</button>
                <a href="/cadastrar">{t["nao_possui"]}</a>
                <a href="/">← Voltar</a>
            </form>
        </div>
    </body>
    </html>
    ''')

# ===# ==================== FEED COM SISTEMA DE CURTIDAS ====================
@app.route("/feed", methods=["GET","POST"])
def feed():
    if not logado():
        return redirect(url_for("entrar"))
    lang = pegar_idioma()
    t = IDIOMAS[lang]
    id_usuario = session["usuario_id"]
    
    # Ação de curtir/descurtir
    if "curtir" in request.args:
        id_pub = request.args.get("curtir", type=int)
        conn = conectar_banco()
        ja_curtiu = conn.execute("SELECT id FROM curtidas WHERE publicacao_id=? AND usuario_id=?", (id_pub, id_usuario)).fetchone()
        if ja_curtiu:
            conn.execute("DELETE FROM curtidas WHERE publicacao_id=? AND usuario_id=?", (id_pub, id_usuario))
        else:
            conn.execute("INSERT INTO curtidas (publicacao_id, usuario_id) VALUES (?,?)", (id_pub, id_usuario))
        conn.commit()
        conn.close()
        return redirect(url_for("feed"))
    
    # Publicar nova postagem
    if request.method == "POST":
        texto = request.form.get("texto","").strip()
        arquivo = request.files.get("arquivo")
        nome_arq = None
        tipo_arq = None
        
        if arquivo and arquivo.filename:
            ext = arquivo.filename.rsplit(".",1)[1].lower()
            if ext in TIPOS_PERMITIDOS:
                nome_arq = secure_filename(f"{datetime.now().timestamp()}_{arquivo.filename}")
                caminho_completo = os.path.join(app.config["UPLOAD_FOLDER"], nome_arq)
                arquivo.save(caminho_completo)
                tipo_arq = ext
        
        conn = conectar_banco()
        conn.execute("INSERT INTO publicacoes (usuario_id,texto,arquivo,tipo_arquivo) VALUES (?,?,?,?)", (id_usuario,texto,nome_arq,tipo_arq))
        conn.commit()
        conn.close()
        return redirect(url_for("feed"))
    
    # Buscar todas as publicações
    conn = conectar_banco()
    publicacoes = conn.execute('''
        SELECT p.*, u.nome,
        (SELECT COUNT(*) FROM curtidas WHERE publicacao_id=p.id) AS total_curtidas,
        CASE WHEN EXISTS(SELECT 1 FROM curtidas WHERE publicacao_id=p.id AND usuario_id=?) THEN 1 ELSE 0 END AS curtiu
        FROM publicacoes p JOIN usuarios u ON p.usuario_id=u.id
        ORDER BY p.destacada DESC, p.data_publicacao DESC
    ''', (id_usuario,)).fetchall()
    conn.close()
    
    html_publicacoes = ""
    for pub in publicacoes:
        cor_botao = "#ef4444" if pub["curtiu"] else "#6b7280"
        icone = "❤️" if pub["curtiu"] else "🤍"
        html_publicacoes += f'''
        <div class="publicacao">
            <strong>{pub["nome"]}</strong>
            <p>{pub["texto"] if pub["texto"] else ""}</p>
        '''
        if pub["arquivo"]:
            if pub["tipo_arquivo"] in ["png","jpg","jpeg","gif","webp"]:
                html_publicacoes += f'<img src="/midia/{pub["arquivo"]}" alt="Imagem da publicação">'
            elif pub["tipo_arquivo"] in ["mp4","webm","mov"]:
                html_publicacoes += f'<video controls src="/midia/{pub["arquivo"]}"></video>'
        html_publicacoes += f'''
            <div style="margin-top:12px;display:flex;align-items:center;gap:8px;">
                <a href="/feed?curtir={pub["id"]}" style="font-size:18px;text-decoration:none;">{icone}</a>
                <span style="color:{cor_botao};font-weight:500;">{pub["total_curtidas"]} {t["curtir"]}</span>
            </div>
            <small style="color:#94a3b8;">{pub["data_publicacao"]}</small>
            <hr style="border-color:#334155;margin:15px 0;">
        </div>
        '''
    
    return render_template_string(f'''
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Feed — JBS WORLDWIDE</title>
        <style>
            *{{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI', Arial, sans-serif;}}
            body{{background:#0f172a;color:white;}}
            .topo{{padding:20px 30px;background:#1e293b;border-bottom:1px solid #334155;display:flex;justify-content:space-between;align-items:center;}}
            .topo h1{{color:#84cc16;font-size:24px;}}
            .sair{{color:#ef4444;text-decoration:none;font-weight:bold;}}
            .conteudo{{max-width:700px;margin:30px auto;padding:0 20px;}}
            .form-publicar{{background:#1e293b;padding:20px;border-radius:10px;margin-bottom:30px;}}
            textarea, input[type="file"]{{width:100%;padding:12px;margin-bottom:12px;background:#334155;border:1px solid #475569;border-radius:8px;color:white;}}
            button{{padding:12px 25px;background:#84cc16;color:#0f172a;border:none;border-radius:8px;font-weight:bold;}}
            .publicacao{{background:#1e293b;padding:20px;border-radius:10px;margin-bottom:20px;border:1px solid #334155;}}
            .publicacao img, .publicacao video{{max-width:100%;border-radius:8px;margin:10px 0;}}
        </style>
    </head>
    <body>
        <div class="topo">
            <h1>JBS WORLDWIDE</h1>
            <a href="/sair" class="sair">{t["sair"]}</a>
        </div>
        <div class="conteudo">
            <div class="form-publicar">
                <h3>{t["o_que_pensa"]}</h3>
                <form method="POST" enctype="multipart/form-data">
                    <textarea name="texto" rows="3" placeholder=""></textarea>
                    <input type="file" name="arquivo" accept="image/*,video/*">
                    <button type="submit">{t["publicar"]}</button>
                </form>
            </div>
            {html_publicacoes}
            <footer style="text-align:center; padding:15px; color:#94a3b8; font-size:13px; border-top:1px solid #334155; margin-top:20px;">
    © 2026 JBS WORLDWIDE — Criado por JBS TECNOLOGIA — Todos os direitos reservados
</footer>

            
        </iv>
    </body>
    </html>
    ''')


# ==================== DEMAIS FUNÇÕES ====================
@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("inicio"))

@app.route("/midia/<nome>")
def ver_midia(nome):
    return send_from_directory(app.config["UPLOAD_FOLDER"], nome)

# ==================== EXECUÇÃO PARA RENDER ====================
if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta, debug=False)
