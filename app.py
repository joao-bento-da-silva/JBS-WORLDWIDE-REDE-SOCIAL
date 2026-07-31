 # ==================================================
# © 2026 JBS TECNOLOGIA — REDE SOCIAL COMPLETA E ESTÁVEL
# VERSÃO FINAL: CADASTRO, LOGIN E PUBLICAÇÕES SALVAS PARA SEMPRE
# DESIGN E IDENTIDADE VISUAL PRESERVADOS
# Compatível com Render / GoDaddy / cPanel
# ==================================================

from flask import Flask, request, session, redirect, url_for, render_template_string
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ==================== SEGURANÇA — CHAVES FORA DO CÓDIGO ====================
app.secret_key = os.environ.get("CHAVE_INTERNA_SEGURANCA")
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
CHAVE_MESTRA_DNA = os.environ.get("CHAVE_MESTRA_DNA")
BANCO_DADOS = "jbs_rede.db"
PASTA_MIDIA = "midia_publicacoes"
os.makedirs(PASTA_MIDIA, exist_ok=True)

# ==================== FUNÇÕES BÁSICAS ====================
def conectar_banco():
    conn = sqlite3.connect(BANCO_DADOS)
    conn.row_factory = sqlite3.Row
    return conn

def usuario_logado():
    return "usuario_id" in session

# ==================== CRIAR BANCO DE DADOS ====================
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
            return "Preencha todos os campos corretamente <br><a href='/cadastrar'>Voltar</a>"

        conn = conectar_banco()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO usuarios (nome,email,senha) VALUES (?,?,?)", (nome,email,senha))
            conn.commit()
            return redirect(url_for("entrar"))
        except sqlite3.IntegrityError:
            return "Esse e-mail já está cadastrado <br><a href='/cadastrar'>Voltar</a>"
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
            *{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif;}
            body{background:#0f172a;color:white;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;}
            .caixa{width:100%;max-width:450px;background:#1e293b;padding:35px;border-radius:15px;border:1px solid #334155;}
            h2{text-align:center;margin
