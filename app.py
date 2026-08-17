# ==================================================
# © 2026 JNB TECNOLOGIA - CODIGO LIMPO SEM ERROS
# DNA DIGITAL B.N.J. INCLUIDO ✅
# SERVIDOR: 0.0.0.0 PORTA 5000 ✅
# ==================================================

from flask import Flask, request, session, redirect, url_for, render_template_string, send_from_directory
import sqlite3
import os
import random
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.secret_key = os.environ.get("CHAVE_UNIFICADA", "JNB_TECNOLOGIA_2026_SEGURA")
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 315360000

PASTA_DADOS = os.path.join(os.path.dirname(__file__), "dados")
os.makedirs(PASTA_DADOS, exist_ok=True)
BANCO_DADOS = os.path.join(PASTA_DADOS, "jnb_plataforma.db")

PASTA_POSTS = os.path.join(PASTA_DADOS, "posts")
os.makedirs(PASTA_POSTS, exist_ok=True)

def conectar_banco():
    conn = sqlite3.connect(BANCO_DADOS)
    conn.row_factory = sqlite3.Row
    return conn

def usuario_logado():
    return "usuario_id" in session

conn = conectar_banco()
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    pontos INTEGER DEFAULT 0,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
)''')
c.execute('''CREATE TABLE IF NOT EXISTS postagens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    texto TEXT,
    arquivo TEXT,
    tipo_arquivo TEXT,
    curtidas INTEGER DEFAULT 0,
    data DATETIME DEFAULT CURRENT_TIMESTAMP
)''')
c.execute('''CREATE TABLE IF NOT EXISTS curtidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    postagem_id INTEGER,
    usuario_id INTEGER
)''')
conn.commit()
conn.close()

PREMIOS = {
    50: {"nome": "Desconto 10%", "valor": 10},
    100: {"nome": "Documento Simples Gratis"},
    200: {"nome": "Desconto 25%", "valor": 25},
    300: {"nome": "Documento Completo Gratis"},
    500: {"nome": "VIP - Desconto 50% por 30 Dias", "valor": 50},
    1000: {"nome": "Documento Especial + Projeto Gratis"}
}

# ======================================
# PÁGINA INICIAL (com botão BNJ)
# ======================================
@app.route("/")
def inicio():
    if usuario_logado():
        return redirect(url_for("painel"))
    return render_template_string('''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>JNB TECNOLOGIA</title>
</head>
<body style="background:#0f172a;color:white;padding:20px;text-align:center;">
    <h1 style="color:#84cc16;">JNB TECNOLOGIA</h1>
    <a href="/documentos" style="display:block;max-width:400px;margin:10px auto;padding:15px;background:#1e293b;border:2px solid #84cc16;border-radius:10px;color:white;text-decoration:none;">📄 Documentos</a>
    <a href="/projetos" style="display:block;max-width:400px;margin:10px auto;padding:15px;background:#1e293b;border:2px solid #84cc16;border-radius:10px;color:white;text-decoration:none;">📐 Projetos</a>
    <a href="/anuncios" style="display:block;max-width:400px;margin:10px auto;padding:15px;background:#1e293b;border:2px solid #84cc16;border-radius:10px;color:white;text-decoration:none;">📢 Anuncios</a>
    <a href="/inteligencia_dna" style="display:block;max-width:400px;margin:10px auto;padding:15px;background:#1e293b;border:2px solid #84cc16;border-radius:10px;color:white;text-decoration:none;">🧬 DNA JNB</a>
    <a href="/bnj" style="display:block;max-width:400px;margin:10px auto;padding:15px;background:#1e293b;border:2px solid #22d3ee;border-radius:10px;color:white;text-decoration:none;">🔬 DNA Digital B.N.J.</a>
    <a href="/rede_social" style="display:block;max-width:400px;margin:10px auto;padding:15px;background:#1e293b;border:2px solid #84cc16;border-radius:10px;color:white;text-decoration:none;">🌐 Rede Social</a>
    <a href="/inteligencia" style="display:block;max-width:400px;margin:10px auto;padding:15px;background:#1e293b;border:2px solid #84cc16;border-radius:10px;color:white;text-decoration:none;">🧠 Inteligencia</a>
    <a href="/jogo_pares" style="display:block;max-width:400px;margin:10px auto;padding:15px;background:#1e293b;border:2px solid #84cc16;border-radius:10px;color:white;text-decoration:none;">🎮 Jogo dos Pares</a>
    <a href="/loja_premios" style="display:block;max-width:400px;margin:10px auto;padding:15px;background:#1e293b;border:2px solid #84cc16;border-radius:10px;color:white;text-decoration:none;">🏆 Loja de Premios</a>
    <a href="/cadastrar" style="display:block;max-width:400px;margin:10px auto;padding:15px;background:#84cc16;color:black;font-weight:bold;border-radius:10px;text-decoration:none;">Criar Conta</a>
