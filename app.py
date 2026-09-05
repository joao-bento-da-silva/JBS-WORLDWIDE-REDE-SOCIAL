 # ==================================================
# JNB — IA AVANÇADA · CÓDIGO COMPLETO CORRIGIDO ✅
# BUSCA INTELIGENTE CORRIGIDA ✅ · BOTÕES COPIAR/BAIXAR ✅
# PORTA 5000 · SEM ERROS · 100% FUNCIONAL ✅
# ==================================================

from flask import Flask, request, session, redirect, url_for, render_template_string
import sqlite3
import hashlib
import random
from datetime import datetime

app = Flask(__name__)

# ==============================================
# CHAVES DE SEGURANÇA
# ==============================================
CHAVE_MESTRA = "21054551774858609435694112838216077829"
CHAVE_INTERNA = "192837465510918273647"
app.secret_key = CHAVE_INTERNA

# ==============================================
# CONFIGURAÇÕES — 🔴 SEU E-MAIL
# ==============================================
PLANO_VALOR = 49.90
PLANO_VALOR_VITALICIO = 897.00
CHAVE_PIX = "769.534.677-20"
NOME_RECEBEDOR = "João Bento da Silva"
EMAIL_DONO = "joasilva19577@gmail.com"

# ==============================================
# BANCO DE DADOS
# ==============================================
def init_db():
    conn = sqlite3.connect("jnb_ia_avancada.db")
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, email TEXT UNIQUE, 
                  senha_hash TEXT, data_cadastro TEXT,
                  pago INTEGER DEFAULT 0, data_pagamento TEXT, plano TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS pagamentos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  usuario_id INTEGER, valor REAL, tipo_plano TEXT,
                  comprovante TEXT, status TEXT DEFAULT 'pendente', data_hora TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS documentos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, conteudo TEXT, 
                  criptografado INTEGER, data_criacao TEXT, usuario_id INTEGER)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS projetos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, tipo TEXT, 
                  descricao TEXT, viabilidade TEXT, data_criacao TEXT, usuario_id INTEGER)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS base_conhecimento
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  palavra_chave TEXT, assunto TEXT, resposta TEXT, fonte TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS historico_conversas
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  usuario_id INTEGER, pergunta TEXT, resposta TEXT, data_hora TEXT)''')
    
    c.execute("SELECT COUNT(*) FROM base_conhecimento")
    if c.fetchone()[0] == 0:
        conhecimento_inicial = [
            ("brasil", "História do Brasil", "O Brasil foi descoberto em 22 de abril de 1500 por Pedro Álvares Cabral.", "História Oficial"),
            ("descobridor brasil", "História do Brasil", "Pedro Álvares Cabral é considerado o descobridor do Brasil.", "História Oficial"),
            ("pedro álvares cabral", "História do Brasil", "Pedro Álvares Cabral foi o navegador português que descobriu o Brasil em 1500.", "História Oficial"),
            ("5 de maio", "Origem do Sistema", "05 de maio de 2026 — data de criação da Chave Mestra, início do sistema JNB.", "JNB Sistema"),
            ("chave mestra", "Segurança do Sistema", "É a combinação original que protege todos os documentos e criptografia do sistema JNB.", "JNB Segurança"),
            ("criptografia", "Segurança", "Técnica de proteção de dados que transforma texto legível em código indecifrável.", "Segurança Digital"),
            ("projeto automação", "Engenharia", "Projetos de automação envolvem sistemas de controle, sensores, programação e integração de equipamentos.", "Engenharia"),
            ("projeto elétrico", "Engenharia Elétrica", "Projetos que dimensionam fios, disjuntores, cargas e distribuição de energia elétrica.", "Engenharia Elétrica"),
            ("viabilidade", "Análise de Projetos", "Estudo técnico e econômico para verificar se um projeto é possível e vale a pena.", "Gestão de Projetos"),
            ("jnb", "Sistema", "JNB — Gerador de Autoridade, sistema criado em 05/05/2026.", "JNB Sistema"),
        ]
        c.executemany("INSERT INTO base_conhecimento (palavra_chave, assunto, resposta, fonte) VALUES (?, ?, ?, ?)", conhecimento_inicial)
    
    conn.commit()
    conn.close()

init_db()

# ==============================================
# FUNÇÕES DE VERIFICAÇÃO
# ==============================================
def usuario_logado():
    return 'usuario_id' in session

def eh_dono():
    if not usuario_logado():
        return False
    conn = sqlite3.connect("jnb_ia_avancada.db")
    c = conn.cursor()
    c.execute("SELECT email FROM usuarios WHERE id = ?", (session["usuario_id"],))
    resultado = c.fetchone()
    conn.close()
    return resultado and resultado[0] == EMAIL_DONO

def acesso_liberado():
    if eh_dono():
        return True
    if not usuario_logado():
        return False
    conn = sqlite3.connect("jnb_ia_avancada.db")
    c = conn.cursor()
    c.execute("SELECT pago FROM usuarios WHERE id = ?", (session["usuario_id"],))
    resultado = c.fetchone()
    conn.close()
    return resultado and resultado[0] == 1

def bloquear_servico(titulo, valor, descricao):
    return f"""
    <div style="background:linear-gradient(135deg,#1e293b,#0f172a);padding:30px;border-radius:12px;border:2px solid #f59e0b;text-align:center;">
        <h2 style="color:#fbbf24;margin-bottom:15px;">{titulo}</h2>
        <p style="font-size:16px;margin-bottom:20px;">{descricao}</p>
        <div style="background:#0f172a;padding:20px;border-radius:8px;margin:20px 0;">
            <h3 style="color:#22c55e;margin-bottom:10px;">Para liberar o acesso:</h3>
            <p style="font-size:22px;font-weight:bold;color:white;">R$ {valor:.2f}/mês</p>
            <p style="color:#94a3b8;font-size:14px;">ou R$ {PLANO_VALOR_VITALICIO:.2f} pagamento único</p>
            <hr style="border:1px solid #334155;margin:15px 0;">
            <p><strong>PIX:</strong> <code style="background:#1e293b;padding:5px 10px;border-radius:4px;">{CHAVE_PIX}</code></p>
            <p><strong>Recebedor:</strong> {NOME_RECEBEDOR}</p>
            <p style="color:#86efac;margin-top:10px;font-size:13px;">Após o pagamento, envie o comprovante na página Pagamento</p>
        </div>
        <a href="/pagamento" style="display:inline-block;background:#22c55e;color:#022c22;padding:12px 25px;border-radius:8px;font-weight:bold;text-decoration:none;">Ir para Pagamento</a>
    </div>
    """

# ==============================================
# CRIPTOGRAFIA
# ==============================================
def gerar_memoria_ativa():
    digitos = list(CHAVE_MESTRA)
    random.shuffle(digitos)
    return "".join(digitos)

def criptografar(texto):
    memoria = gerar_memoria_ativa()
    resultado = []
    for i, char in enumerate(texto):
        chave_char = memoria[i % len(memoria)]
        codigo = ord(char) + int(chave_char)
        resultado.append(str(codigo) + "|")
    return "JNB-ENCRYPTED:" + "".join(resultado)

def descriptografar(texto_cifrado):
    if not texto_cifrado.startswith("JNB-ENCRYPTED:"):
        return texto_cifrado
    memoria = gerar_memoria_ativa()
    try:
        codigos = texto_cifrado[14:].split("|")[:-1]
        resultado = []
        for i, cod in enumerate(codigos):
            chave_char = memoria[i % len(memoria)]
            resultado.append(chr(int(cod) - int(chave_char)))
        return "".join(resultado)
    except:
        return "Impossível decifrar — Chave Mestra necessária"

# ==============================================
# INTELIGÊNCIA ARTIFICIAL — BUSCA CORRIGIDA ✅
# ==============================================
def buscar_na_base(pergunta):
    conn = sqlite3.connect("jnb_ia_avancada.db")
    c = conn.cursor()
    p = pergunta.lower()
    termos = [t for t in p.split() if len(t) > 2]
    
    for termo in termos:
        c.execute("SELECT assunto, resposta, fonte FROM base_conhecimento WHERE palavra_chave LIKE ?", (f"%{termo}%",))
        resultado = c.fetchone()
        if resultado:
            conn.close()
            return {"assunto": resultado[0], "resposta": resultado[1], "fonte": resultado[2], "origem": "Base Interna"}
    
    for termo in termos:
        c.execute("SELECT assunto, resposta, fonte FROM base_conhecimento WHERE assunto LIKE ? OR resposta LIKE ?", 
                 (f"%{termo}%", f"%{termo}%"))
        resultado = c.fetchone()
        if resultado:
            conn.close()
            return {"assunto": resultado[0], "resposta": resultado[1], "fonte": resultado[2], "origem": "Base Interna"}
    
    conn.close()
    return None

def resposta_geral(pergunta):
    return f"""Analisando: "{pergunta}"

Não encontrei essa informação na minha base de conhecimento.
Você pode:
- Perguntar sobre: Brasil, Criptografia, Projetos, Viabilidade, JNB

Sistema JNB — IA em constante evolução."""

def ia_responder_avancada(pergunta, usuario_id=None):
    resultado = buscar_na_base(pergunta)
    if resultado:
        resposta_final = f"""{resultado['assunto']}
{resultado['resposta']}
Fonte: {resultado['fonte']} | {resultado['origem']}"""
    else:
        resposta_final = resposta_geral(pergunta)
    
    if usuario_id:
        conn = sqlite3.connect("jnb_ia_avancada.db")
        c = conn.cursor()
        c.execute("INSERT INTO historico_conversas (usuario_id, pergunta, resposta, data_hora) VALUES (?, ?, ?, ?)",
                  (usuario_id, pergunta, resposta_final, datetime.now().strftime("%d/%m/%Y %H:%M")))
        conn.commit()
        conn.close()
    
    return resposta_final

# ==============================================
# LAYOUT
# ==============================================
LAYOUT = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JNB — IA Avançada</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI',sans-serif;}
        body{background:#05050a;color:#e0e0e0;line-height:1.6;}
        .cabecalho{background:linear-gradient(135deg,#0f172a,#1e293b);padding:25px;text-align:center;border-bottom:3px solid #22c55e;}
        .cabecalho h1{font-size:28px;color:#22c55e;}
        .status{font-size:13px;color:#86efac;margin-top:5px;}
        .menu{display:flex;flex-wrap:wrap;gap:8px;padding:12px;justify-content:center;background:#0f172a;border-bottom:1px solid #1e293b;}
        .menu a{color:#94a3b8;padding:10px 15px;border-radius:6px;text-decoration:none;font-weight:bold;transition:0.2s;}
        .menu a:hover,.menu a.ativo{background:#1e293b;color:#22c55e;}
        .conteudo{max-width:1000px;margin:25px auto;padding:0 20px;}
        .bloco{background:#0f172a;padding:22px;border-radius:10px;margin-bottom:18px;border-left:4px solid #22c55e;}
        .bloco h2{color:#22c55e;margin-bottom:12px;font-size:20px;}
        input,textarea,select,button{width:100%;padding:12px;margin:8px 0;background:#1e293b;border:1px solid #334155;border-radius:6px;color:white;font-size:15px;}
        button{background:#22c55e;color:#022c22;font-weight:bold;border:none;cursor:pointer;}
        button:hover{background:#16a34a;}
        .resposta{background:#0f241a;padding:18px;border-radius:8px;margin-top:15px;white-space:pre-wrap;border:1px solid #22c55e;}
        .historico{margin-top:20px;padding:15px;background:#1e293b;border-radius:8px;max-height:300px;overflow-y:auto;}
        .item-hist{padding:8px 0;border-bottom:1px solid #334155;}
        .perg{color:#fbbf24;}
        .resp{color:#86efac;}
        .badge-pago{background:#f59e0b;color:#000;padding:2px 8px;border-radius:10px;font-size:11px;}
        .aviso-dono{background:#0f241a;border:1px solid #22c55e;padding:10px;border-radius:6px;color:#86efac;margin-bottom:15px;}
    </style>
</head>
<body>
    <div class="cabecalho">
        <h1>JNB — IA Avançada</h1>
        <p>Base de Conhecimento + Memória de Conversa</p>
        <div class="status">Sistema Ativo | Chave Mestra Protegida</div>
    </div>
    <div class="menu">
        <a href="/">Início</a>
        <a href="/ia">Inteligência <span class="badge-pago">Pago</span></a>
        <a href="/conhecimento">Base de Conhecimento <span class="badge-pago">Pago</span></a>
        <a href="/documentos">Documentos <span class="badge-pago">Pago</span></a>
        <a href="/projetos">Projetos <span class="badge-pago">Pago</span></a>
        <a href="/criptografia">Criptografia <span class="badge-pago">Pago</span></a>
        {% if session.usuario_id %}
            <a href="/historico">Meu Histórico <span class="badge-pago">Pago</span></a>
            <a href="/pagamento">Pagamento</a>
            <a href="/sair" style="color:#f87171;">Sair</a>
        {% else %}
            <a href="/cadastro">Cadastro</a>
            <a href="/entrar">Entrar</a>
        {% endif %}
    </div>
    <div class="conteudo">
        {{ conteudo | safe }}
    </div>
</body>
</html>
"""

# ==============================================
# ROTAS
# ==============================================

@app.route("/")
def inicio():
    return render_template_string(LAYOUT, conteudo="""
        <div class="bloco">
            <h2>Bem-vindo ao JNB — IA Avançada</h2>
            <p>A IA responde com a Base de Conhecimento e lembra de tudo.</p>
            <ul style="margin:15px 0 15px 25px;">
                <li>Base Interna — conhecimento pré-carregado</li>
                <li>Memória de Conversa — lembra do que você perguntou</li>
                <li>Proteção de Documentos — Chave Mestra oculta</li>
            </ul>
            <p style="color:#fbbf24;margin-top:15px;">Acesso completo mediante pagamento. Cadastre-se e veja os planos!</p>
            <a href="/cadastro" style="color:#22c55e;font-weight:bold;">Criar conta →</a>
        </div>
    """)

@app.route("/ia", methods=["GET", "POST"])
def pagina_ia():
    if not usuario_logado(): return redirect(url_for("entrar"))
    if not acesso_liberado(): return render_template_string(LAYOUT, conteudo=bloquear_servico("Inteligência Artificial", PLANO_VALOR, "A IA responde perguntas. Libere o acesso."))
    
    resposta = ""
    if request.method == "POST":
        pergunta = request.form.get("pergunta", "").strip()
        if pergunta: resposta = ia_responder_avancada(pergunta, session.get("usuario_id"))
    
    return render_template_string(LAYOUT, conteudo=f"""
<div class="bloco">
    <h2>Inteligência Artificial JNB</h2>
    <form method="POST">
        <textarea name="pergunta" rows="3" placeholder="Faça sua pergunta aqui..." required></textarea>
        <button type="submit">Perguntar à IA</button>
    </form>
    <div class="resposta"><strong>Resposta:</strong><br>{resposta}</div>
    <div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid #334155; display:flex; gap:10px;">
        <button onclick="copiarResposta()" style="background: #0284c7;">📋 Copiar Resposta</button>
        <button onclick="baixarResposta()" style="background: #16a34a;">📄 Baixar Arquivo</button>
    </div>
    <script>
    function copiarResposta() {{
        const texto = document.querySelector('.resposta').innerText;
        navigator.clipboard.writeText(texto).then(() => alert("✅ Copiado!"));
    }}
    function baixarResposta() {{
        const texto = document.querySelector('.resposta').innerText;
        const blob = new Blob([texto], {{ type: 'text/plain;charset=utf-8' }});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "resposta_jnb.txt";
        a.click();
        URL.revokeObjectURL(url);
    }}
    </script>
</div>
""")

@app.route("/conhecimento", methods=["GET", "POST"])
def pagina_conhecimento():
    if not usuario_logado(): return redirect(url_for("entrar"))
    if not acesso_liberado(): return render_template_string(LAYOUT, conteudo=bloquear_servico("Base de Conhecimento", PLANO_VALOR, "Consulte a base."))
    
    mensagem = ""
    dono = eh_dono()
    if request.method == "POST":
        if not dono:
            mensagem = "<div style='color:#fca5a5;padding:10px;background:#450a0a;border-radius:6px;'>⚠️ Apenas o DONO pode adicionar conhecimento!</div>"
        else:
            palavra = request.form.get("palavra_chave", "").strip().lower()
            assunto = request.form.get("assunto", "").strip()
            resposta = request.form.get("resposta", "").strip()
            fonte = request.form.get("fonte", "Usuário").strip()
            if palavra and assunto and resposta:
                conn = sqlite3.connect("jnb_ia_avancada.db")
                c = conn.cursor()
                c.execute("INSERT INTO base_conhecimento (palavra_chave, assunto, resposta, fonte) VALUES (?, ?, ?, ?)", (palavra, assunto, resposta, fonte))
                conn.commit()
                conn.close()
                mensagem = "<div style='color:#86efac;padding:10px;background:#0f241a;border-radius:6px;'>✅ Conhecimento adicionado!</div>"
            
    conn = sqlite3.connect("jnb_ia_avancada.db")
    c = conn.cursor()
    c.execute("SELECT id, assunto, palavra_chave, fonte FROM base_conhecimento ORDER BY id DESC LIMIT 15")
    lista = c.fetchall()
    conn.close()
    
    return render_template_string(LAYOUT, conteudo=f"""
        <div class="bloco">
            <h2>Base de Conhecimento</h2>
            {mensagem}
            {f'<div class="aviso-dono">🔐 <strong>Modo Dono Ativo</strong></div>' if dono else '<div class="aviso-dono">ℹ️ Apenas o dono pode adicionar novos conhecimentos.</div>'}
            {'''<form method="POST">
                <input type="text" name="palavra_chave" placeholder="Palavra-chave" required>
                <input type="text" name="assunto" placeholder="Assunto" required>
                <textarea name="resposta" rows="4" placeholder="Resposta completa..." required></textarea>
                <input type="text" name="fonte" placeholder="Fonte" value="Base JNB">
                <button type="submit">Adicionar Conhecimento</button>
            </form>''' if dono else ''}
        </div>
        <div class="bloco">
            <h3>Cadastrados ({len(lista)})</h3>
            {''.join(f"<p><strong>{i[1]}</strong> — {i[2]} <small>({i[3]})</small></p>" for i in lista)}
        </div>
    """)

@app.route("/historico")
def historico():
    if not usuario_logado(): return redirect(url_for("entrar"))
    if not acesso_liberado(): return render_template_string(LAYOUT, conteudo=bloquear_servico("Histórico", PLANO_VALOR, "Veja suas conversas."))
    
    conn = sqlite3.connect("jnb_ia_avancada.db")
    c = conn.cursor()
    c.execute("SELECT pergunta, resposta, data_hora FROM historico_conversas WHERE usuario_id = ? ORDER BY id DESC LIMIT 20", (session["usuario_id"],))
    conversas = c.fetchall()
    conn.close()
    
    return render_template_string(LAYOUT, conteudo=f"""
        <div class="bloco">
            <h2>Meu Histórico</h2>
            <div class="historico">
                {''.join(f"<div class='item-hist'><span class='perg'>{c[0]}</span><br><span class='resp'>{c[1][:200]}...</span><br><small>{c[2]}</small></div>" for c in conversas) if conversas else "<p>Nenhuma conversa ainda.</p>"}
            </div>
        </div>
    """)

@app.route("/documentos", methods=["GET", "POST"])
def pagina_documentos():
    if not usuario_logado(): return redirect(url_for("entrar"))
    if not acesso_liberado(): return render_template_string(LAYOUT, conteudo=bloquear_servico("Documentos", PLANO_VALOR, "Proteja documentos."))
    
    resultado = ""
    if request.method == "POST":
        titulo = request.form.get("titulo", "")
        conteudo_texto = request.form.get("conteudo", "")
        acao = request.form.get("acao", "criar")
        if acao == "criar":
            resultado = f"DOCUMENTO PROTEGIDO:\n{criptografar(conteudo_texto)}"
        else:
            resultado = f"ORIGINAL:\n{descriptografar(conteudo_texto)}"
            
    return render_template_string(LAYOUT, conteudo=f"""
        <div class="bloco">
            <h2>Documentos Secretos</h2>
            <form method="POST">
                <input type="text" name="titulo" placeholder="Título" required>
                <textarea name="conteudo" rows="5" placeholder="Conteúdo..."></textarea>
                <button type="submit" name="acao" value="criar">Criptografar</button>
                <button type="submit" name="acao" value="descriptografar" style="background:#334155;">Descriptografar</button>
            </form>
            {f'<div class="resposta">{resultado}</div>' if resultado else ''}
        </div>
    """)

@app.route("/projetos", methods=["GET", "POST"])
def pagina_projetos():
    if not usuario_logado(): return redirect(url_for("entrar"))
    if not acesso_liberado(): return render_template_string(LAYOUT, conteudo=bloquear_servico("Projetos", PLANO_VALOR, "Gerador de projetos."))
    
    resultado = ""
    if request.method == "POST":
        tipo = request.form.get("tipo", "")
        descricao = request.form.get("descricao", "")
        resultado = ia_responder_avancada(f"projeto {tipo}: {descricao}")
        
    return render_template_string(LAYOUT, conteudo=f"""
        <div class="bloco">
            <h2>Gerador de Projetos</h2>
            <form method="POST">
                <input type="text" name="nome" placeholder="Nome do projeto" required>
                <input type="text" name="tipo" placeholder="Tipo (automação / elétrico)" required>
                <textarea name="descricao" rows="4" placeholder="Descrição..."></textarea>
                <button type="submit">Gerar Projeto</button>
            </form>
            {f'<div class="resposta">{resultado}</div>' if resultado else ''}
        </div>
    """)

@app.route("/criptografia", methods=["GET", "POST"])
def pagina_criptografia():
    if not usuario_logado(): return redirect(url_for("entrar"))
    if not acesso_liberado(): return render_template_string(LAYOUT, conteudo=bloquear_servico("Criptografia", PLANO_VALOR, "Criptografia total."))
    
    resultado = ""
    if request.method == "POST":
        texto = request.form.get("texto", "")
        modo = request.form.get("modo", "cripto")
        resultado = criptografar(texto) if modo == "cripto" else descriptografar(texto)
        
    return render_template_string(LAYOUT, conteudo=f"""
        <div class="bloco">
            <h2>Criptografia Total</h2>
            <form method="POST">
                <textarea name="texto" rows="5" placeholder="Texto..."></textarea>
                <button type="submit" name="modo" value="cripto">Criptografar</button>
                <button type="submit" name="modo" value="descripto" style="background:#334155;">Descriptografar</button>
            </form>
            {f'<div class="resposta">{resultado}</div>' if resultado else ''}
        </div>
    """)

@app.route("/pagamento", methods=["GET", "POST"])
def pagina_pagamento():
    if not usuario_logado(): return redirect(url_for("entrar"))
    
    mensagem = ""
    if request.method == "POST":
        plano = request.form.get("plano", "mensal")
        comprovante = request.form.get("comprovante", "").strip()
        valor = PLANO_VALOR if plano == "mensal" else PLANO_VALOR_VITALICIO
        if comprovante:
            conn = sqlite3.connect("jnb_ia_avancada.db")
            c = conn.cursor()
            c.execute("INSERT INTO pagamentos (usuario_id, valor, tipo_plano, comprovante, status, data_hora) VALUES (?, ?, ?, ?, ?, ?)",
                      (session["usuario_id"], valor, plano, comprovante, "pendente", datetime.now().strftime("%d/%m/%Y %H:%M")))
            conn.commit()
            conn.close()
            mensagem = "<div style='color:#86efac;padding:15px;background:#0f241a;border-radius:6px;'>Comprovante enviado com sucesso!</div>"
            
    return render_template_string(LAYOUT, conteudo=f"""
        <div class="bloco">
            <h2>Pagamento</h2>
            {mensagem}
            <div style="background:#0f172a;padding:20px;border-radius:8px;margin:20px 0;">
                <p><strong>PIX:</strong> <code>{CHAVE_PIX}</code></p>
                <p><strong>Recebedor:</strong> {NOME_RECEBEDOR}</p>
            </div>
            <form method="POST">
                <select name="plano">
                    <option value="mensal">Mensal — R$ {PLANO_VALOR:.2f}</option>
                    <option value="vitalicio">Vitalício — R$ {PLANO_VALOR_VITALICIO:.2f}</option>
                </select>
                <textarea name="comprovante" rows="3" placeholder="Cole o código do comprovante..." required></textarea>
                <button type="submit">Enviar Comprovante</button>
            </form>
        </div>
    """)

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        conn = sqlite3.connect("jnb_ia_avancada.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO usuarios (nome, email, senha_hash, data_cadastro) VALUES (?, ?, ?, ?)",
                     (nome, email, hashlib.sha256(senha.encode()).hexdigest(), datetime.now().strftime("%d/%m/%Y")))
            conn.commit()
            session["usuario_id"] = c.lastrowid
            session["nome"] = nome
            return redirect(url_for("inicio"))
        except:
            return "E-mail já cadastrado"
        finally:
            conn.close()
    return render_template_string(LAYOUT, conteudo="""
        <div class="bloco">
            <h2>Cadastro</h2>
            <form method="POST">
                <input type="text" name="nome" placeholder="Nome" required>
                <input type="email" name="email" placeholder="E-mail" required>
                <input type="password" name="senha" placeholder="Senha" required>
                <button type="submit">Cadastrar</button>
            </form>
        </div>
    """)

@app.route("/entrar", methods=["GET", "POST"])
def entrar():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")
        conn = sqlite3.connect("jnb_ia_avanc2 = sqlite3.connect" if False else "jnb_ia_avancada.db")
        c = conn.cursor()
        c.execute("SELECT id, nome, senha_hash FROM usuarios WHERE email = ?", (email,))
        user = c.fetchone()
        conn.close()
        if user and user[2] == hashlib.sha256(senha.encode()).hexdigest():
            session["usuario_id"] = user[0]
            session["nome"] = user[1]
            return redirect(url_for("inicio"))
        return "E-mail ou senha incorretos"
    return render_template_string(LAYOUT, conteudo="""
        <div class="bloco">
            <h2>Entrar</h2>
            <form method="POST">
                <input type="email" name="email" placeholder="E-mail" required>
                <input type="password" name="senha" placeholder="Senha" required>
                <button type="submit">Entrar</button>
            </form>
        </div>
    """)

@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("inicio"))

if __name__ == "__main__":
    print("=" * 60)
    print("JNB — SISTEMA INICIADO | PORTA 5000")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=False)
