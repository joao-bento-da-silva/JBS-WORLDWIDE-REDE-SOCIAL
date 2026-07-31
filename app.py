 # ==================================================
# © 2026 JBS TECNOLOGIA — REDE SOCIAL FINAL COMPLETA
# VERSÃO COM: VÍDEO + FOTO + PUBLICAÇÕES SALVAS PARA SEMPRE
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

    c.execute('''
        CREATE TABLE IF NOT EXISTS comentarios (
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
            *{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif;}
            body{background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);color:white;min-height:100vh;}
            .cabecalho{padding:30px;text-align:center;border-bottom:1px solid #334155;}
            .cabecalho h1{color:#84cc16;font-size:36px;margin-bottom:10px;}
            .cabecalho p{color:#94a3b8;}
            .conteudo{max-width:900px;margin:50px auto;padding:20px;}
            .apresentacao{text-align:center;margin-bottom:60px;}
            .apresentacao h2{font-size:30px;margin-bottom:20px;color:#e2e8f0;}
            .apresentacao p{font-size:18px;line-height:1.7;color:#cbd5e1;}
            .botoes{display:flex;gap:25px;justify-content:center;flex-wrap:wrap;}
            .botao{padding:16px 40px;border-radius:10px;text-decoration:none;font-weight:bold;font-size:18px;transition:0.3s;}
            .botao.primario{background:#84cc16;color:#0f172a;}
            .botao.primario:hover{background:#65a30d;transform:scale(1.05);}
            .botao.secundario{background:#334155;color:white;border:1px solid #475569;}
            .botao.secundario:hover{background:#475569;}
            .rodape{text-align:center;padding:25px;color:#64748b;font-size:14px;margin-top:50px;}
        </style>
    </head>
    <body>
        <div class="cabecalho">
            <h1>JBS TECNOLOGIA</h1>
            <p>Sua Rede Social Conectada e Segura</p>
        </div>
        <div class="conteudo">
            <div class="apresentacao">
                <h2>Bem-vindo(a)</h2>
                <p>Conecte-se, compartilhe ideias, fotos e vídeos com segurança.<br>Tudo feito para você pela JBS TECNOLOGIA.</p>
            </div>
            <div class="botoes">
                <a href="/cadastrar" class="botao primario">Criar Nova Conta</a>
                <a href="/entrar" class="botao secundario">Acessar Minha Conta</a>
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
            return "Preencha todos os campos <br><a href='/cadastrar'>Voltar</a>"

        conn = conectar_banco()
        try:
            conn.execute("INSERT INTO usuarios (nome,email,senha) VALUES (?,?,?)", (nome,email,senha))
            conn.commit()
            return redirect(url_for("entrar"))
        except sqlite3.IntegrityError:
            return "E-mail já cadastrado <br><a href='/cadastrar'>Voltar</a>"
        finally:
            conn.close()

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cadastrar</title>
        <style>
            *{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif;}
            body{background:#0f172a;color:white;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;}
            .caixa{width:100%;max-width:450px;background:#1e293b;padding:35px;border-radius:15px;border:1px solid #334155;}
            h2{text-align:center;margin-bottom:30px;color:#84cc16;}
            input{width:100%;padding:15px;margin:10px 0 20px;background:#334155;border:1px solid #475569;border-radius:8px;color:white;font-size:16px;}
            button{width:100%;padding:15px;background:#84cc16;color:#0f172a;border:none;border-radius:8px;font-weight:bold;font-size:17px;cursor:pointer;}
            a{color:#94a3b8;text-decoration:none;display:block;text-align:center;margin-top:20px;}
        </style>
    </head>
    <body>
        <div class="caixa">
            <h2>Criar Conta</h2>
            <form method="POST">
                <input type="text" name="nome" placeholder="Seu nome" required>
                <input type="email" name="email" placeholder="Seu e-mail" required>
                <input type="password" name="senha" placeholder="Senha segura" required>
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
        return "E-mail ou senha errados <br><a href='/entrar'>Voltar</a>"

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Entrar</title>
        <style>
            *{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif;}
            body{background:#0f172a;color:white;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;}
            .caixa{width:100%;max-width:450px;background:#1e293b;padding:35px;border-radius:15px;border:1px solid #334155;}
            h2{text-align:center;margin-bottom:30px;color:#84cc16;}
            input{width:100%;padding:15px;margin:10px 0 20px;background:#334155;border:1px solid #475569;border-radius:8px;color:white;font-size:16px;}
            button{width:100%;padding:15px;background:#84cc16;color:#0f172a;border:none;border-radius:8px;font-weight:bold;font-size:17px;cursor:pointer;}
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
                <a href="/cadastrar">Não tem conta? Crie uma</a>
            </form>
        </div>
    </body>
    </html>
    ''')

