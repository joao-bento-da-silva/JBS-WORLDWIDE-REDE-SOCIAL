 # ==================================================
# © 2026 JBS TECNOLOGIA — REDE SOCIAL COM IDENTIDADE OFICIAL
# MESMO ESTILO DO GERADOR DE AUTORIDADE + NUNCA MAIS PERDE DADOS
# ==================================================

from flask import Flask, request, session, redirect, url_for, render_template_string, send_from_directory
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ==================== SEGURANÇA ====================
app.secret_key = os.environ.get("CHAVE_REDE_SOCIAL", "SEGURANCA_REDE_JBS_2026")

# ==================== BANCO PERMANENTE ====================
PASTA_DADOS = "/app/dados" if os.path.exists("/app") else "."
os.makedirs(PASTA_DADOS, exist_ok=True)
PASTA_MIDIAS = os.path.join(PASTA_DADOS, "midias")
os.makedirs(PASTA_MIDIAS, exist_ok=True)
BANCO_DADOS = os.path.join(PASTA_DADOS, "rede_jbs.db")

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

# ==================== TELA INICIAL — MESMO ESTILO DO GERADOR ====================
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
            body{
                background: linear-gradient(135deg,#050510 0%,#0f172a 50%,#1e293b 100%);
                color:white;min-height:100vh;
                background-image: radial-gradient(circle at 20% 30%, rgba(132,204,22,0.08) 0%, transparent 55%),
                                  radial-gradient(circle at 80% 70%, rgba(59,130,246,0.06) 0%, transparent 55%);
                display:flex;flex-direction:column;align-items:center;justify-content:center;padding:30px;
            }
            .marca{font-size:46px;font-weight:bold;color:#84cc16;margin-bottom:12px;text-align:center;}
            .slogan{font-size:19px;color:#cbd5e1;margin-bottom:50px;text-align:center;}
            .botoes{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:22px;width:100%;max-width:500px;}
            .btn{
                display:block;padding:18px 25px;border-radius:12px;text-decoration:none;font-weight:bold;font-size:18px;text-align:center;
                transition:all 0.3s ease;border:none;
            }
            .btn.verde{background:#84cc16;color:#050510;box-shadow:0 0 20px rgba(132,204,22,0.3);}
            .btn.verde:hover{transform:translateY(-3px);box-shadow:0 0 30px rgba(132,204,22,0.5);}
            .btn.escuro{background:rgba(30,41,59,0.8);color:white;border:1px solid rgba(132,204,22,0.3);}
            .btn.escuro:hover{background:rgba(51,65,85,0.9);transform:translateY(-2px);}
        </style>
    </head>
    <body>
        <div class="marca">JBS REDE SOCIAL</div>
        <div class="slogan">Conectando pessoas, ideias e projetos — da mesma família do Gerador de Autoridade</div>
        <div class="botoes">
            <a href="/cadastrar" class="btn verde">Criar Conta</a>
            <a href="/entrar" class="btn escuro">Entrar</a>
        </div>
    </body>
    </html>
    ''')

# ==================== CADASTRO ====================
@app.route("/cadastrar", methods=["GET","POST"])
def cadastrar():
    if request.method == "POST":
        n = request.form["nome"]
        e = request.form["email"]
        s = request.form["senha"]
        conn = conectar_banco()
        try:
            conn.execute("INSERT INTO usuarios (nome,email,senha) VALUES (?,?,?)", (n,e,s))
            conn.commit()
            return redirect(url_for("entrar"))
        except:
            return render_template_string('''
            <html style="background:#0f172a;color:white;padding:30px;max-width:500px;margin:0 auto;">
                <h2 style="color:#84cc16;">Criar Nova Conta</h2><br>
                <p style="color:#f87171;">E-mail já cadastrado!</p>
                <br><a href="/cadastrar" style="color:#84cc16;">Tentar outro</a> | <a href="/" style="color:#84cc16;">Voltar</a>
            </html>
            ''')
        finally: conn.close()

    return render_template_string('''
    <html style="background:#0f172a;color:white;padding:30px;max-width:500px;margin:0 auto;">
        <h2 style="color:#84cc16;">Criar Nova Conta</h2><br>
        <form method="POST">
            <input type="text" name="nome" required placeholder="Seu nome completo" style="padding:12px;width:100%;margin:8px 0;border-radius:8px;border:none;"><br>
            <input type="email" name="email" required placeholder="Seu melhor e-mail" style="padding:12px;width:100%;margin:8px 0;border-radius:8px;border:none;"><br>
            <input type="password" name="senha" required placeholder="Crie uma senha forte" style="padding:12px;width:100%;margin:8px 0;border-radius:8px;border:none;"><br>
            <button style="padding:12px 30px;background:#84cc16;color:black;border:none;border-radius:8px;font-weight:bold;margin-top:10px;">Cadastrar</button>
        </form>
        <br><a href="/" style="color:#84cc16;">Voltar ao início</a>
    </html>
    ''')

# ==================== LOGIN ====================
@app.route("/entrar", methods=["GET","POST"])
def entrar():
    if request.method == "POST":
        e = request.form["email"]
        s = request.form["senha"]
        conn = conectar_banco()
        user = conn.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (e,s)).fetchone()
        conn.close()
        if user:
            session["usuario_id"] = user["id"]
            session["nome"] = user["nome"]
            return redirect(url_for("feed"))
        return render_template_string('''
        <html style="background:#0f172a;color:white;padding:30px;max-width:500px;margin:0 auto;">
            <h2 style="color:#84cc16;">Entrar na Sua Conta</h2><br>
            <p style="color:#f87171;">E-mail ou senha incorretos!</p>
            <br><a href="/entrar" style="color:#84cc16;">Tentar novamente</a> | <a href="/" style="color:#84cc16;">Voltar</a>
        </html>
        ''')

    return render_template_string('''
    <html style="background:#0f172a;color:white;padding:30px;max-width:500px;margin:0 auto;">
        <h2 style="color:#84cc16;">Entrar</h2><br>
        <form method="POST">
            <input type="email" name="email" required placeholder="Seu e-mail" style="padding:12px;width:100%;margin:8px 0;border-radius:8px;border:none;"><br>
            <input type="password" name="senha" required placeholder="Sua senha" style="padding:12px;width:100%;margin:8px 0;border-radius:8px;border:none;"><br>
            <button style="padding:12px 30px;background:#84cc16;color:black;border:none;border-radius:8px;font-weight:bold;margin-top:10px;">Acessar</button>
        </form>
        <br><a href="/cadastrar" style="color:#84cc16;">Criar conta</a> | <a href="/" style="color:#84cc16;">Voltar</a>
    </html>
    ''')

# ==================== FEED — COM IDENTIDADE JBS ====================
@app.route("/feed", methods=["GET","POST"])
def feed():
    if not usuario_logado():
        return redirect(url_for("entrar"))

    if request.method == "POST":
        texto = request.form.get("texto","")
        nome_imagem = None
        if "imagem" in request.files:
            arq = request.files["imagem"]
            if arq.filename != "":
                nome_imagem = secure_filename(f"{datetime.now().timestamp()}_{arq.filename}")
                caminho = os.path.join(PASTA_MIDIAS, nome_imagem)
                arq.save(caminho)

        conn = conectar_banco()
        conn.execute("INSERT INTO postagens VALUES (NULL,?,?,?,0,?)", (session["usuario_id"], texto, nome_imagem, datetime.now()))
        conn.commit()
        conn.close()
        return redirect(url_for("feed"))

    conn = conectar_banco()
    postagens = conn.execute('''SELECT p.*, u.nome FROM postagens p 
                                JOIN usuarios u ON p.usuario_id = u.id 
                                ORDER BY p.data_hora DESC''').fetchall()
    conn.close()

    html = '''
    <html style="background:#0f172a;color:white;padding:20px;max-width:850px;margin:0 auto;">
        <div style="background:#1e293b;padding:25px;border-radius:12px;margin-bottom:30px;border-left:4px solid #84cc16;">
            <h1 style="font-size:34px;color:#84cc16;margin-bottom:15px;">Olá {nome}!</h1>
            <p style="color:#94a3b8;margin-bottom:20px;">Compartilhe suas ideias, projetos e conquistas</p>
            <form method="POST" enctype="multipart/form-data">
                <textarea name="texto" placeholder="O que você está pensando?" rows="5" style="width:100%;padding:15px;border-radius:8px;border:none;font-size:17px;color:#111;"></textarea><br><br>
                <input type="file" name="imagem" accept="image/*" style="margin-bottom:15px;color:#cbd5e1;"><br>
                <button type="submit" style="padding:12px 35px;background:#84cc16;color:black;border:none;border-radius:8px;font-weight:bold;font-size:17px;">Publicar</button>
            </form>
        </div>
    '''.format(nome=session["nome"])

    for p in postagens:
        parte_imagem = f"<br><img src='/ver_imagem/{p['imagem']}' style='max-width:100%;border-radius:8px;margin:12px 0;'>" if p["imagem"] else ""
        html += f'''
        <div style="background:#1e293b;padding:20px;border-radius:12px;margin-bottom:20px;border-left:3px solid #84cc16;">
            <h3 style="font-size:20px;color:#e2e8f0;margin-bottom:8px;">{p['nome']}</h3>
            <p style="font-size:17px;line-height:1.6;color:#cbd5e1;">{p['texto'] or ""}</p>
            {parte_imagem}
            <div style="margin-top:15px;font-size:16px;">
                <a href="/curtir/{p['id']}" style="color:#ef4444;text-decoration:none;">❤️ {p['curtidas']} Curtir</a>
                <span style="color:#94a3b8;margin-left:15px;">{p['data_hora']}</span>
            </div>
        </div>
        '''

    html += "<br><a href='/sair' style='color:#ef4444;font-size:17px;text-decoration:none;'>Sair da conta</a></html>"
    return html

# ==================== DEMAIS FUNÇÕES ====================
@app.route("/ver_imagem/<nome>")
def ver_imagem(nome):
    return send_from_directory(PASTA_MIDIAS, nome)

@app.route("/curtir/<id_post>")
def curtir(id_post):
    if not usuario_logado():
        return redirect(url_for("entrar"))
    conn = conectar_banco()
    conn.execute("UPDATE postagens SET curtidas = curtidas + 1 WHERE id=?", (id_post,))
    conn.commit()
    conn.close()
    return redirect(url_for("feed"))

@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("inicio"))

# ==================== EXECUÇÃO ====================
if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta)
