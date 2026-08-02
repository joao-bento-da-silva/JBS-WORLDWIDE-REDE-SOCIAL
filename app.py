  # ==================================================
# © 2026 JBS TECNOLOGIA — REDE SOCIAL OFICIAL
# VISUAL PADRÃO JBS | DADOS PERMANENTES | PRONTA PARA USO
# ==================================================

from flask import Flask, request, session, redirect, url_for, render_template_string, send_from_directory
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ==================== SEGURANÇA ====================
app.secret_key = os.environ.get("CHAVE_REDE_SOCIAL", "SEGURANCA_REDE_JBS_2026")
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 315360000

# ==================== BANCO E ARQUIVOS PERMANENTES ====================
PASTA_DADOS = "/app/dados" if os.path.exists("/app") else "."
os.makedirs(PASTA_DADOS, exist_ok=True)
PASTA_MIDIAS = os.path.join(PASTA_DADOS, "arquivos_midia")
os.makedirs(PASTA_MIDIAS, exist_ok=True)
BANCO_DADOS = os.path.join(PASTA_DADOS, "rede_social_jbs.db")

def conectar_banco():
    conn = sqlite3.connect(BANCO_DADOS)
    conn.row_factory = sqlite3.Row
    return conn

def usuario_logado():
    return "usuario_id" in session

# ==================== TABELAS ====================
conn = conectar_banco()
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
)''')

c.execute('''CREATE TABLE IF NOT EXISTS postagens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    texto TEXT,
    imagem TEXT,
    curtidas INTEGER DEFAULT 0,
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
)''')

conn.commit()
conn.close()

# ==================== TELA INICIAL ====================
@app.route("/")
def inicio():
    if usuario_logado():
        return redirect(url_for("feed"))
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>JBS REDE SOCIAL</title>
        <style>
            *{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI',Arial,sans-serif;}
            body{min-height:100vh;background:linear-gradient(160deg,#020617 0%,#0f172a 40%,#1e293b 100%);color:#e2e8f0;position:relative;}
            body::before{content:"";position:absolute;top:0;left:0;width:100%;height:100%;background-image:radial-gradient(circle at 15% 25%,rgba(132,204,22,0.12) 0%,transparent 50%),radial-gradient(circle at 85% 75%,rgba(59,130,246,0.08) 0%,transparent 50%);pointer-events:none;}
            .caixa{position:relative;z-index:1;max-width:800px;margin:0 auto;padding:80px 25px;text-align:center;}
            .logo{font-size:52px;font-weight:900;color:#84cc16;margin-bottom:12px;text-shadow:0 0 25px rgba(132,204,22,0.35);}
            .subtitulo{font-size:18px;color:#cbd5e1;margin-bottom:35px;}
            .botoes{display:flex;gap:22px;justify-content:center;flex-wrap:wrap;}
            .btn{padding:16px 38px;border-radius:10px;text-decoration:none;font-weight:bold;font-size:17px;transition:all 0.3s ease;border:none;}
            .btn.primario{background:#84cc16;color:#020617;box-shadow:0 0 20px rgba(132,204,22,0.35);}
            .btn.primario:hover{transform:translateY(-3px);box-shadow:0 0 35px rgba(132,204,22,0.5);}
            .btn.secundario{background:rgba(30,41,59,0.6);color:#84cc16;border:1px solid rgba(132,204,22,0.4);}
            .btn.secundario:hover{background:rgba(132,204,22,0.1);transform:translateY(-2px);}
            .rodape{position:absolute;bottom:25px;width:100%;text-align:center;font-size:13px;color:#64748b;}
        </style>
    </head>
    <body>
        <div class="caixa">
            <div class="logo">JBS REDE SOCIAL</div>
            <div class="subtitulo">Compartilhe ideias, imagens e conecte-se</div>
            <div class="botoes">
                <a href="/cadastrar" class="btn primario">Criar Conta</a>
                <a href="/entrar" class="btn secundario">Acessar Conta</a>
            </div>
        </div>
        <div class="rodape">© 2026 JBS TECNOLOGIA — Todos os Direitos Reservados</div>
    </body>
    </html>
    ''')

# ==================== CADASTRO ====================
@app.route("/cadastrar", methods=["GET","POST"])
def cadastrar():
    if usuario_logado(): return redirect(url_for("feed"))
    if request.method == "POST":
        n,e,s = request.form["nome"],request.form["email"],request.form["senha"]
        try:
            conn = conectar_banco()
            conn.execute("INSERT INTO usuarios (nome,email,senha) VALUES (?,?,?)",(n,e,s))
            conn.commit()
            user = conn.execute("SELECT * FROM usuarios WHERE email=?",(e,)).fetchone()
            conn.close()
            session.update({"usuario_id":user["id"],"nome":user["nome"]})
            session.permanent = True
            return redirect(url_for("feed"))
        except:
            return '''<html style="background:#0f172a;color:white;padding:30px;text-align:center;">
            <h3 style="color:#ef4444;">Este e-mail já está cadastrado.</h3>
            <br><a href="/cadastrar" style="color:#84cc16;">Voltar</a></html>'''
    return '''<html style="background:#0f172a;color:white;padding:30px;max-width:500px;margin:0 auto;">
    <h2 style="color:#84cc16;text-align:center;margin-bottom:25px;">Cadastro</h2>
    <form method="POST">
        <input type="text" name="nome" required placeholder="Nome completo" style="width:100%;padding:12px;margin:8px 0;border-radius:8px;border:none;">
        <input type="email" name="email" required placeholder="E-mail" style="width:100%;padding:12px;margin:8px 0;border-radius:8px;border:none;">
        <input type="password" name="senha" required placeholder="Senha" style="width:100%;padding:12px;margin:8px 0;border-radius:8px;border:none;">
        <button style="background:#84cc16;color:black;padding:12px;width:100%;border-radius:8px;margin-top:10px;font-weight:bold;">CONFIRMAR</button>
    </form>
    <br><div style="text-align:center;"><a href="/entrar" style="color:#84cc16;">Já possuo cadastro</a></div>
    </html>'''

