 # ==================================================
# © 2026 JBS TECNOLOGIA
# VERSAO DEFINITIVA - 100% TESTADA E CORRIGIDA
# ==================================================

from flask import Flask, request, session, redirect, url_for, render_template_string, send_from_directory
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ==================== CONFIGURACOES ====================
app.secret_key = os.environ.get("CHAVE_INTERNA_SEGURANCA")
app.config["SESSION_PERMANENT"] = True
app.config["UPLOAD_FOLDER"] = "/app/midia_enviada"
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

EXTENSOES_PERMITIDAS = {"png", "jpg", "jpeg", "gif", "mp4", "mov", "avi", "webm"}

CHAVE_MESTRA_DNA = os.environ.get("CHAVE_MESTRA_DNA")
BANCO_DADOS = "jbs_rede.db"

try:
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
except:
    pass

# ==================== FUNCOES ====================
def conectar_banco():
    conn = sqlite3.connect(BANCO_DADOS)
    conn.row_factory = sqlite3.Row
    return conn

def usuario_logado():
    return "usuario_id" in session

def arquivo_valido(nome):
    return "." in nome and nome.rsplit(".", 1)[1].lower() in EXTENSOES_PERMITIDAS

# ==================== INICIAR BANCO ====================
def iniciar_banco():
    conn = conectar_banco()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS publicacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            texto TEXT,
            arquivo TEXT,
            tipo_arquivo TEXT,
            data_publicacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    ''')
    conn.commit()
    conn.close()

iniciar_banco()

# ==================== PAGINA INICIAL ====================
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
        <title>JBS Rede Social</title>
        <style>
            *{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif;}
            body{background:linear-gradient(180deg,#0a0f1a 0%,#121a2b 100%);color:#e2e8f0;min-height:100vh;}
            .cabecalho{padding:25px 20px;border-bottom:1px solid #1e293b;}
            .cabecalho h1{color:#84cc16;font-size:32px;text-align:center;}
            .conteudo{max-width:650px;margin:50px auto;padding:0 20px;}
            .boasvindas{text-align:center;margin-bottom:50px;}
            .boasvindas h2{font-size:28px;margin-bottom:15px;}
            .grupo-botoes{display:flex;gap:20px;justify-content:center;flex-wrap:wrap;}
            .botao{padding:15px 35px;border-radius:12px;text-decoration:none;font-weight:bold;font-size:17px;}
            .botao.verde{background:#84cc16;color:#050505;}
            .botao.verde:hover{background:#65a30d;}
            .botao.escuro{background:#1e293b;color:#fff;border:1px solid #334155;}
            .rodape{text-align:center;padding:30px;color:#64748b;font-size:14px;}
        </style>
    </head>
    <body>
        <div class="cabecalho"><h1>JBS TECNOLOGIA</h1></div>
        <div class="conteudo">
            <div class="boasvindas">
                <h2>Bem-vindo(a)</h2>
                <p>Compartilhe fotos, videos e ideias com seguranca.</p>
            </div>
            <div class="grupo-botoes">
                <a href="/cadastrar" class="botao verde">Criar Conta</a>
                <a href="/entrar" class="botao escuro">Entrar</a>
            </div>
        </div>
        <div class="rodape">© 2026 JBS TECNOLOGIA</div>
    </body>
    </html>
    ''')

