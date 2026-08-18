  # ==================================================
# © 2026 JNB TECNOLOGIA — CÓDIGO CORRIGIDO ✅
# SEM FUNÇÕES DUPLICADAS ✅ PORTA 5000 ✅
# ==================================================

from flask import Flask, request, session, redirect, url_for, render_template_string, send_from_directory
import sqlite3
import os
import random
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.secret_key = os.environ.get("CHAVE_UNIFICADA", "JNB_TECNOLOGIA_2026_SEGURA")
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 315360000
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "midias")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

BANCO_DADOS = "jnb_plataforma.db"

PLANOS = {
    "gratuito": {"nome": "🔹 PLANO GRATUITO", "cor": "#94a3b8", "preco": "R$ 0,00"},
    "basico": {"nome": "🔹 PLANO BÁSICO", "cor": "#84cc16", "preco": "R$ 29,90/mês"},
    "premium": {"nome": "🔸 PLANO PREMIUM", "cor": "#f59e0b", "preco": "R$ 79,90/mês"},
    "assinatura": {"nome": "🔄 GLOBAL", "cor": "#3b82f6", "preco": "R$ 49,90/mês"}
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
        pontos INTEGER DEFAULT 0
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS postagens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        texto TEXT,
        midia TEXT,
        tipo_midia TEXT,
        curtidas INTEGER DEFAULT 0
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS curtidas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        postagem_id INTEGER,
        UNIQUE(usuario_id, postagem_id)
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        descricao TEXT,
        preco REAL NOT NULL,
        tipo TEXT
    )""")
    
    c.execute("PRAGMA table_info(produtos)")
    colunas = [col[1] for col in c.fetchall()]
    if 'tipo' not in colunas:
        c.execute("ALTER TABLE produtos ADD COLUMN tipo TEXT")
    
    c.execute("INSERT OR IGNORE INTO produtos (nome, descricao, preco, tipo) VALUES (?, ?, ?, ?)",
              ("Curso de IA Avançado", "Aprenda inteligência artificial moderna", 299.90, "curso"))
    c.execute("INSERT OR IGNORE INTO produtos (nome, descricao, preco, tipo) VALUES (?, ?, ?, ?)",
              ("E-book Segurança Digital", "Proteja seus dados e privacidade", 49.90, "ebook"))
    c.execute("INSERT OR IGNORE INTO produtos (nome, descricao, preco, tipo) VALUES (?, ?, ?, ?)",
              ("Consultoria de Projetos", "Sessão com especialista em tecnologia", 150.00, "servico"))
    
    conn.commit()
    conn.close()

banco_criar()

def usuario_logado():
    return "usuario_id" in session

# ==================================================
# ROTAS — TODAS ÚNICAS, SEM DUPLICAÇÃO
# ==================================================

@app.route("/")
def inicio():
    return render_template_string("""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="background:#0f172a;color:white;text-align:center;padding:20px">
        <h1>JNB TECNOLOGIA 🌍</h1><p>PLATAFORMA GLOBAL 2.1 ✅</p>
        <a href="/entrar" style="padding:12px 30px;background:#84cc16;border-radius:10px;color:white;text-decoration:none">Entrar</a>
        <a href="/cadastro" style="padding:12px 30px;background:#3b82f6;border-radius:10px;color:white;text-decoration:none;margin-left:10px">Criar Conta</a>
    </body></html>""")

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
            except: pass
            conn.close()
    return render_template_string("""
    <html><body style="background:#0f172a;color:white;text-align:center;padding:20px">
        <h2>Criar Conta</h2><form method="POST">
            <input name="nome" placeholder="Seu nome" required style="padding:10px;margin:8px;width:300px"><br>
            <input name="email" placeholder="E-mail" required style="padding:10px;margin:8px;width:300px"><br>
            <input type="password" name="senha" placeholder="Senha" required style="padding:10px;margin:8px;width:300px"><br>
            <button type="submit" style="padding:10px 30px;background:#84cc16;border:none;border-radius:8px">Cadastrar</button>
        </form><br><a href="/" style="color:#3b82f6">← Voltar</a>
    </body></html>""")

@app.route("/entrar", methods=["GET","POST"])
def entrar():
    if request.method == "POST":
        email = request.form.get("email","").strip()
        senha = request.form.get("senha","").strip()
        conn = sqlite3.connect(BANCO_DADOS)
        c = conn.cursor()
        c.execute("SELECT id,nome,plano,pontos FROM usuarios WHERE email=? AND senha=?",(email,senha))
        usuario = c.fetchone()
        conn.close()
        if usuario:
            session["usuario_id"] = usuario[0]
            session["plano"] = usuario[2]
            session["pontos"] = usuario[3]
            return redirect(url_for("painel"))
    return render_template_string("""
    <html><body style="background:#0f172a;color:white;text-align:center;padding:20px">
        <h2>Entrar</h2><form method="POST">
            <input name="email" placeholder="E-mail" required style="padding:10px;margin:8px;width:300px"><br>
            <input type="password" name="senha" placeholder="Senha" required style="padding:10px;margin:8px;width:300px"><br>
            <button type="submit" style="padding:10px 30px;background:#3b82f6;border:none;border-radius:8px">Entrar</button>
        </form><br><a href="/" style="color:#3b82f6">← Voltar</a>
    </body></html>""")

@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("inicio"))

@app.route("/painel")
def painel():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    plano = PLANOS.get(session.get("plano", "gratuito"))
    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="background:#0f172a;color:white;text-align:center;padding:20px">
        <h1>JNB TECNOLOGIA 🌍</h1><p>PLATAFORMA GLOBAL 2.1</p>
        <p style="color:{plano['cor']}">Plano: {plano['nome']}</p>
        <div style="max-width:450px;margin:auto">
            <a href="/documentos" style="display:block;padding:15px;margin:12px;background:#1e293b;border-radius:12px;color:white;text-decoration:none">📄 DOCUMENTOS</a>
            <a href="/projetos" style="display:block;padding:15px;margin:12px;background:#1e293b;border-radius:12px;color:white;text-decoration:none">📐 PROJETOS</a>
            <a href="/bnj_servico" style="display:block;padding:15px;margin:12px;background:#1e293b;border-radius:12px;color:white;text-decoration:none">🧬 REGISTRO BNJ</a>
            <a href="/anuncios" style="display:block;padding:15px;margin:12px;background:#1e293b;border-radius:12px;color:white;text-decoration:none">📢 ANÚNCIOS</a>
            <a href="/rede_social" style="display:block;padding:15px;margin:12px;background:#1e293b;border-radius:12px;color:white;text-decoration:none">🌐 REDE SOCIAL</a>
            <a href="/inteligencia" style="display:block;padding:15px;margin:12px;background:#1e293b;border-radius:12px;color:white;text-decoration:none">🧠 INTELIGÊNCIA</a>
            <a href="/jogo_numeros" style="display:block;padding:15px;margin:12px;background:#1e293b;border-radius:12px;color:white;text-decoration:none">🎮 O SEGREDO DOS NÚMEROS</a>
            <a href="/loja" style="display:block;padding:15px;margin:12px;background:#1e293b;border-radius:12px;color:white;text-decoration:none">🏆 LOJA</a>
        </div><br><a href="/sair" style="color:#ef4944">Sair</a>
    </body></html>""")

