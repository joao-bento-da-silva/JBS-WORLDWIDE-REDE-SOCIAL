 # ==================================================
# © 2026 JNB TECNOLOGIA — CÓDIGO FINAL
# CABEÇALHO NO TOPO ✅ | ORDEM CORRETA ✅
# ==================================================

from flask import Flask, request, session, redirect, url_for, render_template_string
import sqlite3
import os

app = Flask(__name__)

app.secret_key = os.environ.get("CHAVE_UNIFICADA", "JNB_TECNOLOGIA_2026_SEGURA")
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 315360000

PASTA_DADOS = "/app/dados" if os.path.exists("/app") else "."
BANCO_DADOS = os.path.join(PASTA_DADOS, "jnb_plataforma.db")
os.makedirs(PASTA_DADOS, exist_ok=True)

def banco_criar():
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        pontos INTEGER DEFAULT 0,
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
    <body style="background:#0f172a;color:white;text-align:center;font-family:Arial;padding:20px;">
        <h1 style="color:#84cc16;">JNB TECNOLOGIA</h1>
        <h3>Plataforma de Serviços e Jogos</h3>
        <div style="margin-top:30px;">
            <a href="/entrar" style="display:block;max-width:400px;margin:10px auto;padding:15px;background:#1e293b;border:2px solid #84cc16;border-radius:10px;color:white;text-decoration:none;">Entrar</a>
            <a href="/cadastro" style="display:block;max-width:400px;margin:10px auto;padding:15px;background:#1e293b;border:2px solid #3b82f6;border-radius:10px;color:white;text-decoration:none;">Criar Conta</a>
        </div>
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
    <html><body style="background:#0f172a;color:white;text-align:center;font-family:Arial;padding:20px;">
        <h2>Criar Conta</h2>
        <form method="POST">
            <input name="nome" placeholder="Seu nome" required style="padding:10px;margin:5px;width:300px;"><br>
            <input name="email" placeholder="Seu email" required style="padding:10px;margin:5px;width:300px;"><br>
            <input name="senha" type="password" placeholder="Sua senha" required style="padding:10px;margin:5px;width:300px;"><br>
            <button type="submit" style="padding:10px 30px;background:#84cc16;border:none;border-radius:5px;color:white;margin-top:10px;">Cadastrar</button>
        </form>
    </body></html>
    """)

@app.route("/entrar", methods=["GET","POST"])
def entrar():
    if request.method == "POST":
        email = request.form.get("email","").strip()
        senha = request.form.get("senha","").strip()
        conn = sqlite3.connect(BANCO_DADOS)
        c = conn.cursor()
        c.execute("SELECT id,nome,pontos FROM usuarios WHERE email=? AND senha=?",(email,senha))
        usuario = c.fetchone()
        conn.close()
        if usuario:
            session["usuario_id"] = usuario[0]
            session["usuario_nome"] = usuario[1]
            session["pontos"] = usuario[2]
            return redirect(url_for("painel"))
    return render_template_string("""
    <html><body style="background:#0f172a;color:white;text-align:center;font-family:Arial;padding:20px;">
        <h2>Entrar</h2>
        <form method="POST">
            <input name="email" placeholder="Seu email" required style="padding:10px;margin:5px;width:300px;"><br>
            <input name="senha" type="password" placeholder="Sua senha" required style="padding:10px;margin:5px;width:300px;"><br>
            <button type="submit" style="padding:10px 30px;background:#3b82f6;border:none;border-radius:5px;color:white;margin-top:10px;">Entrar</button>
        </form>
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
    nome = session.get("usuario_nome", "Usuario")
    pontos = session.get("pontos", 0)
    return render_template_string(f"""
    <html><body style="background:#0f172a;color:white;text-align:center;font-family:Arial;padding:20px;">
        <h2>Bem-vindo, {nome}!</h2>
        <p style="color:#84cc16;font-size:20px;">Pontos: {pontos}</p>
        <div style="margin-top:30px;">
            <a href="/documentos" style="display:block;max-width:400px;margin:10px auto;padding:15px;background:#1e293b;border:2px solid #cbd5e1;border-radius:10px;color:white;text-decoration:none;">📄 Documentos</a>
            <a href="/projetos" style="display:block;max-width:400px;margin:10px auto;padding:15px;background:#1e293b;border:2px solid #cbd5e1;border-radius:10px;color:white;text-decoration:none;">📐 Projetos</a>
            <a href="/anuncios" style="display:block;max-width:400px;margin:10px auto;padding:15px;background:#1e293b;border:2px solid #cbd5e1;border-radius:10px;color:white;text-decoration:none;">📢 Anúncios</a>
            <a href="/bnj" style="display:block;max-width:400px;margin:10px auto;padding:15px;background:#1e293b;border:2px solid #f59e0b;border-radius:10px;color:white;text-decoration:none;">🧬 DNA JNB</a>
            <a href="/rede_social" style="display:block;max-width:400px;margin:10px auto;padding:15px;background:#1e293b;border:2px solid #cbd5e1;border-radius:10px;color:white;text-decoration:none;">🌐 Rede Social</a>
            <a href="/inteligencia" style="display:block;max-width:400px;margin:10px auto;padding:15px;background:#1e293b;border:2px solid #cbd5e1;border-radius:10px;color:white;text-decoration:none;">🧠 Inteligência</a>
            <a href="/jogo_pares" style="display:block;max-width:400px;margin:10px auto;padding:15px;background:#1e293b;border:2px solid #cbd5e1;border-radius:10px;color:white;text-decoration:none;">🎮 Jogo dos Pares</a>
            <a href="/loja_premios" style="display:block;max-width:400px;margin:10px auto;padding:15px;background:#1e293b;border:2px solid #cbd5e1;border-radius:10px;color:white;text-decoration:none;">🏆 Loja de Prêmios</a>
        </div>
        <a href="/sair" style="display:inline-block;margin-top:30px;color:#f87171;text-decoration:none;">Sair</a>
    </body></html>
    """)

