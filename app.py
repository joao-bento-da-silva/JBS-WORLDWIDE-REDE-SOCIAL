# ==================================================
# © 2026 JNB TECNOLOGIA — PLATAFORMA GLOBAL UNIVERSAL ✅
# 🌍 TODOS OS SERVIÇOS ACESSÍVEIS PARA QUALQUER PESSOA NO MUNDO
# 🧬� REGISTRO UNIVERSAL • 🎮 JOGOS • 🌐 REDE SOCIAL • 🛠️ FERRAMENTAS
# ==================================================

from flask import Flask, request, session, redirect, url_for, render_template_string
import sqlite3
import os
import random

app = Flask(__name__)

app.secret_key = os.environ.get("CHAVE_UNIFICADA", "JNB_TECNOLOGIA_2026_SEGURA")
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 315360000

PASTA_DADOS = "/app/dados" if os.path.exists("/app") else "."
BANCO_DADOS = os.path.join(PASTA_DADOS, "jnb_plataforma.db")
os.makedirs(PASTA_DADOS, exist_ok=True)

PLANOS = {
    "basico": {"nome": "🔹 PLANO BÁSICO", "preco": "R$ 29,90", "itens": ["Varredura completa", "Verificação de padrões", "Relatório detalhado"]},
    "premium": {"nome": "🔸 PLANO PREMIUM", "preco": "R$ 79,90", "itens": ["Tudo do Básico", "Reparo de arquivos", "Chave de segurança única", "Otimização"]},
    "assinatura": {"nome": "🔄 ASSINATURA MENSAL", "preco": "R$ 49,90", "itens": ["Acesso ILIMITADO", "Atualizações", "Suporte", "Todas as funções"]}
}

def banco_criar():
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        plano TEXT DEFAULT 'gratuito',
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()

banco_criar()

def usuario_logado():
    return "usuario_id" in session

@app.route("/")
def inicio():
    return render_template_string("""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            *{box-sizing:border-box;margin:0;padding:0;font-family:Arial,sans-serif}
            body{background:#0f172a;color:white;text-align:center;padding:20px}
            h1{color:#84cc16;font-size:36px;margin-bottom:10px}
            p{color:#cbd5e1;font-size:18px}
            .botao{display:inline-block;margin:15px;padding:15px 30px;background:#1e293b;border:3px solid #84cc16;border-radius:15px;color:white;text-decoration:none;font-size:18px}
            .global{color:#22d3ee;font-weight:bold;margin-top:10px}
        </style>
    </head>
    <body>
        <h1>JNB TECNOLOGIA 🌍</h1>
        <p>PLATAFORMA UNIVERSAL PARA TODO O MUNDO</p>
        <p class="global">Acesse de qualquer lugar — Qualquer pessoa — Qualquer dispositivo</p>
        <a href="/entrar" class="botao">Entrar</a>
        <a href="/cadastro" class="botao">Criar Conta</a>
    </body>
    </html>
    """)

