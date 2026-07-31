 # ==================================================
# © 2026 JBS TECNOLOGIA — REDE SOCIAL COM DESIGN BONITO
# VERSÃO FINAL: FOTO + VÍDEO + PUBLICAÇÕES + VISUAL PROFISSIONAL
# ==================================================

from flask import Flask, request, session, redirect, url_for, render_template_string, send_from_directory
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ==================== SEGURANÇA ====================
app.secret_key = os.environ.get("CHAVE_INTERNA_SEGURANCA")
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
CHAVE_MESTRA_DNA = os.environ.get("CHAVE_MESTRA_DNA")
BANCO_DADOS = "jbs_rede.db"
PASTA_MIDIA = "midia_publicacoes"
os.makedirs(PASTA_MIDIA, exist_ok=True)

# ==================== FUNÇÕES ====================
def conectar_banco():
    conn = sqlite3.connect(BANCO_DADOS)
    conn.row_factory = sqlite3.Row
    return conn

def usuario_logado():
    return "usuario_id" in session

# ==================== CRIAR BANCO ====================
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
            texto TEXT NOT NULL,
            arquivo TEXT,
            tipo_arquivo TEXT,
            destacada INTEGER DEFAULT 0,
            data_publicacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS curtidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            publicacao_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY (publicacao_id) REFERENCES publicacoes(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            UNIQUE(publicacao_id, usuario_id)
        )
    ''')

    conn.commit()
    conn.close()

iniciar_banco()

# ==================== PÁGINA INICIAL ====================
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
            *{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI',Arial,sans-serif;}
            body{background:linear-gradient(180deg,#0a0f1a 0%,#121a2b 100%);color:#e2e8f0;min-height:100vh;}
            .cabecalho{padding:25px 20px;background:rgba(0,0,0,0.3);border-bottom:1px solid #1e293b;}
            .cabecalho h1{color:#84cc16;font-size:32px;text-align:center;font-weight:800;letter-spacing:1px;}
            .conteudo{max-width:650px;margin:40px auto;padding:0 20px;}
            .boasvindas{text-align:center;margin-bottom:50px;}
            .boasvindas h2{font-size:28px;margin-bottom:15px;color:#ffffff;}
            .boasvindas p{font-size:17px;line-height:1.8;color:#94a3b8;}
            .grupo-botoes{display:flex;gap:20px;justify-content:center;flex-wrap:wrap;}
            .botao{padding:15px 35px;border-radius:12px;text-decoration:none;font-weight:bold;font-size:17px;border:none;cursor:pointer;transition:all 0.3s ease;}
            .botao.verde{background:#84cc16;color:#050505;box-shadow:0 0 15px rgba(132,204,22,0.3);}
            .botao.verde:hover{background:#65a30d;transform:translateY(-2px);}
            .botao.escuro{background:#1e293b;color:#ffffff;border:1px solid #334155;}
            .botao.escuro:hover{background:#334155;transform:translateY(-2px);}
            .rodape{text-align:center;padding:30px;color:#64748b;font-size:14px;}
        </style>
    </head>
    <body>
        <div class="cabecalho">
            <h1>JBS TECNOLOGIA</h1>
        </div>
        <div class="conteudo">
            <div class="boasvindas">
                <h2>Bem-vindo à sua rede social</h2>
                <p>Conecte-se, compartilhe fotos, vídeos e ideias com segurança.<br>Tudo feito com a qualidade JBS TECNOLOGIA.</p>
            </div>
            <div class="grupo-botoes">
                <a href="/cadastrar" class="botao verde">Criar Nova Conta</a>
                <a href="/entrar" class="botao escuro">Entrar na Conta</a>
            </div>
        </div>
        <div class="rodape">© 2026 JBS TECNOLOGIA — Todos os direitos reservados</div>
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
            return "Preencha todos os campos corretamente <br><a href='/cadastrar' style='color:#84cc16;'>Voltar</a>"

        conn = conectar_banco()
        try:
            conn.execute("INSERT INTO usuarios (nome,email,senha) VALUES (?,?,?)", (nome,email,senha))
            conn.commit()
            return redirect(url_for("entrar"))
        except sqlite3.IntegrityError:
            return "Esse e-mail já está cadastrado <br><a href='/cadastrar' style='color:#84cc16;'>Voltar</a>"
        finally:
            conn.close()

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cadastrar Conta</title>
        <style>
            *{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI',Arial,sans-serif;}
            body{background:linear-gradient(180deg,#0a0f1a 0%,#121a2b 100%);color:white;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;}
            .caixa{width:100%;max-width:480px;background:#121a2b;padding:40px;border-radius:16px;border:1px solid #1e293b;box-shadow:0 0 25px rgba(0,0,0,0.5);}
            h2{text-align:center;margin-bottom:30px;color:#84cc16;font-size:26px;}
            .campo{margin-bottom:20px;}
            input{width:100%;padding:16px;background:#0a0f1a;border:1px solid #334155;border-radius:10px;color:white;font-size:16px;}
            input:focus{outline:none;border-color:#84cc16;}
            button{width:100%;padding:16px;background:#84cc16;color:#050505;border:none;border-radius:10px;font-weight:bold;font-size:17px;cursor:pointer;transition:0.3s;}
            button:hover{background:#65a30d;}
            a{color:#94a3b8;text-decoration:none;display:block;text-align:center;margin-top:20px;}
        </style>
    </head>
    <body>
        <div class="caixa">
            <h2>Criar Sua Conta</h2>
            <form method="POST">
                <div class="campo"><input type="text" name="nome" placeholder="Seu nome completo" required></div>
                <div class="campo"><input type="email" name="email" placeholder="Seu melhor e-mail" required></div>
                <div class="campo"><input type="password" name="senha" placeholder="Crie uma senha segura" required></div>
                <button type="submit">Finalizar Cadastro</button>
                <a href="/">Voltar ao início</a>
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
        return "E-mail ou senha incorretos <br><a href='/entrar' style='color:#84cc16;'>Voltar</a>"

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Acessar Conta</title>
        <style>
            *{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI',Arial,sans-serif;}
            body{background:linear-gradient(180deg,#0a0f1a 0%,#121a2b 100%);color:white;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;}
            .caixa{width:100%;max-width:480px;background:#121a2b;padding:40px;border-radius:16px;border:1px solid #1e293b;box-shadow:0 0 25px rgba(0,0,0,0.5);}
            h2{text-align:center;margin-bottom:30px;color:#84cc16;font-size:26px;}
            .campo{margin-bottom:20px;}
            input{width:100%;padding:16px;background:#0a0f1a;border:1px solid #334155;border-radius:10px;color:white;font-size:16px;}
            input:focus{outline:none;border-color:#84cc16;}
            button{width:100%;padding:16px;background:#84cc16;color:#050505;border:none;border-radius:10px;font-weight:bold;font-size:17px;cursor:pointer;transition:0.3s;}
            button:hover{background:#65a30d;}
            a{color:#94a3b8;text-decoration:none;display:block;text-align:center;margin-top:20px;}
        </style>
    </head>
    <body>
        <div class="caixa">
            <h2>Acessar Minha Conta</h2>
            <form method="POST">
                <div class="campo"><input type="email" name="email" placeholder="Seu e-mail cadastrado" required></div>
                <div class="campo"><input type="password" name="senha" placeholder="Sua senha" required></div>
                <button type="submit">Entrar</button>
                <a href="/cadastrar">Não tem conta? Crie uma agora</a>
                <a href="/">Voltar ao início</a>
            </form>
        </div>
    </body>
    </html>
    ''')