@app.route("/documentos", methods=["GET","POST"])
def documentos():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    mensagem = ""
    if request.method == "POST":
        mensagem = "✅ Solicitação enviada!"
    return render_template_string(f"""
    <html><body style="background:#0f172a;color:white;text-align:center;font-family:Arial;padding:20px;">
        <h2>📄 Documentos</h2>
        {mensagem}
        <form method="POST">
            <select name="tipo" style="padding:10px;width:300px;">
                <option value="simples">Documento Simples</option>
                <option value="completo">Documento Completo</option>
                <option value="especial">Documento Especial</option>
            </select><br><br>
            <button type="submit" style="padding:10px 30px;background:#84cc16;border:none;border-radius:5px;color:white;">Solicitar</button>
        </form>
        <br><a href="/painel" style="color:#3b82f6;">← Voltar</a>
    </body></html>
    """)

@app.route("/projetos", methods=["GET","POST"])
def projetos():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    mensagem = ""
    if request.method == "POST":
        mensagem = "✅ Projeto criado!"
    return render_template_string(f"""
    <html><body style="background:#0f172a;color:white;text-align:center;font-family:Arial;padding:20px;">
        <h2>📐 Projetos</h2>
        {mensagem}
        <form method="POST">
            <textarea name="descricao" placeholder="Descreva seu projeto..." style="width:300px;height:100px;padding:10px;"></textarea><br>
            <button type="submit" style="padding:10px 30px;background:#3b82f6;border:none;border-radius:5px;color:white;margin-top:10px;">Criar Projeto</button>
        </form>
        <br><a href="/painel" style="color:#3b82f6;">← Voltar</a>
    </body></html>
    """)

@app.route("/anuncios", methods=["GET","POST"])
def anuncios():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    mensagem = ""
    if request.method == "POST":
        mensagem = "✅ Anúncio publicado!"
    return render_template_string(f"""
    <html><body style="background:#0f172a;color:white;text-align:center;font-family:Arial;padding:20px;">
        <h2>📢 Anúncios</h2>
        {mensagem}
        <form method="POST">
            <input name="titulo" placeholder="Título" style="width:300px;padding:10px;margin:5px;"><br>
            <textarea name="descricao" placeholder="Descrição..." style="width:300px;height:100px;padding:10px;"></textarea><br>
            <button type="submit" style="padding:10px 30px;background:#f59e0b;border:none;border-radius:5px;color:black;margin-top:10px;">Publicar</button>
        </form>
        <br><a href="/painel" style="color:#3b82f6;">← Voltar</a>
    </body></html>
    """)