# ==================== FEED COM FOTO E VÍDEO ====================
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
        <title>Feed</title>
        <style>
            *{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif;}
            body{background:#0f172a;color:white;}
            .topo{padding:20px 30px;background:#1e293b;border-bottom:1px solid #334155;display:flex;justify-content:space-between;align-items:center;}
            .topo h1{color:#84cc16;font-size:24px;}
            .topo a{color:#ef4444;text-decoration:none;font-weight:bold;}
            .conteudo{max-width:700px;margin:30px auto;padding:0 20px;}
            .botao-publicar{margin-bottom:30px;text-align:center;}
            .botao-publicar a{padding:12px 30px;background:#84cc16;color:#0f172a;border-radius:8px;text-decoration:none;font-weight:bold;display:inline-block;}
            .publicacao{background:#1e293b;padding:20px;border-radius:12px;border:1px solid #334155;margin-bottom:25px;}
            .publicacao .nome{font-weight:bold;color:#84cc16;margin-bottom:10px;}
            .publicacao .data{color:#64748b;font-size:13px;margin-bottom:15px;}
            .publicacao .texto{color:#e2e8f0;line-height:1.6;margin-bottom:15px;}
            .midia{max-width:100%;border-radius:8px;margin-bottom:15px;}
            .acoes{display:flex;gap:20px;color:#94a3b8;font-size:15px;}
        </style>
    </head>
    <body>
        <div class="topo">
            <h1>JBS REDE SOCIAL</h1>
            <a href="/sair">Sair</a>
        </div>
        <div class="conteudo">
            <div class="botao-publicar">
                <a href="/publicar">+ Nova Publicação</a>
            </div>
            {% for p in publicacoes %}
            <div class="publicacao">
                <div class="nome">{{p.nome}}</div>
                <div class="data">{{p.data_publicacao}}</div>
                {% if p.texto %}<div class="texto">{{p.texto}}</div>{% endif %}
                {% if p.arquivo %}
                    {% if p.tipo_arquivo in ['mp4','mov','avi','webm'] %}
                    <video controls class="midia">
                        <source src="/midia/{{p.arquivo}}">
                        Vídeo não suportado
                    </video>
                    {% else %}
                    <img src="/midia/{{p.arquivo}}" class="midia" alt="Imagem">
                    {% endif %}
                {% endif %}
                <div class="acoes">❤️ {{p.total_curtidas}} | 💬 Comentários</div>
            </div>
            {% endfor %}
        </div>
    </body>
    </html>
    ''', publicacoes=publicacoes)

# ==================== PUBLICAR — ACEITA FOTO E VÍDEO ====================
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

        # SALVA NO BANCO — NUNCA MAIS SOME
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
            *{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif;}
            body{background:#0f172a;color:white;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;}
            .caixa{width:100%;max-width:550px;background:#1e293b;padding:30px;border-radius:15px;border:1px solid #334155;}
            h2{text-align:center;margin-bottom:25px;color:#84cc16;}
            textarea, input{width:100%;padding:14px;margin:8px 0 18px;background:#334155;border:1px solid #475569;border-radius:8px;color:white;font-size:16px;}
            button{width:100%;padding:14px;background:#84cc16;color:#0f172a;border:none;border-radius:8px;font-weight:bold;font-size:17px;cursor:pointer;}
            a{color:#94a3b8;text-decoration:none;display:block;text-align:center;margin-top:15px;}
        </style>
    </head>
    <body>
        <div class="caixa">
            <h2>Compartilhe algo</h2>
            <form method="POST" enctype="multipart/form-data">
                <textarea name="texto" rows="5" placeholder="Escreva sua mensagem..." required></textarea>
                <input type="file" name="arquivo" accept="image/*,video/*">
                <button type="submit">Publicar</button>
                <a href="/feed">Voltar</a>
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
