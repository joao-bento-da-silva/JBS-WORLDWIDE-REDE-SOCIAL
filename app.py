  # ==================================================
# © 2026 JNB TECNOLOGIA — PLATAFORMA COMPLETA
# LOGIN · CADASTRO · PAINEL · LOJA · LICENÇA · REGISTRO BNJ
# IDENTIDADE VISUAL COMPLETA · SEM DEPENDÊNCIAS EXTRAS
# ==================================================

from flask import Flask, request, session, redirect, url_for, render_template_string, send_file
import sqlite3
import os
import random
import uuid
import hashlib
from datetime import datetime, timedelta
import base64

app = Flask(__name__)
app.secret_key = os.environ.get("CHAVE_UNIFICADA", "JNB_TECNOLOGIA_2026_SEGURA")

# 🔐 SUA CHAVE MESTRA — NÃO MEXE
CHAVE_MESTRA_JNB = "21054551774858609435694112838216077829"

# ----------------------
# BANCO DE DADOS
# ----------------------
def init_db():
    conn = sqlite3.connect("jnb.db")
    c = conn.cursor()
    
    c.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        email TEXT UNIQUE,
        senha TEXT,
        pontos INTEGER DEFAULT 0
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS licencas_bnj (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        chave_licenca TEXT UNIQUE,
        plano TEXT,
        hardware_id TEXT,
        status TEXT DEFAULT 'ativa',
        data_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_expiracao TIMESTAMP,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS pagamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        plano TEXT,
        valor REAL,
        forma_pagamento TEXT,
        status TEXT DEFAULT 'pendente',
        data_pagamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )""")
    
    conn.commit()
    conn.close()

init_db()

def usuario_logado():
    return session.get("usuario_id")

# ----------------------
# LICENÇA — APENAS MÓDULOS NATIVOS
# ----------------------
def gerar_licenca_assinada(email, plano, data_expiracao):
    dados = f"{email}|{plano}|{data_expiracao.isoformat()}"
    assinatura = hashlib.sha256((dados + CHAVE_MESTRA_JNB).encode()).hexdigest()[:32]
    licenca_gerada = f"BNJ:{base64.urlsafe_b64encode(dados.encode()).decode()}:{assinatura}"
    return licenca_gerada

def validar_licenca(chave_licenca, email, hardware_id):
    try:
        partes = chave_licenca.split(":")
        if len(partes) != 3 or partes[0] != "BNJ":
            return False, "Formato de licença inválido"
        dados = base64.urlsafe_b64decode(partes[1]).decode()
        assinatura_original = partes[2]
        assinatura_calculada = hashlib.sha256((dados + CHAVE_MESTRA_JNB).encode()).hexdigest()[:32]
        if assinatura_calculada != assinatura_original:
            return False, "Licença inválida ou falsificada"
        lic_email, lic_plano, lic_data_exp = dados.split("|")
        if lic_email != email:
            return False, "Licença pertence a outro usuário"
        if datetime.fromisoformat(lic_data_exp) < datetime.now():
            return False, "Licença expirada"
        return True, lic_plano
    except Exception as e:
        return False, f"Erro na validação: {str(e)}"

# ----------------------
# ROTAS BÁSICAS COM IDENTIDADE VISUAL
# ----------------------
@app.route("/", methods=["GET"])
def index():
    if usuario_logado():
        return redirect(url_for("painel"))
    return redirect(url_for("entrar"))

@app.route("/cadastrar", methods=["GET","POST"])
def cadastrar():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = hashlib.sha256(request.form.get("senha").encode()).hexdigest()
        try:
            conn = sqlite3.connect("jnb.db")
            c = conn.cursor()
            c.execute("INSERT INTO usuarios (nome, email, senha, pontos) VALUES (?, ?, ?, ?)",
                      (nome, email, senha, 1000)) # bônus de 1000 pontos ao cadastrar
            conn.commit()
            conn.close()
            return redirect(url_for("entrar"))
        except sqlite3.IntegrityError:
            return render_template_string(TEMPLATE_ERRO, mensagem="E-mail já cadastrado!")
    return render_template_string(TEMPLATE_CADASTRAR)

@app.route("/entrar", methods=["GET","POST"])
def entrar():
    if request.method == "POST":
        email = request.form.get("email")
        senha = hashlib.sha256(request.form.get("senha").encode()).hexdigest()
        conn = sqlite3.connect("jnb.db")
        c = conn.cursor()
        c.execute("SELECT id, nome FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
        usuario = c.fetchone()
        conn.close()
        if usuario:
            session["usuario_id"] = usuario[0]
            return redirect(url_for("painel"))
        return render_template_string(TEMPLATE_ERRO, mensagem="E-mail ou senha inválidos!")
    return render_template_string(TEMPLATE_ENTRAR)

@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("entrar"))

@app.route("/painel")
def painel():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    conn = sqlite3.connect("jnb.db")
    c = conn.cursor()
    c.execute("SELECT nome, pontos FROM usuarios WHERE id = ?", (session["usuario_id"],))
    nome, pontos = c.fetchone()
    conn.close()
    return render_template_string(TEMPLATE_PAINEL, nome=nome, pontos=pontos)

# ----------------------
# LOJA DE PRÊMIOS
# ----------------------
@app.route("/loja_premios", methods=["GET","POST"])
def loja_premios():
    if not usuario_logado(): return redirect(url_for("entrar"))
    usuario_id = session["usuario_id"]
    mensagem = ""
    
    planos = [
        {"id":1, "nome":"Plano Básico BNJ", "desc":"30 dias · Varrer + Reparar + Gerar Chaves · 1 dispositivo", "valor":49.90, "pontos":500, "dias":30},
        {"id":2, "nome":"Plano Profissional BNJ", "desc":"90 dias · Todas as funções · Suporte prioritário · 2 dispositivos", "valor":129.90, "pontos":1200, "dias":90},
        {"id":3, "nome":"Plano Empresarial BNJ", "desc":"365 dias · Todas as funções · Suporte VIP · 5 dispositivos", "valor":399.90, "pontos":3500, "dias":365}
    ]
    
    conn = sqlite3.connect("jnb.db")
    c = conn.cursor()
    c.execute("SELECT pontos, email FROM usuarios WHERE id = ?", (usuario_id,))
    pontos_usuario, email_usuario = c.fetchone()
    
    if request.method == "POST":
        plano_id = int(request.form.get("plano_id"))
        forma = request.form.get("forma_pagamento")
        plano = next((p for p in planos if p["id"] == plano_id), None)
        
        c.execute("""INSERT INTO pagamentos (usuario_id, plano, valor, forma_pagamento, status)
                     VALUES (?, ?, ?, ?, ?)""",
                  (usuario_id, plano["nome"], plano["valor"], forma, "aprovado"))
        
        data_exp = datetime.now() + timedelta(days=plano["dias"])
        licenca = gerar_licenca_assinada(email_usuario, plano["nome"], data_exp)
        
        c.execute("""INSERT INTO licencas_bnj (usuario_id, chave_licenca, plano, data_expiracao)
                     VALUES (?, ?, ?, ?)""",
                  (usuario_id, licenca, plano["nome"], data_exp))
        
        if forma == "pontos" and pontos_usuario >= plano["pontos"]:
            c.execute("UPDATE usuarios SET pontos = ? WHERE id = ?", (pontos_usuario - plano["pontos"], usuario_id))
            pontos_usuario -= plano["pontos"]
        
        conn.commit()
        mensagem = "✅ Pagamento confirmado! Acesse o Registro BNJ para baixar o instalador."
    
    conn.close()
    return render_template_string(TEMPLATE_LOJA, planos=planos, pontos=pontos_usuario, mensagem=mensagem)

# ----------------------
# REGISTRO BNJ
# ----------------------
@app.route("/registro_bnj")
def registro_bnj():
    if not usuario_logado(): return redirect(url_for("entrar"))
    usuario_id = session["usuario_id"]
    
    conn = sqlite3.connect("jnb.db")
    c = conn.cursor()
    c.execute("""SELECT chave_licenca, plano, data_expiracao 
                 FROM licencas_bnj 
                 WHERE usuario_id = ? AND status = 'ativa' AND data_expiracao > ?""",
              (usuario_id, datetime.now()))
    licenca = c.fetchone()
    conn.close()
    
    if not licenca:
        return render_template_string("""
        <div style="font-family:Arial; background:#0f172a; color:white; min-height:100vh; padding:50px 20px; text-align:center;">
            <h1 style="color:#ef4444;">🧬 Registro BNJ — JNB TECNOLOGIA</h1>
            <p style="font-size:18px; margin:30px 0;">Você ainda não possui uma licença ativa.</p>
            <a href="/loja_premios" style="background:#3b82f6; color:white; padding:15px 30px; border-radius:10px; text-decoration:none; font-weight:bold;">Adquirir Licença</a>
        </div>
        """)
    
    chave_licenca, plano, data_expiracao = licenca
    return render_template_string(TEMPLATE_REGISTRO_BNJ, chave_licenca=chave_licenca, plano=plano, data_expiracao=data_expiracao)

# ----------------------
# DOWNLOAD E API DE ATIVAÇÃO
# ----------------------
@app.route("/download_instalador")
def download_instalador():
    return "⚠️ Coloque o instalador BNJ_Registro_Setup.exe na pasta 'instaladores' do servidor."

@app.route("/api/ativar_licenca", methods=["POST"])
def ativar_licenca():
    dados = request.get_json()
    valida, msg = validar_licenca(dados.get("chave_licenca"), dados.get("email"), dados.get("hardware_id"))
    if not valida: return {"status":"invalida", "mensagem":msg}
    conn = sqlite3.connect("jnb.db")
    c = conn.cursor()
    c.execute("UPDATE licencas_bnj SET hardware_id = ? WHERE chave_licenca = ?", (dados.get("hardware_id"), dados.get("chave_licenca")))
    conn.commit()
    conn.close()
    return {"status":"ativa", "mensagem":"Licença ativada com sucesso!"}

# ----------------------
# TEMPLATES HTML COM IDENTIDADE JNB
# ----------------------
TEMPLATE_ENTRAR = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Entrar — JNB TECNOLOGIA</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; font-family:Arial,sans-serif; }
        body { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color:white; min-height:100vh; display:flex; align-items:center; justify-content:center; padding:20px; }
        .container { background:#1e293b; padding:40px 30px; border-radius:20px; width:100%; max-width:420px; box-shadow:0 8px 32px rgba(0,0,0,0.3); }
        .logo { text-align:center; margin-bottom:30px; }
        .logo-icon { font-size:64px; background:linear-gradient(45deg, #ef4444, #8b5cf6, #3b82f6); -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-weight:bold; }
        h1 { color:#4ade80; font-size:26px; margin:10px 0 5px; }
        .slogan { color:#94a3b8; font-size:14px; margin-bottom:30px; }
        form { display:flex; flex-direction:column; gap:18px; }
        input { padding:14px; font-size:16px; border:none; border-radius:10px; background:#0f172a; color:white; }
        button { padding:14px; background:#4ade80; color:#0f172a; font-weight:bold; font-size:16px; border:none; border-radius:10px; cursor:pointer; margin-top:10px; }
        button:hover { background:#22c55e; }
        .link { text-align:center; margin-top:25px; color:#94a3b8; font-size:14px; }
        .link a { color:#4ade80; text-decoration:none; font-weight:bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <div class="logo-icon">🧬</div>
            <h1>JNB TECNOLOGIA</h1>
            <div class="slogan">Plataforma de Autoridade · Registro BNJ · Licenças</div>
        </div>
        <form method="POST">
            <input type="email" name="email" placeholder="Seu e-mail" required>
            <input type="password" name="senha" placeholder="Sua senha" required>
            <button type="submit">🔑 Entrar na Plataforma</button>
        </form>
        <div class="link">
            Não tem conta? <a href="/cadastrar">Criar conta agora</a>
        </div>
    </div>
</body>
</html>
'''

TEMPLATE_CADASTRAR = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cadastrar — JNB TECNOLOGIA</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; font-family:Arial,sans-serif; }
        body { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color:white; min-height:100vh; display:flex; align-items:center; justify-content:center; padding:20px; }
        .container { background:#1e293b; padding:40px 30px; border-radius:20px; width:100%; max-width:420px; box-shadow:0 8px 32px rgba(0,0,0,0.3); }
        .logo { text-align:center; margin-bottom:30px; }
        .logo-icon { font-size:48px; background:linear-gradient(45deg, #ef4444, #8b5cf6, #3b82f6); -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-weight:bold; }
        h1 { color:#4ade80; font-size:24px; margin:10px 0 20px; }
        form { display:flex; flex-direction:column; gap:18px; }
        input { padding:14px; font-size:16px; border:none; border-radius:10px; background:#0f172a; color:white; }
        button { padding:14px; background:#4ade80; color:#0f172a; font-weight:bold; font-size:16px; border:none; border-radius:10px; cursor:pointer; }
        button:hover { background:#22c55e; }
        .link { text-align:center; margin-top:25px; color:#94a3b8; font-size:14px; }
        .link a { color:#4ade80; text-decoration:none; font-weight:bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <div class="logo-icon">🧬</div>
            <h1>Criar Conta — JNB TECNOLOGIA</h1>
        </div>
        <form method="POST">
            <input name="nome" placeholder="Seu nome completo" required>
            <input name="email" type="email" placeholder="Seu e-mail" required>
            <input name="senha" type="password" placeholder="Crie uma senha segura" required>
            <button type="submit">📝 Cadastrar</button>
        </form>
        <div class="link">
            Já tem conta? <a href="/entrar">Voltar para o login</a>
        </div>
    </div>
</body>
</html>
'''

TEMPLATE_PAINEL = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel — JNB TECNOLOGIA</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; font-family:Arial,sans-serif; }
        body { background:#0f172a; color:white; min-height:100vh; padding:30px 20px; }
        .container { max-width:600px; margin:0 auto; }
        .header { text-align:center; margin-bottom:40px; }
        .logo-icon { font-size:48px; background:linear-gradient(45deg, #ef4444, #8b5cf6, #3b82f6); -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-weight:bold; }
        h1 { color:#4ade80; font-size:28px; margin:10px 0 5px; }
        .subtitulo { color:#94a3b8; font-size:16px; margin-bottom:20px; }
        .user-info { background:#1e293b; padding:20px; border-radius:12px; text-align:center; margin-bottom:30px; }
        .user-name { font-size:20px; font-weight:bold; margin-bottom:8px; }
        .user-points { color:#fbbf24; font-size:18px; }
        .menu { display:flex; flex-direction:column; gap:15px; }
        .menu a { padding:18px; border-radius:12px; text-align:center; text-decoration:none; font-weight:bold; font-size:18px; transition:transform 0.2s; }
        .menu a:hover { transform:translateY(-2px); }
        .btn-loja { background:#3b82f6; color:white; }
        .btn-registro { background:#8b5cf6; color:white; }
        .btn-sair { background:#ef4444; color:white; margin-top:10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo-icon">🧬</div>
            <h1>JNB TECNOLOGIA</h1>
            <div class="subtitulo">Painel de Controle</div>
        </div>
        <div class="user-info">
            <div class="user-name">Bem-vindo, {{ nome }}!</div>
            <div class="user-points">🏆 Seus Pontos: {{ pontos }}</div>
        </div>
        <div class="menu">
            <a href="/loja_premios" class="btn-loja">🏆 Loja de Prêmios & Licenças</a>
            <a href="/registro_bnj" class="btn-registro">🧬 Registro BNJ</a>
            <a href="/sair" class="btn-sair">🚪 Sair da Plataforma</a>
        </div>
    </div>
</body>
</html>
'''

TEMPLATE_LOJA = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Loja de Prêmios — JNB TECNOLOGIA</title>
    <style>
        * { box-sizing:border-box; margin:0; padding:0; font-family:Arial,sans-serif; }
        body { background:#0f172a; color:white; min-height:100vh; padding:30px 20px; }
        .container { max-width:480px; margin:0 auto; }
        h1 { color:#fbbf24; text-align:center; margin-bottom:30px; font-size:28px; }
        .saldo { text-align:center; font-size:18px; margin-bottom:30px; color:#4ade80; }
        .mensagem { text-align:center; font-weight:bold; margin:20px 0; padding:15px; border-radius:10px; color:#22c55e; background:#064e3b; }
        .plano { background:#1e293b; border-radius:16px; padding:25px; margin-bottom:20px; }
        .plano h2 { color:#fbbf24; margin-bottom:15px; font-size:22px; }
        .preco { font-size:24px; font-weight:bold; margin-bottom:10px; color:#f1f5f9; }
        .descricao { color:#cbd5e1; margin-bottom:20px; line-height:1.5; }
        select { width:100%; padding:12px; border-radius:8px; background:#0f172a; color:white; border:none; font-size:16px; margin-bottom:15px; }
        .btn { width:100%; padding:14px; border-radius:10px; background:#22c55e; color:black; font-weight:bold; font-size:18px; border:none; cursor:pointer; }
        .btn:hover { background:#16a34a; }
        .voltar { display:block; text-align:center; color:#4ade80; font-size:18px; text-decoration:none; margin-top:30px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏆 Loja de Prêmios & Licenças</h1>
        <div class="saldo">Seus Pontos: {{ pontos }}</div>
        {% if mensagem %}<div class="mensagem">{{ mensagem }}</div>{% endif %}
        {% for p in planos %}
        <div class="plano">
            <h2>{{ p.nome }}</h2>
            <div class="preco">R$ {{ "%.2f"|format(p.valor) }} ou {{ p.pontos }} pts</div>
            <div class="descricao">{{ p.desc }}</div>
            <form method="POST">
                <input type="hidden" name="plano_id" value="{{ p.id }}">
                <select name="forma_pagamento" required>
                    <option value="">-- Forma de Pagamento --</option>
                    <option value="pix">PIX</option>
                    <option value="cartao">Cartão de Crédito</option>
                    <option value="boleto">Boleto Bancário</option>
                    <option value="pontos">Usar {{ p.pontos }} Pontos</option>
                </select>
                <button type="submit" class="btn">Adquirir Licença</button>
            </form>
        </div>
        {% endfor %}
        <a href="/painel" class="voltar">← Voltar ao Painel</a>
    </div>
</body>
</html>
'''

TEMPLATE_REGISTRO_BNJ = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Registro BNJ — JNB TECNOLOGIA</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; font-family:Arial,sans-serif; }
        body { background:#0f172a; color:white; min-height:100vh; padding:30px 20px; }
        .container { max-width:480px; margin:0 auto; }
        .header { text-align:center; margin-bottom:40px; }
        .logo-icon { font-size:48px; background:linear-gradient(45deg, #ef4444, #8b5cf6, #3b82f6); -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-weight:bold; }
        h1 { color:#4ade80; margin:15px 0; }
        .plano { background:#1e293b; border-radius:16px; padding:25px; margin-bottom:30px; }
        .plano p { margin-bottom:12px; font-size:16px; }
        .chave { word-break:break-all; font-size:13px; color:#94a3b8; padding:10px; background:#0f172a; border-radius:8px; }
        .download { background:#064e3b; border-radius:16px; padding:30px; text-align:center; margin-bottom:30px; }
        .download h3 { margin-bottom:15px; color:#4ade80; }
        .btn-download { background:#22c55e; color:black; padding:15px 30px; border-radius:10px; text-decoration:none; font-weight:bold; display:inline-block; }
        .ativacao { background:#1e293b; border-radius:16px; padding:25px; margin-bottom:30px; }
        .ativacao h3 { margin-bottom:15px; color:#4ade80; }
        ol { padding-left:20px; line-height:1.6; color:#cbd5e1; }
        .voltar { display:block; text-align:center; color:#4ade80; font-size:18px; text-decoration:none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo-icon">🧬</div>
            <h1>Registro BNJ</h1>
            <p style="color:#94a3b8;">Sistema de Licenciamento Oficial</p>
        </div>
        <div class="plano">
            <p><strong>🪪 Plano:</strong> {{ plano }}</p>
            <p><strong>⏳ Expira em:</strong> {{ data_expiracao[:10] }}</p>
            <p><strong>🔑 Chave de Licença:</strong></p>
            <div class="chave">{{ chave_licenca }}</div>
        </div>
        <div class="download">
            <h3>💻 Baixar Instalador Oficial</h3>
            <a href="/download_instalador" class="btn-download">⬇️ Baixar BNJ_Registro_Setup.exe</a>
        </div>
        <div class="ativacao">
            <h3>📋 Como Ativar a Licença</h3>
            <ol>
                <li>Instale o BNJ Registro no computador do cliente</li>
                <li>Abra o aplicativo</li>
                <li>Digite seu e-mail e a chave de licença acima</li>
                <li>A licença ativa exclusivamente naquela máquina</li>
            </ol>
        </div>
        <a href="/painel" class="voltar">← Voltar ao Painel</a>
    </div>
</body>
</html>
'''

TEMPLATE_ERRO = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Erro — JNB TECNOLOGIA</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; font-family:Arial,sans-serif; }
        body { background:#0f172a; color:white; min-height:100vh; display:flex; align-items:center; justify-content:center; padding:20px; }
        .container { background:#1e293b; padding:30px; border-radius:16px; text-align:center; max-width:400px; }
        h2 { color:#ef4444; margin-bottom:20px; }
        p { margin-bottom:25px; color:#fca5a5; }
        a { color:#4ade80; text-decoration:none; font-weight:bold; }
    </style>
</head>
<body>
    <div class="container">
        <h2>⚠️ Erro</h2>
        <p>{{ mensagem }}</p>
        <a href="/entrar">← Voltar</a>
    </div>
</body>
</html>
'''

# ----------------------
# INICIAR SERVIDOR
# ----------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