@app.route("/bnj", methods=["GET", "POST"])
def bnj():
    if not usuario_logado():
        return redirect(url_for("entrar"))

    DNA_ORIGINAL = "yabcdefgxz"
    DNA_PAR      = "yzxgfedcba"

    mensagem = ""
    analise = None

    def converter_sequencia(seq):
        binario = ' '.join(format(ord(c), '08b') for c in seq)
        hexa    = ' '.join(format(ord(c), '02X') for c in seq)
        bits    = len(seq) * 8
        bytes_  = bits // 8
        return binario, hexa, bits, bytes_

    if request.method == "POST":
        sequencia_usuario = request.form.get("sequencia", "").strip().lower()
        bin_ori, hex_ori, bits_ori, bytes_ori = converter_sequencia(DNA_ORIGINAL)
        bin_par, hex_par, bits_par, bytes_par = converter_sequencia(DNA_PAR)

        if sequencia_usuario == DNA_PAR:
            mensagem = "✅ SISTEMA ÍNTEGRO"
            status = "ÍNTEGRO"
            integridade = "100%"
        elif sequencia_usuario == DNA_ORIGINAL:
            mensagem = "ℹ️ Digite o PAR correspondente"
            status = "AGUARDANDO"
            integridade = "—"
        else:
            mensagem = "⚠️ FALHA DETECTADA"
            status = "FALHA"
            integridade = "COMPROMETIDA"

        analise = {
            "status": status, "integridade": integridade,
            "bin_ori": bin_ori, "hex_ori": hex_ori,
            "bin_par": bin_par, "hex_par": hex_par,
            "bits_ori": bits_ori, "bytes_ori": bytes_ori,
            "bits_par": bits_par, "bytes_par": bytes_par,
            "megabits": round((bits_ori + bits_par) / 1_000_000, 6)
        }

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SISTEMA B.N.J.</title>
        <style>
            *{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif}
            body{background:linear-gradient(135deg,#0f172a,#1e293b);min-height:100vh;padding:20px}
            .painel{background:#1e293b;border-radius:20px;padding:30px;max-width:720px;margin:0 auto;border:3px solid #f59e0b}
            h1{text-align:center;color:#f59e0b;margin-bottom:10px}
            .caixa{background:#0f172a;padding:15px;border-radius:10px;border:2px solid #475569;margin:10px 0}
            .rotulo{color:#94a3b8;font-size:13px;margin-bottom:5px}
            .valor{font-family:monospace;color:#f59e0b;word-break:break-all}
            .status{padding:12px;border-radius:8px;text-align:center;font-weight:bold;margin:15px 0;font-size:18px}
            .status.ok{background:#84cc1620;color:#84cc16;border:2px solid #84cc16}
            .status.erro{background:#f8717120;color:#f87171;border:2px solid #f87171}
            .status.info{background:#3b82f620;color:#3b82f6;border:2px solid #3b82f6}
            input{width:100%;padding:14px;font-size:18px;text-align:center;border-radius:10px;border:2px solid #f59e0b;background:#0f172a;color:#f1f5f9;outline:none}
            button{width:100%;padding:14px;font-size:16px;font-weight:bold;background:linear-gradient(90deg,#f59e0b,#d97706);color:#000;border:none;border-radius:10px;margin-top:12px;cursor:pointer}
            a{display:block;text-align:center;margin-top:20px;color:#22d3ee;text-decoration:none}
        </style>
    </head>
    <body>
        <div class="painel">
            <h1>🧬 SISTEMA B.N.J.</h1>
            <div class="caixa">
                <div class="rotulo">Sequência Original:</div>
                <div class="valor">""" + DNA_ORIGINAL + """</div>
            </div>
            <form method="POST">
                <input name="sequencia" placeholder="Digite o PAR correspondente" required autocomplete="off">
                <button>🔍 ANALISAR</button>
            </form>
    """
    if analise:
        html += """
            <div class="status """ + ("ok" if analise['status']=="ÍNTEGRO" else "erro" if analise['status']=="FALHA" else "info") + """">
                """ + analise['status'] + """ — Integridade: """ + analise['integridade'] + """
            </div>
            <p style="text-align:center;color:#cbd5e1;margin:10px 0;">""" + mensagem + """</p>
            <div class="caixa">
                <div class="rotulo">Original → Binário:</div>
                <div class="valor" style="font-size:11px;">""" + analise['bin_ori'] + """</div>
            </div>
            <div class="caixa">
                <div class="rotulo">Original → Hexadecimal:</div>
                <div class="valor">""" + analise['hex_ori'] + """</div>
            </div>
            <div class="caixa">
                <div class="rotulo">Par → Binário:</div>
                <div class="valor" style="font-size:11px;">""" + analise['bin_par'] + """</div>
            </div>
            <div class="caixa">
                <div class="rotulo">Par → Hexadecimal:</div>
                <div class="valor">""" + analise['hex_par'] + """</div>
            </div>
        """
    html += """
        </div>
        <a href="/painel">← Voltar</a>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route("/rede_social")
def rede_social():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    return render_template_string("""
    <html><body style="background:#0f172a;color:white;text-align:center;font-family:Arial;padding:20px;">
        <h2>🌐 Rede Social</h2>
        <br><a href="/painel" style="color:#3b82f6;">← Voltar</a>
    </body></html>
    """)

@app.route("/inteligencia")
def inteligencia():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    return render_template_string("""
    <html><body style="background:#0f172a;color:white;text-align:center;font-family:Arial;padding:20px;">
        <h2>🧠 Inteligência</h2>
        <br><a href="/painel" style="color:#3b82f6;">← Voltar</a>
    </body></html>
    """)

@app.route("/jogo_pares")
def jogo_pares():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    return render_template_string("""
    <html><body style="background:#0f172a;color:white;text-align:center;font-family:Arial;padding:20px;">
        <h2>🎮 Jogo dos Pares</h2>
        <br><a href="/painel" style="color:#3b82f6;">← Voltar</a>
    </body></html>
    """)

@app.route("/loja_premios")
def loja_premios():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    return render_template_string("""
    <html><body style="background:#0f172a;color:white;text-align:center;font-family:Arial;padding:20px;">
        <h2>🏆 Loja de Prêmios</h2>
        <br><a href="/painel" style="color:#3b82f6;">← Voltar</a>
    </body></html>
    """)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