# ==================== CADASTRO ====================
@app.route("/cadastrar", methods=["GET","POST"])
def cadastrar():
    if request.method == "POST":
        nome = request.form.get("nome","").strip()
        email = request.form.get("email","").strip().lower()
        senha = request.form.get("senha","").strip()
        if not nome or not email or not senha:
            return "Preencha todos os campos <br><a href='/cadastrar' style='color:#84cc16;'>Voltar</a>"
        conn = conectar_banco()
        try:
            conn.execute("INSERT INTO usuarios (nome,email,senha) VALUES (?,?,?)", (nome,email,senha))
            conn.commit()
            return redirect(url_for("entrar"))
        except:
            return "E-mail ja cadastrado <br><a href='/cadastrar' style='color:#84cc16;'>Voltar</a>"
        finally: conn.close()
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cadastrar</title>
        <style>
            *{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif;}
            body{background:#0a0f1a;color:white;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;}
            .caixa{width:100%;max-width:480px;background:#121a2b;padding:40px;border-radius:16px;border:1px solid #1e293b;}
            h2{text-align:center;margin-bottom:30px;color:#84cc16;}
            input{width:100%;padding:16px;margin-bottom:20px;background:#0a0f1a;border:1px solid #334155;border-radius:10px;color:white;font-size:16px;}
            input:focus{outline:none;border-color:#84cc16;}
            button{width:100%;padding:16px;background:#84cc16;color:#050505;border:none;border-radius:10px;font-weight:bold;font-size:17px;}
            button:hover{background:#65a30d;}
            a{color:#94a3b8;text-decoration:none;display:block;text-align:center;margin-top:20px;}
        </style>
    </head>
    <body>
        <div class="caixa">
            <h2>Criar Conta</h2>
            <form method="POST">
                <input type="text" name="nome" placeholder="Seu nome" required>
                <input type="email" name="email" placeholder="Seu e-mail" required>
                <input type="password" name="senha" placeholder="Sua senha" required>
                <button type="submit">Cadastrar</button>
                <a href="/">Voltar</a>
            </form>
        </div>
    </body>
    </html>
    ''')

# ==================== LOGIN ====================
@app.route("/entrar", methods=["GET","POST"])
def entrar():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        senha = request.form.get("senha","").strip()
        conn = conectar_banco()
        usuario = conn.execute("SELECT id FROM usuarios WHERE email = ? AND senha = ?", (email,senha)).fetchone()
        conn.close()
        if usuario:
            session["usuario_id"] = usuario["id"]
            return redirect(url_for("feed"))
        return "E-mail ou senha errados <br><a href='/entrar' style='color:#84cc16;'>Voltar</a>"
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Entrar</title>
        <style>
            *{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif;}
            body{background:#0a0f1a;color:white;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;}
            .caixa{width:100%;max-width:480px;background:#121a2b;padding:40px;border-radius:16px;border:1px solid #1e293b;}
            h2{text-align:center;margin-bottom:30px;color:#84cc16;}
            input{width:100%;padding:16px;margin-bottom:20px;background:#0a0f1a;border:1px solid #334155;border-radius:10px;color:white;font-size:16px;}
            input:focus{outline:none;border-color:#84cc16;}
            button{width:100%;padding:16px;background:#84cc16;color:#050505;border:none;border-radius:10px;font-weight:bold;font-size:17px;}
            button:hover{background:#65a30d;}
            a{color:#94a3b8;text-decoration:none;display:block;text-align:center;margin-top:20px;}
        </style>
    </head>
    <body>
        <div class="caixa">
            <h2>Acessar Conta</h2>
            <form method="POST">
                <input type="email" name="email" placeholder="Seu e-mail" required>
                <input type="password" name="senha" placeholder="Sua senha" required>
                <button type="submit">Entrar</button>
                <a href="/cadastrar">Criar conta</a>
                <a href="/">Voltar</a>
            </form>
        </div>
    </body>
    </html>
    ''')

# ==================== FEED ====================
@app.route("/feed")
def feed():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    conn = conectar_banco()
    publicacoes = conn.execute('''
        SELECT p.*, u.nome FROM publicacoes p
        JOIN usuarios u ON p.usuario_id = u.id
        ORDER BY p.data_publicacao DESC
    ''').fetchall()
    conn.close()
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Feed</title>
        <style>
            *{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif;}
            body{background:linear-gradient(180deg,#0a0f1a 0%,#121a2b 100%);color:#e2e8f0;}
            .topo{padding:20px;background:rgba(0,0,0,0.3);border-bottom:1px solid #1e293b;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;}
            .topo h1{color:#84cc16;font-size:26px;}
            .topo a{color:#ef4444;text-decoration:none;font-weight:bold;padding:8px 15px;}
            .conteudo{max-width:650px;margin:30px auto;padding:0 15px;}
            .btn-novo{text-align:center;margin-bottom:35px;}
            .btn-novo a{padding:14px 35px;background:#84cc16;color:#050505;border-radius:12px;text-decoration:none;font-weight:bold;font-size:16px;display:inline-block;}
            .btn-novo a:hover{background:#65a30d;}
            .publicacao{background:#121a2b;padding:22px;border-radius:16px;border:1px solid #1e293b;margin-bottom:25px;}
            .nome-autor{font-weight:bold;color:#84cc16;font-size:18px;margin-bottom:10px;}
            .data-pub{color:#64748b;font-size:13px;margin-bottom:15px;}
            .texto-pub{font-size:16px;line-height:1.7;color:#e2e8f0;margin-bottom:15px;}
            .midia{width:100%;border-radius:12px;margin-bottom:15px;}
        </style>
    </head>
    <body>
        <div class="topo">
            <h1>JBS REDE SOCIAL</h1>
            <a href="/sair">Sair</a>
        </div>
        <div class="conteudo">
            <div class="btn-novo">
                <a href="/publicar">Nova Publicacao</a>
            </div>
            {% if publicacoes %}
                {% for p in publicacoes %}
                <div class="publicacao">
                    <div class="nome-autor">{{p.nome}}</div>
                    <div class="data-pub">{{p.data_publicacao}}</div>
                    {% if p.texto %}<div class="texto-pub">{{p.texto}}</div>{% endif %}
                    {% if p.arquivo %}
                        {% if p.tipo_arquivo in ['mp4','mov','avi','webm'] %}
                        <video controls class="midia">
                            <source src="/midia/{{p.arquivo}}">
                        </video>
                        {% else %}
                        <img src="/midia/{{p.arquivo}}" class="midia" alt="Arquivo">
                        {% endif %}
                    {% endif %}
                </div>
                {% endfor %}
            {% else %}
                <div style="text-align:center;padding:50px;color:#94a3b8;">
                    <h3>Ainda nao ha publicacoes</h3>
                    <p>Seja o primeiro a compartilhar algo!</p>
                </div>
            {% endif %}
        </div>
    </body>
    </html>
    ''', publicacoes=publicacoes)

# ==================== PUBLICAR ====================
@app.route("/publicar", methods=["GET","POST"])
def publicar():
    if not usuario_logado():
        return redirect(url_for("entrar"))

    if request.method == "POST":
        texto = request.form.get("texto","").strip()
        arquivo = request.files.get("arquivo")
        nome_arq = None
        tipo_arq = None

        if not texto and not (arquivo and arquivo.filename):
            return "Escreva algo ou escolha um arquivo <br><a href='/publicar' style='color:#84cc16;'>Voltar</a>"

        if arquivo and arquivo.filename and arquivo_valido(arquivo.filename):
            nome_arq = secure_filename(arquivo.filename)
            caminho_completo = os.path.join(app.config["UPLOAD_FOLDER"], nome_arq)
            arquivo.save(caminho_completo)
            tipo_arq = nome_arq.rsplit('.',1)[1].lower()

        conn = conectar_banco()
        conn.execute('''
            INSERT INTO publicacoes (usuario_id, texto, arquivo, tipo_arquivo)
            VALUES (?, ?, ?, ?)
        ''', (session["usuario_id"], texto, nome_arq, tipo_arq))
        conn.commit()
        conn.close()

        return redirect(url_for("feed"))

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Nova Publicacao</title>
        <style>
            *{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif;}
            body{background:linear-gradient(180deg,#0a0f1a 0%,#121a2b 100%);color:white;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;}
            .caixa{width:100%;max-width:580px;background:#121a2b;padding:35px;border-radius:16px;border:1px solid #1e293b;}
            h2{text-align:center;margin-bottom:25px;color:#84cc16;}
            textarea, input{width:100%;padding:16px;margin-bottom:20px;background:#0a0f1a;border:1px solid #334155;border-radius:10px;color:white;font-size:16px;}
            textarea:focus, input:focus{outline:none;border-color:#84cc16;}
            button{width:100%;padding:16px;background:#84cc16;color:#050505;border:none;border-radius:10px;font-weight:bold;font-size:17px;cursor:pointer;}
            button:hover{background:#65a30d;}
            a{color:#94a3b8;text-decoration:none;display:block;text-align:center;margin-top:20px;}
        </style>
    </head>
    <body>
        <div class="caixa">
            <h2>Compartilhe o que quiser</h2>
            <form method="POST" enctype="multipart/form-data">
                <textarea name="texto" rows="5" placeholder="Escreva sua mensagem (opcional)..."></textarea>
                <input type="file" name="arquivo" accept="image/*,video/*">
                <button type="submit">Publicar Agora</button>
                <a href="/feed">Voltar ao feed</a>
            </form>
        </div>
    </body>
    </html>
    ''')

# ==================== EXIBIR ARQUIVOS ====================
@app.route("/midia/<nome>")
def ver_midia(nome):
    return send_from_directory(app.config["UPLOAD_FOLDER"], nome)

# ==================== SAIR ====================
@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("inicio"))

# ==================== EXECUCAO ====================
if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta, debug=False)