# ==================== LOGIN ====================
@app.route("/entrar", methods=["GET","POST"])
def entrar():
    if usuario_logado(): return redirect(url_for("feed"))
    if request.method == "POST":
        conn = conectar_banco()
        user = conn.execute("SELECT * FROM usuarios WHERE email=? AND senha=?",(request.form["email"],request.form["senha"])).fetchone()
        conn.close()
        if user:
            session.update({"usuario_id":user["id"],"nome":user["nome"]})
            session.permanent = True
            return redirect(url_for("feed"))
        return '''<html style="background:#0f172a;color:white;padding:30px;text-align:center;">
        <h3 style="color:#ef4444;">Dados incorretos.</h3>
        <br><a href="/entrar" style="color:#84cc16;">Tentar novamente</a></html>'''
    return '''<html style="background:#0f172a;color:white;padding:30px;max-width:500px;margin:0 auto;">
    <h2 style="color:#84cc16;text-align:center;margin-bottom:25px;">Acesso</h2>
    <form method="POST">
        <input type="email" name="email" required placeholder="E-mail cadastrado" style="width:100%;padding:12px;margin:8px 0;border-radius:8px;border:none;">
        <input type="password" name="senha" required placeholder="Senha" style="width:100%;padding:12px;margin:8px 0;border-radius:8px;border:none;">
        <button style="background:#84cc16;color:black;padding:12px;width:100%;border-radius:8px;margin-top:10px;font-weight:bold;">ACESSAR</button>
    </form>
    <br><div style="text-align:center;"><a href="/cadastrar" style="color:#84cc16;">Novo cadastro</a></div>
    </html>'''

# ==================== FEED PRINCIPAL ====================
@app.route("/feed", methods=["GET","POST"])
def feed():
    if not usuario_logado(): return redirect(url_for("entrar"))

    if request.method == "POST":
        texto = request.form.get("texto","")
        nome_imagem = None
        if "imagem" in request.files:
            arq = request.files["imagem"]
            if arq.filename:
                nome_imagem = secure_filename(f"{datetime.now().timestamp()}_{arq.filename}")
                arq.save(os.path.join(PASTA_MIDIAS, nome_imagem))
        
        conn = conectar_banco()
        conn.execute("INSERT INTO postagens VALUES (NULL,?,?,?,0,?)",(session["usuario_id"],texto,nome_imagem,datetime.now()))
        conn.commit()
        conn.close()
        return redirect(url_for("feed"))

    conn = conectar_banco()
    postagens = conn.execute("SELECT p.*,u.nome FROM postagens p JOIN usuarios u ON p.usuario_id=u.id ORDER BY p.data_hora DESC").fetchall()
    conn.close()

    html = f'''
    <html style="background:#0f172a;color:white;padding:20px;max-width:850px;margin:0 auto;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:25px;">
            <h2 style="color:#84cc16;">Olá, {session['nome']}</h2>
            <a href="/sair" style="color:#ef4444;text-decoration:none;">Encerrar Sessão</a>
        </div>

        <div style="background:rgba(30,41,59,0.6);border:1px solid rgba(132,204,22,0.3);padding:25px;border-radius:12px;margin-bottom:35px;">
            <h3 style="color:#84cc16;margin-bottom:15px;">Nova Publicação</h3>
            <form method="POST" enctype="multipart/form-data">
                <textarea name="texto" placeholder="Compartilhe algo..." rows="4" style="width:100%;padding:12px;border-radius:8px;border:none;font-size:16px;margin-bottom:12px;"></textarea>
                <input type="file" name="imagem" accept="image/*" style="margin-bottom:15px;color:#94a3b8;">
                <button style="background:#84cc16;color:black;padding:12px 35px;border-radius:8px;border:none;font-weight:bold;font-size:17px;">PUBLICAR</button>
            </form>
        </div>
    '''

    for p in postagens:
        img_html = f"<br><img src='/imagem/{p['imagem']}' style='max-width:100%;border-radius:8px;margin:12px 0;'>" if p["imagem"] else ""
        html += f'''
        <div style="background:rgba(30,41,59,0.6);border:1px solid rgba(132,204,22,0.2);padding:22px;border-radius:12px;margin-bottom:20px;">
            <h3 style="color:#84cc16;margin-bottom:8px;">{p['nome']}</h3>
            <p style="font-size:16px;line-height:1.6;margin-bottom:10px;">{p['texto'] or ""}</p>
            {img_html}
            <div style="margin-top:15px;color:#94a3b8;">
                <a href="/curtir/{p['id']}" style="color:#ef4444;text-decoration:none;margin-right:20px;">Curtir ({p['curtidas']})</a>
                <span>{p['data_hora']}</span>
            </div>
        </div>
        '''

    html += "</html>"
    return html

# ==================== EXIBIR IMAGEM ====================
@app.route("/imagem/<nome>")
def imagem(nome):
    return send_from_directory(PASTA_MIDIAS, nome)

# ==================== CURTIR ====================
@app.route("/curtir/<id_post>")
def curtir(id_post):
    if not usuario_logado(): return redirect(url_for("entrar"))
    conn = conectar_banco()
    conn.execute("UPDATE postagens SET curtidas = curtidas + 1 WHERE id=?",(id_post,))
    conn.commit()
    conn.close()
    return redirect(url_for("feed"))

# ==================== SAIR ====================
@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("inicio"))

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta)