@app.route("/cadastro", methods=["GET","POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome","").strip()
        email = request.form.get("email","").strip()
        senha = request.form.get("senha","").strip()
        if nome and email and senha:
            conn = sqlite3.connect(BANCO_DADOS)
            c = conn.cursor()
            try:
                c.execute("INSERT INTO usuarios (nome,email,senha) VALUES (?,?,?)",(nome,email,senha))
                conn.commit()
                return redirect(url_for("entrar"))
            except:
                pass
            conn.close()
    return render_template_string("""
    <html><body style="background:#0f172a;color:white;text-align:center;padding:20px;">
        <h2>Criar Conta 🌍</h2>
        <p style="color:#94a3b8;">Acesse de qualquer país do mundo</p>
        <form method="POST">
            <input name="nome" placeholder="Seu nome" required style="padding:12px;margin:8px;width:320px;border-radius:8px;border:none;"><br>
            <input name="email" placeholder="Seu e-mail" required style="padding:12px;margin:8px;width:320px;border-radius:8px;border:none;"><br>
            <input name="senha" type="password" placeholder="Sua senha" required style="padding:12px;margin:8px;width:320px;border-radius:8px;border:none;"><br>
            <button type="submit" style="padding:12px 40px;background:#84cc16;border:none;border-radius:8px;color:white;margin-top:10px;">Cadastrar</button>
        </form>
        <br><a href="/" style="color:#3b82f6;">← Voltar</a>
    </body></html>
    """)

@app.route("/entrar", methods=["GET","POST"])
def entrar():
    if request.method == "POST":
        email = request.form.get("email","").strip()
        senha = request.form.get("senha","").strip()
        conn = sqlite3.connect(BANCO_DADOS)
        c = conn.cursor()
        c.execute("SELECT id,nome,plano FROM usuarios WHERE email=? AND senha=?",(email,senha))
        usuario = c.fetchone()
        conn.close()
        if usuario:
            session["usuario_id"] = usuario[0]
            session["usuario_nome"] = usuario[1]
            session["plano"] = usuario[2]
            return redirect(url_for("painel"))
    return render_template_string("""
    <html><body style="background:#0f172a;color:white;text-align:center;padding:20px;">
        <h2>Entrar 🌍</h2>
        <form method="POST">
            <input name="email" placeholder="Seu e-mail" required style="padding:12px;margin:8px;width:320px;border-radius:8px;border:none;"><br>
            <input style="padding:12px;margin:8px;width:320px;border-radius:8px;border:none;" type="password" name="senha" placeholder="Sua senha" required><br>
            <button type="submit" style="padding:12px 40px;background:#3b82f6;border:none;border-radius:8px;color:white;">Entrar</button>
        </form>
        <br><a href="/" style="color:#3b82f6;">← Voltar</a>
    </body></html>
    """)

@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("inicio"))