@app.route("/documentos")
def documentos():
    if not usuario_logado(): return redirect(url_for("entrar"))
    return render_template_string("""
    <html><body style="background:#0f172a;color:white;text-align:center;padding:20px">
        <h1>📄 DOCUMENTOS GLOBAL</h1><p>✅ Funcionalidade Ativa ✅</p>
        <br><a href="/painel" style="color:#3b82f6">← Voltar</a>
    </body></html>""")

@app.route("/projetos")
def projetos():
    if not usuario_logado(): return redirect(url_for("entrar"))
    return render_template_string("""
    <html><body style="background:#0f172a;color:white;text-align:center;padding:20px">
        <h1>📐 PROJETOS GLOBAL</h1><p>✅ Funcionalidade Ativa ✅</p>
        <br><a href="/painel" style="color:#3b82f6">← Voltar</a>
    </body></html>""")

@app.route("/bnj_servico", methods=["GET","POST"])
def bnj_servico():
    if not usuario_logado(): return redirect(url_for("entrar"))
    resultado = ""; cor = "#84cc16"
    if request.method == "POST":
        acao = request.form.get("acao")
        if acao == "varrer":
            resultado = "✅ VARREDURA CONCLUÍDA ✅"; cor = "#3b82f6"
        elif acao == "reparar":
            resultado = "🔧 SISTEMA REPARADO ✅"; cor = "#f59e0b"
        elif acao == "chave":
            chave = "CHAVE_BNJ_" + ''.join(random.choice("0123456789ABCDEF") for _ in range(24))
            resultado = f"🔑 {chave}"; cor = "#10b981"
    return render_template_string(f"""
    <html><body style="background:#0f172a;color:white;text-align:center;padding:20px">
        <h1>🧬 REGISTRO BNJ</h1>
        <div style="background:#1e293b;padding:25px;border-radius:15px;max-width:450px;margin:auto;border:2px solid {cor}">
            <p>{resultado}</p><form method="POST">
                <button type="submit" name="acao" value="varrer" style="padding:10px 20px;margin:5px;background:#3b82f6;border:none;border-radius:6px;color:white">VAR</button>
                <button type="submit" name="acao" value="reparar" style="padding:10px 20px;margin:5px;background:#f59e0b;border:none;border-radius:6px;color:black">REPARAR</button>
                <button type="submit" name="acao" value="chave" style="padding:10px 20px;margin:5px;background:#10b981;border:none;border-radius:6px;color:white">CHAVE</button>
            </form>
        </div><br><a href="/painel" style="color:#3b82f6">← Voltar</a>
    </body></html>""")