# ==================== FEED BONITO E FUNCIONAL ====================
@app.route("/feed")
def feed():
    if not usuario_logado():
        return redirect(url_for("entrar"))

    conn = conectar_banco()
    publicacoes = conn.execute('''
        SELECT p.*, u.nome,
            (SELECT COUNT(*) FROM curtidas WHERE publicacao_id = p.id) AS total_curtidas,
            CASE WHEN EXISTS(SELECT 1 FROM curtidas WHERE publicacao_id = p.id AND usuario_id = ?)
            THEN 1 ELSE 0 END AS curtiu
        FROM publicacoes p
        JOIN usuarios u ON p.usuario_id = u.id
        ORDER BY p.destacada DESC, p.data_publicacao DESC
    ''', (session["usuario_id"],)).fetchall()
    conn.close()

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Feed — JBS Rede Social</title>
        <style>
            *{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI',Arial,sans-serif;}
            body{background:linear-gradient(180deg,#0a0f1a 0%,#121a2b 100%);color:#e2e8f0;}
            .topo{padding:20px;background:rgba(0,0,0,0.3);border-bottom:1px solid #1e293b;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:10;}
            .topo h1{color:#84cc16;font-size:26px;font-weight:800;}
            .topo a{color:#ef4444;text-decoration:none;font-weight:bold;padding:8px 15px;border-radius:8px;transition:0.3s;}
            .topo a:hover{background:rgba(239,68,68,0.1);}
            .conteudo{max-width:650px;margin:30px auto;padding:0 15px;}
            .btn-novo{text-align:center;margin-bottom:35px;}
            .btn-novo a{padding:14px 35px;background:#84cc16;color:#050505;border-radius:12px;text-decoration:none;font-weight:bold;font-size:16px;display:inline-block;box-shadow:0 0 15px rgba(132,204,22,0.25);transition:0.3s;}
            .btn-novo a:hover{background:#65a30d;transform:translateY(-2px);}
            .publicacao{background:#121a2b;padding:22px;border-radius:16px;border:1px solid #1e293b;margin-bottom:25px;box-shadow:0 4px 12px rgba(0,0,0,0.3);}
            .cabecalho-pub{display:flex;justify-content:space-between;align-items:center;margin-bottom:15px;}
            .nome-autor{font-weight:bold;color:#84cc16;font-size:18px;}
            .data-pub{color:#64748b;font-size:13px;}
            .texto-pub{font-size:16px;line-height:1.7;color:#e2e8f0;margin-bottom:18px;}
            .midia{width:100%;border-radius:12px;margin-bottom:18px;}
            .acoes-pub{display:flex;gap:25px;color:#94a3b8;font-size:15px;padding-top:10px;border-top:1px solid #1e293b;}
        </style>
    </head>
    <body>
        <div class="topo">
            <h1>JBS REDE SOCIAL</h1>
            <a href="/sair">Sair</a>
        </div>
        <div class="conteudo">
            <div class="btn-novo">
                <a href="/publicar">+ Nova Publicação</a>
            </div>
            {% if publicacoes %}
                {% for p in publicacoes %}
                <div class="publicacao">
                    <div class="cabecalho-pub">
                        <span class="nome-autor">{{p.nome}}</span>
                        <span class="data-pub">{{p.data_publicacao}}</span>
                    </div>
                    {% if p.texto %}<div class="texto-pub">{{p.texto}}</div>{% endif %}
                    {% if p.arquivo %}
                        {% if p.tipo_arquivo in ['mp4','mov','avi','webm'] %}
                        <video controls class="midia">
                            <source src="/midia/{{p.arquivo}}">
                            Seu navegador não suporta reproduzir esse vídeo.
                        </video>
                        {% else %}
                        <img src="/midia/{{p.arquivo}}" class="midia" alt="Imagem da publicação">
                        {% endif %}
                    {% endif %}
                    <div class="acoes-pub">
                        <span>❤️ {{p.total_curtidas}}</span>
                        <span>💬 Comentários</span>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div style="text-align:center;padding:50px;color:#94a3b8;">
                    <h3>Ainda não há publicações</h3>
                    <p>Seja o primeiro a compartilhar algo!</p>
                </div>
            {% endif %}
        </div>
    </body>
    </html>
    ''', publicacoes=publicacoes)

# ==================== PUBLICAR COM FOTO E VÍDEO ====================
@app.route("/publicar", methods=["GET","POST"])
def publicar():
    if not usuario_logado():
        return redirect(url_for("entrar"))

    if request.method == "POST":
        texto = request.form.get("texto","").strip()
        arquivo = request.files.get("arquivo")
        nome_arq = None
        tipo_arq = None

        if arquivo and arquivo.filename:
            nome_arq = secure_filename(arquivo.filename)
            caminho = os.path.join(PASTA_MIDIA, nome_arq)
            arquivo.save(caminho)
            tipo_arq = nome_arq.rsplit('.',1)[-1].lower()

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
        <title>Nova Publicação</title>
        <style>
            *{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI',Arial,sans-serif;}
            body{background:linear-gradient(180deg,#0a0f1a 0%,#121a2b 100%);color:white;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;}
            .caixa{width:100%;max-width:580px;background:#121a2b;padding:35px;border-radius:16px;border:1px solid #1e293b;box-shadow:0 0 25px rgba(0,0,0,0.5);}
            h2{text-align:center;margin-bottom:25px;color:#84cc16;}
            textarea, input{width:100%;padding:16px;margin-bottom:20px;background:#0a0f1a;border:1px solid #334155;border-radius:10px;color:white;font-size:16px;}
            textarea:focus, input:focus{outline:none;border-color:#84cc16;}
            button{width:100%;padding:16px;background:#84cc16;color:#050505;border:none;border-radius:10px;font-weight:bold;font-size:17px;cursor:pointer;transition:0.3s;}
            button:hover{background:#65a30d;}
            a{color:#94a3b8;text-decoration:none;display:block;text-align:center;margin-top:20px;}
        </style>
    </head>
    <body>
        <div class="caixa">
            <h2>Compartilhe o que quiser</h2>
            <form method="POST" enctype="multipart/form-data">
                <textarea name="texto" rows="5" placeholder="Escreva sua mensagem aqui..." required></textarea>
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
    return send_from_directory(PASTA_MIDIA, nome)

# ==================== SAIR ====================
@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("inicio"))

# ==================== EXECUÇÃO ====================
if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta, debug=False)
