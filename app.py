 # ==================================================
# © 2026 JBS TECNOLOGIA — REDE SOCIAL VISUAL 100% CORRETO
# TELA INICIAL EXATA — NÃO FICA MAIS DESCONFIGURADO
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

# ==================== TELA INICIAL — EXATA, SEM FALHAS ====================
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
        <title>JBS WORLDWIDE</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, sans-serif; }
            body {
                background-color: #050510;
                color: white;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .idioma {
                position: absolute;
                top: 20px;
                right: 25px;
                font-size: 18px;
            }
            .idioma a {
                color: #84cc16;
                text-decoration: none;
                margin: 0 5px;
            }
            .marca-1 {
                font-size: 80px;
                font-weight: bold;
                color: #84cc16;
                text-align: center;
                line-height: 1;
            }
            .marca-2 {
                font-size: 80px;
                font-weight: bold;
                color: #84cc16;
                text-align: center;
                margin-bottom: 25px;
                line-height: 1;
            }
            .frase {
                font-size: 24px;
                color: #cbd5e1;
                text-align: center;
                margin-bottom: 50px;
                max-width: 90%;
                line-height: 1.5;
            }
            .grupo-botoes {
                width: 100%;
                max-width: 500px;
                display: flex;
                flex-direction: column;
                gap: 20px;
            }
            .botao {
                display: block;
                padding: 20px;
                border-radius: 10px;
                text-decoration: none;
                font-weight: bold;
                font-size: 24px;
                text-align: center;
                border: none;
            }
            .botao.verde {
                background-color: #84cc16;
                color: #000000;
            }
            .botao.borda {
                background-color: transparent;
                color: #84cc16;
                border: 3px solid #84cc16;
            }
        </style>
    </head>
    <body>
        <div class="idioma">
            <a href="#">PT</a> | <a href="#">EN</a>
        </div>
        <div class="marca-1">JBS</div>
        <div class="marca-2">WORLDWIDE</div>
        <div class="frase">Conectando pessoas, ideias e sonhos em todo o mundo</div>
        <div class="grupo-botoes">
            <a href="/cadastrar" class="botao verde">Criar Nova Conta</a>
            <a href="/entrar" class="botao borda">Entrar</a>
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
        except sqlite3.IntegrityError:
            return "E-mail já cadastrado <br><a href='/cadastrar' style='color:#84cc16;'>Voltar</a>"
        except Exception as erro:
            return f"Erro: {str(erro)} <br><a href='/cadastrar' style='color:#84cc16;'>Voltar</a>"
        finally: conn.close()
    return render_template_string('''
    <html style="background:#0f172a;color:white;padding:30px;max-width:500px;margin:0 auto;">
        <h2>Criar Conta</h2><br>
        <form method="POST">
            <input type="text" name="nome" required placeholder="Seu nome" style="padding:10px;width:100%;margin:5px 0;"><br>
            <input type="email" name="email" required placeholder="Seu e-mail" style="padding:10px;width:100%;margin:5px 0;"><br>
            <input type="password" name="senha" required placeholder="Sua senha" style="padding:10px;width:100%;margin:5px 0;"><br>
            <button style="padding:10px 25px;background:#84cc16;color:black;border:none;border-radius:5px;">Cadastrar</button>
        </form>
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
        return "Dados incorretos <br><a href='/entrar' style='color:#84cc16;'>Voltar</a>"
    return render_template_string('''
    <html style="background:#0f172a;color:white;padding:30px;max-width:500px;margin:0 auto;">
        <h2>Entrar</h2><br>
        <form method="POST">
            <input type="email" name="email" required placeholder="E-mail" style="padding:10px;width:100%;margin:5px 0;"><br>
            <input type="password" name="senha" required placeholder="Senha" style="padding:10px;width:100%;margin:5px 0;"><br>
            <button style="padding:10px 25px;background:#84cc16;color:black;border:none;border-radius:5px;">Entrar</button>
        </form>
    </html>
    ''')

# ==================== FEED ====================
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
    <html style="background:#0f172a;color:white;padding:20px;max-width:900px;margin:0 auto;">
        <div style="background:#1e293b;padding:25px;border-radius:12px;">
            <h1 style="font-size:36px;font-weight:normal;margin-bottom:20px;">Olá {nome} !</h1><br>
            <form method="POST" enctype="multipart/form-data">
                <textarea name="texto" placeholder="O que você está pensando?" rows="6" style="width:100%;padding:15px;border-radius:8px;border:none;font-size:20px;color:#333;"></textarea><br><br>
                <input type="file" name="imagem" accept="image/*"><br><br>
                <button type="submit" style="padding:15px 45px;background:#84cc16;color:black;border:none;border-radius:8px;font-weight:bold;font-size:22px;">Publicar</button>
            </form>
        </div>
        <br><br>
        <a href="/sair" style="color:#ef4444;font-size:20px;text-decoration:underline;">Sair da conta</a>
    '''.format(nome=session["nome"])

    for p in postagens:
        parte_imagem = f"<br><img src='/ver_imagem/{p['imagem']}' style='max-width:100%;border-radius:8px;margin:15px 0;'>" if p["imagem"] else ""
        html += f'''
        <div style="background:#1e293b;padding:20px;border-radius:12px;margin-top:25px;">
            <h3 style="font-size:22px;margin-bottom:10px;">{p['nome']}</h3>
            <p style="font-size:18px;line-height:1.6;">{p['texto'] or ""}</p>
            {parte_imagem}
            <div style="margin-top:15px;font-size:18px;">
                <a href="/curtir/{p['id']}" style="color:#ef4444;text-decoration:none;">❤️ {p['curtidas']} Curtir</a>
                <span style="color:#94a3b8;margin-left:20px;">{p['data_hora']}</span>
            </div>
        </div>
        '''

    html += "</html>"
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