</body>
</html>''')

@app.route("/cadastrar", methods=["GET","POST"])
def cadastrar():
    if request.method == "POST":
        nome = request.form.get("nome","")
        email = request.form.get("email","")
        senha = request.form.get("senha","")
        if nome and email and senha:
            conn = conectar_banco()
            try:
                conn.execute("INSERT INTO usuarios (nome,email,senha) VALUES (?,?,?)", (nome,email,senha))
                conn.commit()
                session["usuario_id"] = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                session["nome"] = nome
                return redirect(url_for("painel"))
            except:
                return "E-mail ja cadastrado! <a href='/'>Voltar</a>"
            finally:
                conn.close()
    return render_template_string('''<html><body style="background:#0f172a;color:white;padding:20px;text-align:center;"><h2>Cadastrar Nova Conta</h2><form method="POST">Nome: <input name="nome" required><br>E-mail: <input name="email" required><br>Senha: <input type="password" name="senha" required><br><button type="submit">Cadastrar</button></form><a href="/">Voltar</a></body></html>''')

@app.route("/entrar", methods=["GET","POST"])
def entrar():
    if request.method == "POST":
        email = request.form.get("email","")
        senha = request.form.get("senha","")
        conn = conectar_banco()
        usuario = conn.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?", (email,senha)).fetchone()
        conn.close()
        if usuario:
            session["usuario_id"] = usuario["id"]
            session["nome"] = usuario["nome"]
            return redirect(url_for("painel"))
        return "E-mail ou senha incorretos! <a href='/entrar'>Tentar novamente</a>"
    return render_template_string('''<html><body style="background:#0f172a;color:white;padding:20px;text-align:center;"><h2>Entrar</h2><form method="POST">E-mail: <input name="email" required><br>Senha: <input type="password" name="senha" required><br><button type="submit">Entrar</button></form><a href="/">Voltar</a></body></html>''')

@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("inicio"))

# ======================================
# PAINEL INTERNO (com botão BNJ + versão atualizada)
# ======================================
@app.route("/painel")
def painel():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    nome = session.get("nome", "Usuario")
    conn = conectar_banco()
    usuario = conn.execute("SELECT * FROM usuarios WHERE id = ?", (session["usuario_id"],)).fetchone()
    conn.close()
    pontos = usuario["pontos"] if usuario else 0
    return render_template_string('''<html><body style="background:#0f172a;color:white;padding:20px;text-align:center;">
        <h1>JNB 2 JNB — Versão 2.1</h1>
        <h3>Bem-vindo, ''' + nome + '''!</h3>
        <h3>Pontos: ''' + str(pontos) + '''</h3>
        <a href="/documentos" style="display:inline-block;padding:10px 20px;margin:5px;background:#1e293b;border:2px solid #84cc16;border-radius:8px;color:white;text-decoration:none;">📄 Documentos</a>
        <a href="/projetos" style="display:inline-block;padding:10px 20px;margin:5px;background:#1e293b;border:2px solid #84cc16;border-radius:8px;color:white;text-decoration:none;">📐 Projetos</a>
        <a href="/anuncios" style="display:inline-block;padding:10px 20px;margin:5px;background:#1e293b;border:2px solid #84cc16;border-radius:8px;color:white;text-decoration:none;">📢 Anuncios</a>
        <br>
        <a href="/inteligencia_dna" style="display:inline-block;padding:10px 20px;margin:5px;background:#1e293b;border:2px solid #84cc16;border-radius:8px;color:white;text-decoration:none;">🧬 DNA JNB</a>
        <a href="/bnj" style="display:inline-block;padding:10px 20px;margin:5px;background:#1e293b;border:2px solid #22d3ee;border-radius:8px;color:white;text-decoration:none;">🔬 DNA Digital B.N.J.</a>
        <a href="/rede_social" style="display:inline-block;padding:10px 20px;margin:5px;background:#1e293b;border:2px solid #84cc16;border-radius:8px;color:white;text-decoration:none;">🌐 Rede Social</a>
        <a href="/inteligencia" style="display:inline-block;padding:10px 20px;margin:5px;background:#1e293b;border:2px solid #84cc16;border-radius:8px;color:white;text-decoration:none;">🧠 Inteligencia</a>
        <br>
        <a href="/jogo_pares" style="display:inline-block;padding:10px 20px;margin:5px;background:#1e293b;border:2px solid #84cc16;border-radius:8px;color:white;text-decoration:none;">🎮 Jogo dos Pares</a>
        <a href="/loja_premios" style="display:inline-block;padding:10px 20px;margin:5px;background:#1e293b;border:2px solid #84cc16;border-radius:8px;color:white;text-decoration:none;">🏆 Loja de Premios</a>
        <br><br>
        <a href="/sair" style="color:#ef4444;">Sair</a>
    </body></html>''')


@app.route("/documentos", methods=["GET","POST"])
def documentos():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    mensagem = ""
    if request.method == "POST":
        tipo = request.form.get("tipo", "")
        descricao = request.form.get("descricao", "")
        nomes = {"simples":"Documento Simples","completo":"Documento Completo","especial":"Documento Especial"}
        valores = {"simples":"R$ 15,00","completo":"R$ 35,00","especial":"R$ 80,00"}
        if tipo in nomes:
            mensagem = "✅ Solicitacao Enviada!<br>"+nomes[tipo]+"<br>Valor: "+valores[tipo]+"<br>Descricao: "+(descricao or "Sem descricao")
    return render_template_string('''<html><body style="background:#0f172a;color:white;padding:20px;max-width:600px;margin:0 auto;"><h1>📄 Documentos</h1><form method="POST"><select name="tipo" required><option value="simples">Simples - R$15</option><option value="completo">Completo - R$35</option><option value="especial">Especial - R$80</option></select><br><br>Descricao:<br><textarea name="descricao" rows="4"></textarea><br><br><button type="submit">Solicitar</button></form><p>'''+mensagem+'''</p><a href="/painel">Voltar</a></body></html>''')

@app.route("/projetos", methods=["GET","POST"])
def projetos():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    mensagem = ""
    if request.method == "POST":
        tipo = request.form.get("tipo_projeto", "")
        titulo = request.form.get("titulo", "")
        descricao = request.form.get("descricao", "")
        nomes = {"civil":"Engenharia Civil","eletrica":"Engenharia Eletrica","automacao":"Engenharia de Automacao","outro":"Projeto Especial"}
        if tipo in nomes:
            mensagem = "✅ Projeto Registrado!<br>Area: "+nomes[tipo]+"<br>Titulo: "+titulo+"<br>Descricao: "+descricao
    return render_template_string('''<html><body style="background:#0f172a;color:white;padding:20px;max-width:600px;margin:0 auto;"><h1>📐 Projetos</h1><form method="POST"><select name="tipo_projeto" required><option value="civil">Engenharia Civil</option><option value="eletrica">Engenharia Eletrica</option><option value="automacao">Engenharia de Automacao</option><option value="outro">Outro</option></select><br><br>Titulo:<br><input name="titulo" required><br><br>Descricao:<br><textarea name="descricao" rows="5"></textarea><br><br><button type="submit">Enviar</button></form><p>'''+mensagem+'''</p><a href="/painel">Voltar</a></body></html>''')

@app.route("/anuncios", methods=["GET","POST"])
def anuncios():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    mensagem = ""
    if request.method == "POST":
        plano = request.form.get("plano", "")
        titulo = request.form.get("titulo", "")
        descricao = request.form.get("descricao", "")
        arquivo = request.files.get("arquivo_anuncio")
        planos = {"15dias":["15 Dias","R$ 50,00"],"30dias":["30 Dias","R$ 90,00"],"90dias":["90 Dias","R$ 220,00"]}
        nome_arq = "Nao enviado"
        if arquivo and arquivo.filename:
            nome_arq = secure_filename(arquivo.filename)
            caminho = os.path.join(PASTA_DADOS, "anuncios")
            os.makedirs(caminho, exist_ok=True)
            arquivo.save(os.path.join(caminho, nome_arq))
        if plano in planos:
            mensagem = "✅ Anuncio Registrado!<br>Plano: "+planos[plano][0]+"<br>Valor: "+planos[plano][1]+"<br>Titulo: "+titulo+"<br>Arquivo: "+nome_arq
    return render_template_string('''<html><body style="background:#0f172a;color:white;padding:20px;max-width:600px;margin:0 auto;"><h1>📢 Anuncios</h1><form method="POST" enctype="multipart/form-data"><select name="plano" required><option value="15dias">15 Dias - R$50</option><option value="30dias">30 Dias - R$90</option><option value="90dias">90 Dias - R$220</option></select><br><br>Titulo:<br><input name="titulo" required><br><br>Descricao:<br><textarea name="descricao" rows="4"></textarea><br><br>Arquivo:<br><input type="file" name="arquivo_anuncio"><br><br><button type="submit">Solicitar</button></form><p>'''+mensagem+'''</p><a href="/painel">Voltar</a></body></html>''')

@app.route("/inteligencia", methods=["GET","POST"])
def inteligencia():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    resp = ""
    if request.method == "POST":
        pergunta = request.form.get("pergunta","").strip().lower()
        if "jogo" in pergunta and "par" in pergunta:
            resp = "🎮 Soma 10: 1↔9, 2↔8, 3↔7, 4↔6, 5↔5, 6↔4, 7↔3, 8↔2, 9↔1, 0↔0. 4ª fase = numeros + chave secreta!"
        elif "documento" in pergunta:
            resp = "📄 Simples R$15, Completo R$35, Especial R$80."
        elif "ponto" in pergunta:
            resp = "🏆 1ªF+25 | 2ªF+50 | 3ªF+75 | 4ªF+100 pontos."
        elif "ola" in pergunta:
            resp = "Ola! Pergunte sobre servicos, jogo ou pontos."
        else:
            resp = "📋 Pergunta recebida. Consulte as paginas do painel."
    return render_template_string('''<html><body style="background:#0f172a;color:white;padding:20px;max-width:600px;margin:0 auto;"><h1>🧠 Inteligencia</h1><form method="POST"><textarea name="pergunta" rows="4" placeholder="Faca sua pergunta..." required></textarea><br><br><button type="submit">Enviar</button></form><p>'''+resp+'''</p><a href="/painel">Voltar</a></body></html>''')

@app.route("/inteligencia_dna", methods=["GET","POST"])
def inteligencia_dna():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    res = ""
    if request.method == "POST":
        seq = request.form.get("sequencia","").strip().upper()
        if all(c in "ATCG" for c in seq):
            comp = {"A":"T","T":"A","C":"G","G":"C"}
            fita = "".join(comp.get(c,"?") for c in seq)
            res = "🧬 Original: "+seq+"<br>Complementar: "+fita+"<br>A:"+str(seq.count("A"))+" T:"+str(seq.count("T"))+" C:"+str(seq.count("C"))+" G:"+str(seq.count("G"))
        else:
            res = "⚠️ Use apenas A T C G"
    return render_template_string('''<html><body style="background:#0f172a;color:white;padding:20px;max-width:600px;margin:0 auto;"><h1>🧬 DNA JNB</h1><form method="POST"><input name="sequencia" required placeholder="Ex: AATGCC"><br><br><button type="submit">Analisar</button></form><p>'''+res+'''</p><a href="/painel">Voltar</a></body></html>''')

# ======================================
# DNA DIGITAL B.N.J. — NOVA FUNÇÃO
# ======================================
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
            mensagem = "✅ SISTEMA ÍNTEGRO — Par correspondente confirmado. DNA sem falhas detectadas."
            status = "ÍNTEGRO"
            integridade = "100%"
        elif sequencia_usuario == DNA_ORIGINAL:
            mensagem = "ℹ️ Essa é a sequência ORIGINAL. Digite o PAR correspondente para análise."
            status = "AGUARDANDO"
            integridade = "—"
        else:
            mensagem = "⚠️ FALHA DETECTADA — Sequência não corresponde. Possível erro, corrupção ou alteração."
            status = "FALHA"
            integridade = "COMPROMETIDA"

        analise = {
            "status": status,
            "integridade": integridade,
            "bin_ori": bin_ori, "hex_ori": hex_ori,
            "bin_par": bin_par, "hex_par": hex_par,
            "bits_ori": bits_ori, "bytes_ori": bytes_ori,
            "bits_par": bits_par, "bytes_par": bytes_par,
            "megabits": round((bits_ori + bits_par) / 1_000_000, 6)
        }

    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DNA DIGITAL B.N.J.</title>
        <style>
            *{{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif}}
            body{{background:linear-gradient(135deg,#0f172a,#1e293b);min-height:100vh;padding:20px}}
            .painel{{background:#1e293b;border-radius:20px;padding:30px;max-width:720px;margin:0 auto;border:3px solid #22d3ee;box-shadow:0 0 30px #22d3ee40}}
            h1{{text-align:center;color:#22d3ee;margin-bottom:5px}}
            .sub{{text-align:center;color:#94a3b8;font-size:14px;margin-bottom:25px;line-height:1.5}}
            .bloco{{background:#334155;border-radius:12px;padding:18px;margin-bottom:15px;border:2px solid #475569}}
            .rot{{color:#94a3b8;font-size:13px;margin-bottom:8px}}
            .seq{{font-size:24px;letter-spacing:7px;color:#f1f5f9;font-weight:bold;text-align:center;word-break:break-all}}
            .msg{{padding:14px;border-radius:10px;margin:20px 0;text-align:center;font-weight:bold;
                background:{'#22d3ee20' if '✅' in mensagem else '#f8717120' if '⚠️' in mensagem else '#47556940'};
                color:{'#22d3ee' if '✅' in mensagem else '#f87171' if '⚠️' in mensagem else '#94a3b8'}}}
            .grade{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:15px}}
            .caixa{{background:#0f172a;border-radius:8px;padding:12px}}
            .etq{{color:#64748b;font-size:12px;margin-bottom:5px}}
            .val{{color:#e2e8f0;font-size:13px;word-break:break-all;font-family:monospace}}
            .linha{{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #334155;font-size:14px}}
            input{{width:100%;padding:14px;font-size:20px;text-align:center;border-radius:10px;border:2px solid #22d3ee;
                background:#0f172a;color:#f1f5f9;letter-spacing:5px;outline:none;text-transform:lowercase}}
            button{{width:100%;padding:14px;margin-top:12px;background:linear-gradient(90deg,#22d3ee,#0891b2);
                color:#000;font-weight:bold;font-size:17px;border:none;border-radius:10px;cursor:pointer}}
            button:hover{{transform:scale(1.02)}}
            .titulo{{color:#22d3ee;font-size:15px;margin:20px 0 10px 0;padding-bottom:8px;border-bottom:1px solid #475569}}
            @media(max-width:600px){{.grade{{grid-template-columns:1fr}}}}
        </style>
    </head>
    <body>
        <div class="painel">
            <h1>🧬 DNA DIGITAL — B.N.J.</h1>
            <p class="sub">Análise de Sequências · Integridade · Binário · Hexadecimal · Medição de Dados</p>

            <div class="bloco">
                <div class="rot">🧬 Sequência DNA Original</div>
                <div class="seq">{DNA_ORIGINAL}</div>
            </div>

            <form method="POST">
                <div class="bloco">
                    <div class="rot">🔍 Digite o PAR correspondente</div>
                    <input type="text" name="sequencia" placeholder="yzxgfedcba" autofocus autocomplete="off">
                </div>
                <button type="submit">📡 EXECUTAR ANÁLISE COMPLETA</button>
            </form>

            {f'<div class="msg">{mensagem}</div>' if mensagem else ''}

            {f'''
            <div class="titulo">📊 RELATÓRIO COMPLETO</div>
            <div class="bloco">
                <div class="linha"><span>Status do Sistema</span><span style="color:{'#22d3ee' if analise['status']=='ÍNTEGRO' else '#f87171'}">{analise['status']}</span></div>
                <div class="linha"><span>Integridade Detectada</span><span>{analise['integridade']}</span></div>
            </div>
            <div class="titulo">🔢 CONVERSÃO DE DADOS</div>
            <div class="grade">
                <div class="caixa"><div class="etq">Original · Binário</div><div class="val">{analise['bin_ori']}</div></div>
                <div class="caixa"><div class="etq">Original · Hexadecimal</div><div class="val">{analise['hex_ori']}</div></div>
                <div class="caixa"><div class="etq">Par · Binário</div><div class="val">{analise['bin_par']}</div></div>
                <div class="caixa"><div class="etq">Par · Hexadecimal</div><div class="val">{analise['hex_par']}</div></div>
            </div>
            <div class="titulo">📏 MEDIÇÃO DE CAPACIDADE</div>
            <div class="bloco">
                <div class="linha"><span>Bits — Sequência Original</span><span>{analise['bits_ori']} bits</span></div>
                <div class="linha"><span>Bytes — Sequência Original</span><span>{analise['bytes_ori']} bytes</span></div>
                <div class="linha"><span>Bits — Par Correspondente</span><span>{analise['bits_par']} bits</span></div>
                <div class="linha"><span>Bytes — Par Correspondente</span><span>{analise['bytes_par']} bytes</span></div>
                <div class="linha"><span>Capacidade Total</span><span>{analise['megabits']} Megabits</span></div>
            </div>
            ''' if analise else ''}
        </div>
        <div style="text-align:center;margin-top:20px;"><a href="/painel" style="color:#22d3ee;">← Voltar ao Painel</a></div>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route("/rede_social", methods=["GET","POST"])
def rede_social():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    BANCO = os.path.join(PASTA_DADOS, "jnb_plataforma.db")
    msg = ""
    if request.method == "POST" and "texto_post" in request.form:
        texto = request.form.get("texto_post","").strip()
        arq = request.files.get("arquivo_post")
        nome_arq = None
        tipo_arq = None
        if arq and arq.filename:
            seguro = secure_filename(arq.filename)
            nome_arq = datetime.now().strftime("%Y%m%d%H%M%S_")+seguro
            arq.save(os.path.join(PASTA_POSTS, nome_arq))
            ext = seguro.rsplit(".",1)[-1].lower() if "." in seguro else ""
            if ext in {"jpg","jpeg","png","gif"}: tipo_arq = "imagem"
            elif ext in {"mp4","webm","mov"}: tipo_arq = "video"
        conn = sqlite3.connect(BANCO)
        conn.execute("INSERT INTO postagens VALUES (NULL,?,?,?,?,0,CURRENT_TIMESTAMP)",(session["usuario_id"],texto,nome_arq,tipo_arq))
        conn.commit()
        conn.close()
        msg = "✅ Postado!"
    if request.method == "POST" and "curtir" in request.form:
        pid = request.form.get("post_id")
        conn = sqlite3.connect(BANCO)
        if not conn.execute("SELECT * FROM curtidas WHERE postagem_id=? AND usuario_id=?",(pid,session["usuario_id"])).fetchone():
            conn.execute("INSERT INTO curtidas VALUES (NULL,?,?)",(pid,session["usuario_id"]))
            conn.execute("UPDATE postagens SET curtidas=curtidas+1 WHERE id=?",(pid,))
            conn.commit()
        conn.close()
        return redirect(url_for("rede_social"))
    conn = sqlite3.connect(BANCO)
    conn.row_factory = sqlite3.Row
    posts = conn.execute("SELECT p.*,u.nome FROM postagens p JOIN usuarios u ON p.usuario_id=u.id ORDER BY p.data DESC").fetchall()
    conn.close()
    html = ""
    for p in posts:
        midia = ""
        if p["tipo_arquivo"]=="imagem" and p["arquivo"]:
            midia = "<img src='/ver_arquivo/"+p["arquivo"]+"' style='max-width:100%;border-radius:8px;'>"
        elif p["tipo_arquivo"]=="video" and p["arquivo"]:
            midia = "<video controls style='max-width:100%;'><source src='/ver_arquivo/"+p["arquivo"]+"'></video>"
        html += "<div style='background:#1e293b;padding:12px;margin:8px 0;border-radius:8px;'><b>"+p["nome"]+"</b> "+p["data"][:16]+"<p>"+(p["texto"] or "")+"</p>"+midia+"<form method='POST'><input type='hidden' name='post_id' value='"+str(p["id"])+"'><button name='curtir' style='border:none;background:none;color:red;'>❤️ "+str(p["curtidas"])+"</button></form></div>"
    return render_template_string('''<html><body style="background:#0f172a;color:white;padding:20px;max-width:600px;margin:0 auto;"><h1>🌐 Rede Social</h1><p>'''+msg+'''</p><form method="POST" enctype="multipart/form-data"><textarea name="texto_post" rows="3" placeholder="Escreva algo..." required></textarea><br><input type="file" name="arquivo_post" accept="image/*,video/*"><br><button type="submit">Publicar</button></form>'''+html+'''<br><a href="/painel">Voltar</a></body></html>''')

@app.route("/ver_arquivo/<nome>")
def ver_arquivo(nome):
    return send_from_directory(PASTA_POSTS, nome)

@app.route("/loja_premios")
def loja_premios():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    conn = conectar_banco()
    u = conn.execute("SELECT * FROM usuarios WHERE id=?",(session["usuario_id"],)).fetchone()
    conn.close()
    pts = u["pontos"] if u else 0
    html = ""
    for v,p in PREMIOS.items():
        tem = pts >= v
        html += str(v)+"pts → "+p["nome"]+(" ✅" if tem else (" - falta "+str(v-pts))) + "<br>"
    return render_template_string('''<html><body style="background:#0f172a;color:white;padding:20px;max-width:600px;margin:0 auto;"><h1>🏆 Loja de Premios</h1><h3>Seus Pontos: '''+str(pts)+'''</h3><p>'''+html+'''</p><a href="/painel">Voltar</a></body></html>''')

@app.route("/jogo_pares", methods=["GET","POST"])
def jogo_pares():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    if "pontos" not in session: session["pontos"]=0
    if "sequencia" not in session: session["sequencia"]=[]
    if "fase_atual" not in session: session["fase_atual"]=3
    if "tentativas_na_fase" not in session: session["tentativas_na_fase"]={}
    if "vez_chave_100" not in session: session["vez_chave_100"]=0

    PAR = {"0":"0","1":"9","2":"8","3":"7","4":"6","5":"5","6":"4","7":"3","8":"2","9":"1"}
    FASES = {3:[0,25,"1ª Fase"],6:[1,50,"2ª Fase"],8:[2,75,"3ª Fase"],9:[2,100,"🏆 4ª FASE"]}
    CHAVES = ["WYK","KYW","YWK"]
    SIMB = ["🟠","🔴","⚫","⚪","🟣","🔶"]
    msg = ""

    if request.method=="POST" and "trocar_fase" in request.form:
        session["fase_atual"]=int(request.form["trocar_fase"])
        session["sequencia"]=[]

    if request.method=="POST" and "nova_sequencia" in request.form:
        f = session["fase_atual"]
        tent = session["tentativas_na_fase"].get(str(f),0)
        seq = []
        for _ in range(f):
            d = str(random.randint(0,9))
            if tent==0: nc = d+str(random.randint(0,9))+str(random.randint(0,9))+str(random.randint(0,9))
            elif tent==1: nc = str(random.randint(0,9))+d+str(random.randint(0,9))+str(random.randint(0,9))
            else: nc = str(random.randint(0,9))+str(random.randint(0,9))+d+str(random.randint(0,9))
            seq.append({"n":nc,"s":random.choice(SIMB)})
        session["sequencia"]=seq

    if request.method=="POST" and "resposta" in request.form:
        resp = request.form.get("resposta","").strip().upper().replace(" ","")
        seq = session.get("sequencia",[])
        f = session["fase_atual"]
        pos,pts,nome = FASES[f]
        if not seq:
            msg = "⚠️ Gere sequencia primeiro!"
        else:
            tent = session["tentativas_na_fase"].get(str(f),0)
            digitos = []
            for x in seq: digitos.append(PAR[x["n"][pos]])
            if pts==100:
                chave_correta = CHAVES[session["vez_chave_100"]%3]
                correta = "".join(digitos)+chave_correta
            else:
                correta = "".join(digitos)
            if resp==correta:
                session["pontos"]+=pts
                conn = conectar_banco()
                conn.execute("UPDATE usuarios SET pontos=pontos+? WHERE id=?",(pts,session["usuario_id"]))
                conn.commit();conn.close()
                msg = "✅ ACERTOU! +"+str(pts)+"pts Total: "+str(session["pontos"])
                session["tentativas_na_fase"][str(f)]=0
                if pts==100: session["vez_chave_100"]+=1
                session["sequencia"]=[]
            else:
                msg = "❌ Errou! Tente novamente."
                session["tentativas_na_fase"][str(f)]=tent+1

    seq = session.get("sequencia",[])
    f = session["fase_atual"]
    pos,pts,nome = FASES[f]
    tent = session["tentativas_na_fase"].get(str(f),0)
    aviso = ""
    if tent==1: aviso = "⚠️ Atencao! Os numeros mudaram de posicao!"
    elif tent>=2: aviso = "🔴 Ficou mais dificil!"
    html_seq = ""
    for x in seq: html_seq += x["s"]+" = "+x["n"]+"<br>"

    return render_template_string('''<html><body style="background:#0f172a;color:white;padding:20px;text-align:center;"><h1>🎮 O Segredo dos Numeros</h1><h3>Pontos: '''+str(session["pontos"])+''' | '''+nome+'''</h3><form method="POST"><button name="trocar_fase" value="3">F1</button><button name="trocar_fase" value="6">F2</button><button name="trocar_fase" value="8">F3</button><button name="trocar_fase" value="9">F4</button></form><br><form method="POST"><button name="nova_sequencia">🔄 Gerar Sequencia</button></form><p>'''+aviso+'''</p><p style="font-size:24px;">'''+html_seq+'''</p>''' + ('''<form method="POST"><input name="resposta" placeholder="Resposta" style="padding:10px;font-size:20px;text-align:center;"><br><br><button>✅ Enviar</button></form>''' if seq else "") + '''<p>'''+msg+'''</p><br><a href="/painel">Voltar</a></body></html>''')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