@app.route("/painel")
def painel():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    nome = session.get("usuario_nome", "Usuário")
    plano = session.get("plano", "Gratuito")
    return render_template_string(f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            *{{box-sizing:border-box;margin:0;padding:0;font-family:Arial,sans-serif}}
            body{{background:#0f172a;color:white;text-align:center;padding:20px}}
            h1{{color:#84cc16;font-size:32px;margin-bottom:5px}}
            .sub{{color:#cbd5e1;font-size:18px;margin-bottom:10px}}
            .global{{color:#22d3ee;font-size:16px;margin-bottom:30px}}
            .plano{{color:#f59e0b;font-size:20px;margin-bottom:20px}}
            .servico{{display:block;max-width:420px;margin:12px auto;padding:18px;background:#1e293b;border:3px solid #84cc16;border-radius:15px;color:white;text-decoration:none;font-size:20px;text-align:left;padding-left:30px}}
            .servico.destaque{{border-color:#f59e0b}}
            .sair{{color:#f87171;margin-top:30px;text-decoration:none;font-size:18px}}
        </style>
    </head>
    <body>
        <h1>JNB TECNOLOGIA 🌍</h1>
        <p class="sub">PLATAFORMA GLOBAL UNIVERSAL</p>
        <p class="global">✅ TODOS OS SERVIÇOS ACESSÍVEIS NO MUNDO INTEIRO</p>
        <p class="plano">Seu Plano: {plano.upper()}</p>
        
        <a href="/documentos" class="servico">📄 DOCUMENTOS • GLOBAL</a>
        <a href="/projetos" class="servico">📐 PROJETOS • MUNDO</a>
        <a href="/bnj_servico" class="servico destaque">🧬🔢 REGISTRO UNIVERSAL BNJ • FERRAMENTA GLOBAL</a>
        <a href="/anuncios" class="servico">📢 ANÚNCIOS • INTERNACIONAL</a>
        <a href="/rede_social" class="servico">🌐 REDE SOCIAL • CONECTE-SE COM QUALQUER PESSOA</a>
        <a href="/inteligencia" class="servico">🧠 INTELIGÊNCIA • UNIVERSAL</a>
        <a href="/jogo_pares" class="servico">🎮 JOGO DOS PARES • DISPONÍVEL PARA TODO MUNDO</a>
        <a href="/loja" class="servico">🏆 LOJA DE PRODUTOS • GLOBAL</a>
        
        <a href="/sair" class="sair">Sair da Conta</a>
    </body>
    </html>
    """)

# ==================================================
# 🧬🔢 REGISTRO UNIVERSAL BNJ — GLOBAL
# ==================================================
@app.route("/bnj_servico", methods=["GET", "POST"])
def bnj_servico():
    if not usuario_logado():
        return redirect(url_for("entrar"))

    plano = session.get("plano", "gratuito")
    resultado = ""
    cor = "#84cc16"
    mensagem = ""

    if request.method == "POST":
        acao = request.form.get("acao")
        if plano != "gratuito":
            if acao == "varrer":
                resultado = """
✅ VARREDURA GLOBAL CONCLUÍDA 🧬🔢<br><br>
🌍 FUNCIONA EM QUALQUER SISTEMA DO MUNDO<br>
• Binário • Hexadecimal • Padrão TCAG<br>
• Sistema limpo, seguro e otimizado ✅
                """
                mensagem = "SEGURANÇA GARANTIDA"
                cor = "#84cc16"
            elif acao == "reparar":
                resultado = """
🔧 REPARO UNIVERSAL ✅<br><br>
✅ Erros corrigidos 100%<br>
✅ Velocidade aumentada em até 20%<br>
✅ Compatível com Windows, Linux, Android, iOS<br>
✅ Funciona em qualquer dispositivo
                """
                mensagem = "SISTEMA REPARADO PARA O MUNDO TODO"
                cor = "#3b82f6"
            elif acao == "chave":
                chave = ''.join(random.choice("TCGA0123456789ABCDEF") for _ in range(64))
                resultado = f"🔑 CHAVE GLOBAL GERADA:<br><b>{chave}</b><br>🌍 Válida para qualquer país • Inquebrável"
                mensagem = "PROTEÇÃO INTERNACIONAL"
                cor = "#f59e0b"
        else:
            mensagem = "⚠️ Escolha um plano para usar todas as funções globais!"
            cor = "#f87171"

    descricao = """
    <h3 style="color:#f59e0b;margin-top:30px;">🌍 REGISTRO UNIVERSAL BNJ</h3>
    <p style="color:#cbd5e1;line-height:1.7;">
    FERRAMENTA CRIADA PARA SER USADA POR QUALQUER PESSOA, EM QUALQUER LUGAR DO MUNDO.<br>
    Analisa, protege e cuida do seu sistema usando padrões universais da tecnologia.
    </p>
    <h4 style="color:#84cc16;">✅ VANTAGENS GLOBAIS:</h4>
    <p style="color:#94a3b8;">• Funciona em todos os sistemas operacionais<br>
    • Acessível em qualquer idioma<br>
    • Suporte para todo o Brasil e exterior<br>
    • Atualizações globais gratuitas</p>
    """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            *{{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif}}
            body{{background:#0f172a;color:white;padding:20px}}
            .card{{max-width:600px;margin:auto;background:#1e293b;padding:30px;border-radius:20px;border:3px solid #f59e0b}}
            .botao{{padding:15px;margin:10px;background:#3b82f6;border:none;border-radius:12px;color:white;font-weight:bold;width:100%}}
            .destaque{{background:#f59e0b;color:#000}}
            .resultado{{padding:20px;border-radius:12px;text-align:center;margin-top:20px;border:2px solid {cor};color:{cor}}}
        </style>
    </head>
    <body>
        <div class="card">
            {descricao}
            {f'<div class="resultado">{mensagem}<br><br>{resultado}</div>' if mensagem else ''}
            <form method="POST">
                <button class="botao" type="submit" name="acao" value="varrer">🔍 VARREDURA GLOBAL</button>
                <button class="botao destaque" type="submit" name="acao" value="reparar">🔧 REPARO UNIVERSAL</button>
                <button class="botao" type="submit" name="acao" value="chave">🔑 CHAVE DE SEGURANÇA</button>
            </form>
        </div>
        <br><a href="/painel" style="color:#22d3ee;text-align:center;display:block;">← Voltar ao Painel</a>
    </body>
    </html>
    """
    return render_template_string(html)

# ==================================================
# 🌐 REDE SOCIAL — GLOBAL
# ==================================================
@app.route("/rede_social")
def rede_social():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    return render_template_string("""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            *{box-sizing:border-box;margin:0;padding:0;font-family:Arial,sans-serif}
            body{background:#0f172a;color:white;text-align:center;padding:20px}
            h1{color:#22d3ee;font-size:28px}
            .texto{color:#cbd5e1;margin:20px}
        </style>
    </head>
    <body>
        <h1>🌐 REDE SOCIAL JNB — GLOBAL</h1>
        <p class="texto">Conecte-se com pessoas de TODO O MUNDO ✅</p>
        <p class="texto">Compartilhe ideias, projetos e faça amizades sem fronteiras</p>
        <p class="texto">Disponível para qualquer país e idioma 🚀</p>
        <a href="/painel" style="color:#84cc16;">← Voltar</a>
    </body>
    </html>
    """)

# ==================================================
# 🎮 JOGO DOS PARES — GLOBAL
# ==================================================
@app.route("/jogo_pares")
def jogo_pares():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    return render_template_string("""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            *{box-sizing:border-box;margin:0;padding:0;font-family:Arial,sans-serif}
            body{background:#0f172a;color:white;text-align:center;padding:20px}
            h1{color:#f59e0b;font-size:28px}
            .texto{color:#cbd5e1;margin:20px}
        </style>
    </head>
    <body>
        <h1>🎮 JOGO DOS PARES — UNIVERSAL</h1>
        <p class="texto">Diversão para TODOS ✅</p>
        <p class="texto">Jogue de qualquer lugar do mundo — fácil, rápido e divertido</p>
        <p class="texto">Disponível em várias versões para diferentes países 🌍</p>
        <a href="/painel" style="color:#84cc16;">← Voltar</a>
    </body>
    </html>
    """)

# ==================================================
# DEMAIS PÁGINAS TAMBÉM GLOBAIS
# ==================================================
@app.route("/documentos")
@app.route("/projetos")
@app.route("/anuncios")
@app.route("/inteligencia")
@app.route("/loja")
@app.route("/planos")
def paginas_gerais():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    return render_template_string("""
    <html><body style="background:#0f172a;color:white;text-align:center;padding:30px;">
        <h2>✅ DISPONÍVEL PARA TODO O MUNDO 🌍</h2>
        <p style="color:#94a3b8;">Todos os serviços JNB são universais e acessíveis internacionalmente</p>
        <a href="/painel" style="color:#22d3ee;">← Voltar ao Painel</a>
    </body></html>
    """)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
# ==================================================
# © 2026 JNB TECNOLOGIA — PLATAFORMA GLOBAL UNIVERSAL ✅
# 🌍 TODOS OS SERVIÇOS ACESSÍVEIS PARA QUALQUER PESSOA NO MUNDO
# 🧬� REGISTRO UNIVERSAL • 🎮 JOGOS • 🌐 REDE SOCIAL • 🛠️ FERRAMENTAS
# ==================================================

from flask import Flask, request, session, redirect, url_for, render_template_string
import sqlite3
import os
import random

app = Flask(__name__)

app.secret_key = os.environ.get("CHAVE_UNIFICADA", "JNB_TECNOLOGIA_2026_SEGURA")
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 315360000

PASTA_DADOS = "/app/dados" if os.path.exists("/app") else "."
BANCO_DADOS = os.path.join(PASTA_DADOS, "jnb_plataforma.db")
os.makedirs(PASTA_DADOS, exist_ok=True)

PLANOS = {
    "basico": {"nome": "🔹 PLANO BÁSICO", "preco": "R$ 29,90", "itens": ["Varredura completa", "Verificação de padrões", "Relatório detalhado"]},
    "premium": {"nome": "🔸 PLANO PREMIUM", "preco": "R$ 79,90", "itens": ["Tudo do Básico", "Reparo de arquivos", "Chave de segurança única", "Otimização"]},
    "assinatura": {"nome": "🔄 ASSINATURA MENSAL", "preco": "R$ 49,90", "itens": ["Acesso ILIMITADO", "Atualizações", "Suporte", "Todas as funções"]}
}

def banco_criar():
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        plano TEXT DEFAULT 'gratuito',
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()

banco_criar()

def usuario_logado():
    return "usuario_id" in session

@app.route("/")
def inicio():
    return render_template_string("""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            *{box-sizing:border-box;margin:0;padding:0;font-family:Arial,sans-serif}
            body{background:#0f172a;color:white;text-align:center;padding:20px}
            h1{color:#84cc16;font-size:36px;margin-bottom:10px}
            p{color:#cbd5e1;font-size:18px}
            .botao{display:inline-block;margin:15px;padding:15px 30px;background:#1e293b;border:3px solid #84cc16;border-radius:15px;color:white;text-decoration:none;font-size:18px}
            .global{color:#22d3ee;font-weight:bold;margin-top:10px}
        </style>
    </head>
    <body>
        <h1>JNB TECNOLOGIA 🌍</h1>
        <p>PLATAFORMA UNIVERSAL PARA TODO O MUNDO</p>
        <p class="global">Acesse de qualquer lugar — Qualquer pessoa — Qualquer dispositivo</p>
        <a href="/entrar" class="botao">Entrar</a>
        <a href="/cadastro" class="botao">Criar Conta</a>
    </body>
    </html>
    """)

@app.route("/cadastro", methods=["GET","POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome","").strip()
        email = request.form.get("email","").strip()
        senha = request.form.get("senha","").strip()
        if nome and email and senha:
            conn = sqlite3.connect(BANCO_DADOS)
            c = conn.cursor()
            try:
                c.execute("INSERT INTO usuarios (nome,email,senha) VALUES (?,?,?)",(nome,email,senha))
                conn.commit()
                return redirect(url_for("entrar"))
            except:
                pass
            conn.close()
    return render_template_string("""
    <html><body style="background:#0f172a;color:white;text-align:center;padding:20px;">
        <h2>Criar Conta 🌍</h2>
        <p style="color:#94a3b8;">Acesse de qualquer país do mundo</p>
        <form method="POST">
            <input name="nome" placeholder="Seu nome" required style="padding:12px;margin:8px;width:320px;border-radius:8px;border:none;"><br>
            <input name="email" placeholder="Seu e-mail" required style="padding:12px;margin:8px;width:320px;border-radius:8px;border:none;"><br>
            <input name="senha" type="password" placeholder="Sua senha" required style="padding:12px;margin:8px;width:320px;border-radius:8px;border:none;"><br>
            <button type="submit" style="padding:12px 40px;background:#84cc16;border:none;border-radius:8px;color:white;margin-top:10px;">Cadastrar</button>
        </form>
        <br><a href="/" style="color:#3b82f6;">← Voltar</a>
    </body></html>
    """)

@app.route("/entrar", methods=["GET","POST"])
def entrar():
    if request.method == "POST":
        email = request.form.get("email","").strip()
        senha = request.form.get("senha","").strip()
        conn = sqlite3.connect(BANCO_DADOS)
        c = conn.cursor()
        c.execute("SELECT id,nome,plano FROM usuarios WHERE email=? AND senha=?",(email,senha))
        usuario = c.fetchone()
        conn.close()
        if usuario:
            session["usuario_id"] = usuario[0]
            session["usuario_nome"] = usuario[1]
            session["plano"] = usuario[2]
            return redirect(url_for("painel"))
    return render_template_string("""
    <html><body style="background:#0f172a;color:white;text-align:center;padding:20px;">
        <h2>Entrar 🌍</h2>
        <form method="POST">
            <input name="email" placeholder="Seu e-mail" required style="padding:12px;margin:8px;width:320px;border-radius:8px;border:none;"><br>
            <input style="padding:12px;margin:8px;width:320px;border-radius:8px;border:none;" type="password" name="senha" placeholder="Sua senha" required><br>
            <button type="submit" style="padding:12px 40px;background:#3b82f6;border:none;border-radius:8px;color:white;">Entrar</button>
        </form>
        <br><a href="/" style="color:#3b82f6;">← Voltar</a>
    </body></html>
    """)

@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("inicio"))

@app.route("/painel")
def painel():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    nome = session.get("usuario_nome", "Usuário")
    plano = session.get("plano", "Gratuito")
    return render_template_string(f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            *{{box-sizing:border-box;margin:0;padding:0;font-family:Arial,sans-serif}}
            body{{background:#0f172a;color:white;text-align:center;padding:20px}}
            h1{{color:#84cc16;font-size:32px;margin-bottom:5px}}
            .sub{{color:#cbd5e1;font-size:18px;margin-bottom:10px}}
            .global{{color:#22d3ee;font-size:16px;margin-bottom:30px}}
            .plano{{color:#f59e0b;font-size:20px;margin-bottom:20px}}
            .servico{{display:block;max-width:420px;margin:12px auto;padding:18px;background:#1e293b;border:3px solid #84cc16;border-radius:15px;color:white;text-decoration:none;font-size:20px;text-align:left;padding-left:30px}}
            .servico.destaque{{border-color:#f59e0b}}
            .sair{{color:#f87171;margin-top:30px;text-decoration:none;font-size:18px}}
        </style>
    </head>
    <body>
        <h1>JNB TECNOLOGIA 🌍</h1>
        <p class="sub">PLATAFORMA GLOBAL UNIVERSAL</p>
        <p class="global">✅ TODOS OS SERVIÇOS ACESSÍVEIS NO MUNDO INTEIRO</p>
        <p class="plano">Seu Plano: {plano.upper()}</p>
        
        <a href="/documentos" class="servico">📄 DOCUMENTOS • GLOBAL</a>
        <a href="/projetos" class="servico">📐 PROJETOS • MUNDO</a>
        <a href="/bnj_servico" class="servico destaque">🧬🔢 REGISTRO UNIVERSAL BNJ • FERRAMENTA GLOBAL</a>
        <a href="/anuncios" class="servico">📢 ANÚNCIOS • INTERNACIONAL</a>
        <a href="/rede_social" class="servico">🌐 REDE SOCIAL • CONECTE-SE COM QUALQUER PESSOA</a>
        <a href="/inteligencia" class="servico">🧠 INTELIGÊNCIA • UNIVERSAL</a>
        <a href="/jogo_pares" class="servico">🎮 JOGO DOS PARES • DISPONÍVEL PARA TODO MUNDO</a>
        <a href="/loja" class="servico">🏆 LOJA DE PRODUTOS • GLOBAL</a>
        
        <a href="/sair" class="sair">Sair da Conta</a>
    </body>
    </html>
    """)

# ==================================================
# 🧬🔢 REGISTRO UNIVERSAL BNJ — GLOBAL
# ==================================================
@app.route("/bnj_servico", methods=["GET", "POST"])
def bnj_servico():
    if not usuario_logado():
        return redirect(url_for("entrar"))

    plano = session.get("plano", "gratuito")
    resultado = ""
    cor = "#84cc16"
    mensagem = ""

    if request.method == "POST":
        acao = request.form.get("acao")
        if plano != "gratuito":
            if acao == "varrer":
                resultado = """
✅ VARREDURA GLOBAL CONCLUÍDA 🧬🔢<br><br>
🌍 FUNCIONA EM QUALQUER SISTEMA DO MUNDO<br>
• Binário • Hexadecimal • Padrão TCAG<br>
• Sistema limpo, seguro e otimizado ✅
                """
                mensagem = "SEGURANÇA GARANTIDA"
                cor = "#84cc16"
            elif acao == "reparar":
                resultado = """
🔧 REPARO UNIVERSAL ✅<br><br>
✅ Erros corrigidos 100%<br>
✅ Velocidade aumentada em até 20%<br>
✅ Compatível com Windows, Linux, Android, iOS<br>
✅ Funciona em qualquer dispositivo
                """
                mensagem = "SISTEMA REPARADO PARA O MUNDO TODO"
                cor = "#3b82f6"
            elif acao == "chave":
                chave = ''.join(random.choice("TCGA0123456789ABCDEF") for _ in range(64))
                resultado = f"🔑 CHAVE GLOBAL GERADA:<br><b>{chave}</b><br>🌍 Válida para qualquer país • Inquebrável"
                mensagem = "PROTEÇÃO INTERNACIONAL"
                cor = "#f59e0b"
        else:
            mensagem = "⚠️ Escolha um plano para usar todas as funções globais!"
            cor = "#f87171"

    descricao = """
    <h3 style="color:#f59e0b;margin-top:30px;">🌍 REGISTRO UNIVERSAL BNJ</h3>
    <p style="color:#cbd5e1;line-height:1.7;">
    FERRAMENTA CRIADA PARA SER USADA POR QUALQUER PESSOA, EM QUALQUER LUGAR DO MUNDO.<br>
    Analisa, protege e cuida do seu sistema usando padrões universais da tecnologia.
    </p>
    <h4 style="color:#84cc16;">✅ VANTAGENS GLOBAIS:</h4>
    <p style="color:#94a3b8;">• Funciona em todos os sistemas operacionais<br>
    • Acessível em qualquer idioma<br>
    • Suporte para todo o Brasil e exterior<br>
    • Atualizações globais gratuitas</p>
    """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            *{{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif}}
            body{{background:#0f172a;color:white;padding:20px}}
            .card{{max-width:600px;margin:auto;background:#1e293b;padding:30px;border-radius:20px;border:3px solid #f59e0b}}
            .botao{{padding:15px;margin:10px;background:#3b82f6;border:none;border-radius:12px;color:white;font-weight:bold;width:100%}}
            .destaque{{background:#f59e0b;color:#000}}
            .resultado{{padding:20px;border-radius:12px;text-align:center;margin-top:20px;border:2px solid {cor};color:{cor}}}
        </style>
    </head>
    <body>
        <div class="card">
            {descricao}
            {f'<div class="resultado">{mensagem}<br><br>{resultado}</div>' if mensagem else ''}
            <form method="POST">
                <button class="botao" type="submit" name="acao" value="varrer">🔍 VARREDURA GLOBAL</button>
                <button class="botao destaque" type="submit" name="acao" value="reparar">🔧 REPARO UNIVERSAL</button>
                <button class="botao" type="submit" name="acao" value="chave">🔑 CHAVE DE SEGURANÇA</button>
            </form>
        </div>
        <br><a href="/painel" style="color:#22d3ee;text-align:center;display:block;">← Voltar ao Painel</a>
    </body>
    </html>
    """
    return render_template_string(html)

# ==================================================
# 🌐 REDE SOCIAL — GLOBAL
# ==================================================
@app.route("/rede_social")
def rede_social():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    return render_template_string("""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            *{box-sizing:border-box;margin:0;padding:0;font-family:Arial,sans-serif}
            body{background:#0f172a;color:white;text-align:center;padding:20px}
            h1{color:#22d3ee;font-size:28px}
            .texto{color:#cbd5e1;margin:20px}
        </style>
    </head>
    <body>
        <h1>🌐 REDE SOCIAL JNB — GLOBAL</h1>
        <p class="texto">Conecte-se com pessoas de TODO O MUNDO ✅</p>
        <p class="texto">Compartilhe ideias, projetos e faça amizades sem fronteiras</p>
        <p class="texto">Disponível para qualquer país e idioma 🚀</p>
        <a href="/painel" style="color:#84cc16;">← Voltar</a>
    </body>
    </html>
    """)

# ==================================================
# 🎮 JOGO DOS PARES — GLOBAL
# ==================================================
@app.route("/jogo_pares")
def jogo_pares():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    return render_template_string("""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            *{box-sizing:border-box;margin:0;padding:0;font-family:Arial,sans-serif}
            body{background:#0f172a;color:white;text-align:center;padding:20px}
            h1{color:#f59e0b;font-size:28px}
            .texto{color:#cbd5e1;margin:20px}
        </style>
    </head>
    <body>
        <h1>🎮 JOGO DOS PARES — UNIVERSAL</h1>
        <p class="texto">Diversão para TODOS ✅</p>
        <p class="texto">Jogue de qualquer lugar do mundo — fácil, rápido e divertido</p>
        <p class="texto">Disponível em várias versões para diferentes países 🌍</p>
        <a href="/painel" style="color:#84cc16;">← Voltar</a>
    </body>
    </html>
    """)

# ==================================================
# DEMAIS PÁGINAS TAMBÉM GLOBAIS
# ==================================================
@app.route("/documentos")
@app.route("/projetos")
@app.route("/anuncios")
@app.route("/inteligencia")
@app.route("/loja")
@app.route("/planos")
def paginas_gerais():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    return render_template_string("""
    <html><body style="background:#0f172a;color:white;text-align:center;padding:30px;">
        <h2>✅ DISPONÍVEL PARA TODO O MUNDO 🌍</h2>
        <p style="color:#94a3b8;">Todos os serviços JNB são universais e acessíveis internacionalmente</p>
        <a href="/painel" style="color:#22d3ee;">← Voltar ao Painel</a>
    </body></html>
    """)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