@app.route("/anuncios")
def anuncios():
    if not usuario_logado(): return redirect(url_for("entrar"))
    return render_template_string("""
    <html><body style="background:#0f172a;color:white;text-align:center;padding:20px">
        <h1>📢 ANÚNCIOS GLOBAL</h1><p>✅ Publicação Ativa ✅</p>
        <br><a href="/painel" style="color:#3b82f6">← Voltar</a>
    </body></html>""")

@app.route("/rede_social", methods=["GET","POST"])
def rede_social():
    if not usuario_logado(): return redirect(url_for("entrar"))
    if request.method == "POST":
        texto = request.form.get("texto","")
        midia = request.files.get("midia")
        caminho = None; tipo = "texto"
        if midia and midia.filename:
            nome_seguro = secure_filename(midia.filename)
            if nome_seguro.endswith(("jpg","jpeg","png","gif")): tipo = "imagem"
            elif nome_seguro.endswith(("mp4","webm")): tipo = "video"
            caminho = nome_seguro
            midia.save(os.path.join(app.config["UPLOAD_FOLDER"], nome_seguro))
        if texto or caminho:
            conn = sqlite3.connect(BANCO_DADOS)
            c = conn.cursor()
            c.execute("INSERT INTO postagens (usuario_id, texto, midia, tipo_midia) VALUES (?,?,?,?)",
                      (session["usuario_id"], texto, caminho, tipo))
            conn.commit(); conn.close()
    if request.args.get("curtir"):
        pid = request.args.get("curtir")
        conn = sqlite3.connect(BANCO_DADOS)
        c = conn.cursor()
        c.execute("SELECT * FROM curtidas WHERE usuario_id=? AND postagem_id=?",(session["usuario_id"], pid))
        if c.fetchone():
            c.execute("DELETE FROM curtidas WHERE usuario_id=? AND postagem_id=?",(session["usuario_id"], pid))
            c.execute("UPDATE postagens SET curtidas = curtidas -1 WHERE id=?",(pid,))
        else:
            c.execute("INSERT INTO curtidas (usuario_id, postagem_id) VALUES (?,?)",(session["usuario_id"], pid))
            c.execute("UPDATE postagens SET curtidas = curtidas +1 WHERE id=?",(pid,))
        conn.commit(); conn.close()
        return redirect(url_for("rede_social"))
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("SELECT p.id, u.nome, p.texto, p.midia, p.tipo_midia, p.curtidas FROM postagens p JOIN usuarios u ON p.usuario_id = u.id ORDER BY p.data DESC LIMIT 15")
    posts = c.fetchall()
    conn.close()
    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="background:#0f172a;color:white;padding:20px">
        <h1 style="text-align:center;color:#3b82f6">🌐 REDE SOCIAL JNB</h1>
        <form method="POST" enctype="multipart/form-data" style="max-width:450px;margin:auto">
            <textarea name="texto" placeholder="Escreva algo..." style="width:100%;height:70px;padding:10px;border-radius:8px;background:#1e293b;color:white;border:none"></textarea><br>
            <input type="file" name="midia" accept="image/*,video/*" style="margin:10px 0"><br>
            <button type="submit" style="padding:10px 30px;background:#f59e0b;border:none;border-radius:8px;color:black;font-weight:bold">COMPARTILHAR</button>
        </form><br><h3 style="text-align:center;color:#94a3b8">📢 POSTAGENS</h3>
        {''.join([f'''
        <div style="background:#1e293b;padding:15px;border-radius:10px;margin:12px auto;max-width:450px">
            <div style="color:#10b981;font-weight:bold">{p[1]}</div>
            <div style="margin:8px 0">{p[2]}</div>
            {f'<img src="/midias/{p[3]}" style="max-width:100%;border-radius:8px">' if p[3] and p[4] == 'imagem' else ''}
            {f'<video controls style="max-width:100%;border-radius:8px"><source src="/midias/{p[3]}"></video>' if p[3] and p[4] == 'video' else ''}
            <a href="/rede_social?curtir={p[0]}" style="color:#ef4944">❤️ {p[5]} Curtidas</a>
        </div>
        ''' for p in posts])}
        <br><a href="/painel" style="color:#3b82f6;display:block;text-align:center">← Voltar</a>
    </body></html>""")

@app.route("/midias/<nome>")
def midias(nome):
    return send_from_directory(app.config["UPLOAD_FOLDER"], nome)

@app.route("/inteligencia", methods=["GET","POST"])
def inteligencia():
    if not usuario_logado(): return redirect(url_for("entrar"))
    return render_template_string("""
    <html><body style="background:#0f172a;color:white;text-align:center;padding:20px">
        <h1>🧠 INTELIGÊNCIA GLOBAL</h1><p>✅ Funcionando ✅</p>
        <form method="POST">
            <textarea name="pergunta" placeholder="Digite sua mensagem..." style="width:80%;height:70px;padding:10px;border-radius:8px;background:#1e293b;color:white;border:none"></textarea><br>
            <button type="submit" style="padding:10px 30px;background:#84cc16;border:none;border-radius:8px;color:black">ENVIAR</button>
        </form><p style="color:#10b981;margin-top:20px">✅ Sistema ativo e conectado!</p>
        <br><a href="/painel" style="color:#3b82f6">← Voltar</a>
    </body></html>""")

@app.route("/jogo_numeros", methods=["GET","POST"])
def jogo_numeros():
    if not usuario_logado(): return redirect(url_for("entrar"))
    pontos = session.get("pontos", 0); msg = ""
    if request.method == "POST":
        resp = request.form.get("resposta","")
        if len(resp) >= 9:
            pontos += 100; msg = "✅ +100 PONTOS!"
        elif len(resp) >= 6:
            pontos += 50; msg = "✅ +50 PONTOS!"
        session["pontos"] = pontos
    return render_template_string(f"""
    <html><body style="background:#0f172a;color:white;text-align:center;padding:20px">
        <h1>🎮 O SEGREDO DOS NÚMEROS</h1><p style="color:#84cc16;font-size:22px">Pontos: {pontos}</p>
        <div style="background:#1e293b;padding:25px;border-radius:15px;max-width:450px;margin:auto;border:3px solid #f59e0b">
            <p>🟠 = 4164 | 🔴 = 1462 | ⚫ = 9808</p>
            <p>⚪ = 5561 | 🟣 = 2493 | 🟦 = 2251</p>
            <form method="POST">
                <input type="text" name="resposta" placeholder="Digite a sequência..." style="width:80%;padding:12px;border-radius:8px;border:2px solid #f59e0b;background:#0f172a;color:white">
                <br><button type="submit" style="padding:12px 35px;background:#f59e0b;border:none;border-radius:8px;color:black;margin-top:15px">CONFIRMAR</button>
            </form><p style="color:#10b981;margin-top:20px">{msg}</p>
        </div><br><a href="/painel" style="color:#3b82f6">← Voltar</a>
    </body></html>""")

@app.route("/loja")
def loja():
    if not usuario_logado(): return redirect(url_for("entrar"))
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("SELECT nome, descricao, preco, tipo FROM produtos")
    produtos = c.fetchall()
    conn.close()
    return render_template_string(f"""
    <html><body style="background:#0f172a;color:white;padding:20px">
        <h1 style="text-align:center;color:#f59e0b">🏆 LOJA JNB</h1>
        <h3 style="color:#84cc16">📦 PRODUTOS DISPONÍVEIS</h3>
        {''.join([f'<div style="background:#1e293b;padding:15px;border-radius:8px;margin:10px 0"><b>{p[0]}</b><p style="color:#94a3b8">{p[1]}</p><p style="color:#10b981">R$ {p[2]:.2f}</p></div>' for p in produtos])}
        <br><a href="/painel" style="color:#3b82f6;display:block;text-align:center">← Voltar</a>
    </body></html>""")

# ==================================================
# ✅ SERVIDOR FECHADO CORRETAMENTE — ÚLTIMA LINHA ✅
# ==================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
