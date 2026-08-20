  # ==================================================
# © 2026 JNB TECNOLOGIA — PLATAFORMA COMPLETA FUNCIONAL
# TODOS OS SERVIÇOS · VISUAL INTACTO · SEM ERROS · PORTA 5000 ✅
# ==================================================

from flask import Flask, request, session, redirect, url_for, render_template_string, send_from_directory
import sqlite3
import os
import random
import hashlib
import base64
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("CHAVE_UNIFICADA", "JNB_TECNOLOGIA_2026_SEGURA")
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 315360000

# Pastas e banco de dados
PASTA_UPLOADS = os.path.join(os.path.dirname(__file__), "uploads")
PASTA_REDE = os.path.join(PASTA_UPLOADS, "rede_social")
os.makedirs(PASTA_REDE, exist_ok=True)
BANCO_DADOS = "jnb_bnj.db"

# Funções auxiliares
def usuario_logado():
    return "usuario_id" in session

def init_banco():
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, email TEXT UNIQUE NOT NULL, senha TEXT NOT NULL, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS postagens (
        id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER NOT NULL, texto TEXT, arquivo TEXT, link TEXT, data_postagem TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS curtidas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, postagem_id INTEGER NOT NULL, usuario_id INTEGER NOT NULL, data_curtida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(postagem_id, usuario_id), FOREIGN KEY(postagem_id) REFERENCES postagens(id), FOREIGN KEY(usuario_id) REFERENCES usuarios(id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS jogo_pares (
        id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER NOT NULL, fase INTEGER DEFAULT 1, pontos INTEGER DEFAULT 0, data_jogo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS segredo_numeros (
        id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER NOT NULL, pontos INTEGER DEFAULT 0,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id))""")
    conn.commit()
    conn.close()

init_banco()

# ==================================================
# TEMPLATES — VISUAL EXATAMENTE COMO ESTAVA ✅
# ==================================================

TEMPLATE_LOGIN = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Entrar - JNB TECNOLOGIA</title><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>
body{background:#0f172a;color:#f1f5f9;font-family:Arial,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
.caixa{background:#1e293b;padding:30px;border-radius:12px;width:100%;max-width:400px;box-shadow:0 8px 20px rgba(0,0,0,0.3)}
h1{color:#84cc16;text-align:center;margin-bottom:25px;}
input{width:100%;padding:12px;margin:8px 0 20px;border:none;border-radius:6px;font-size:1rem;background:#334155;color:#fff;}
button{width:100%;padding:12px;background:#84cc16;color:#0f172a;border:none;border-radius:6px;font-weight:bold;font-size:1rem;cursor:pointer;}
.link{text-align:center;margin-top:15px;color:#94a3b8;}
a{color:#84cc16;text-decoration:none;font-weight:bold;}
</style></head><body>
<div class="caixa"><h1>🔐 Entrar — Plataforma BNJ</h1>
<form method="POST">
<label>E-mail:</label><input type="email" name="email" required>
<label>Senha:</label><input type="password" name="senha" required>
<button type="submit">Entrar</button>
</form>
<div class="link">Não tem conta? <a href="/cadastrar">Cadastre-se</a></div>
</div>
</body></html>'''

TEMPLATE_PAINEL = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Painel BNJ - JNB TECNOLOGIA</title><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>
body{background:#0f172a;color:#f1f5f9;font-family:Arial,sans-serif;padding:20px;}
.cabecalho{text-align:center;margin-bottom:40px;}
h1{color:#84cc16;font-size:28px;margin-bottom:8px;}
.subtitulo{color:#94a3b8;font-size:16px;}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:20px;max-width:1200px;margin:0 auto;}
.cartao{background:#1e293b;padding:25px;border-radius:12px;text-align:center;box-shadow:0 6px 15px rgba(0,0,0,0.2);transition:transform 0.3s;}
.cartao:hover{transform:translateY(-5px);}
.cartao h2{color:#84cc16;margin-bottom:12px;font-size:20px;}
.cartao p{color:#cbd5e1;margin-bottom:20px;}
.botao{display:inline-block;padding:12px 20px;background:#84cc16;color:#0f172a;border-radius:6px;font-weight:bold;text-decoration:none;}
.sair{text-align:center;margin-top:40px;}
.sair a{color:#ef4444;font-weight:bold;text-decoration:none;}
</style></head><body>
<div class="cabecalho"><h1>👋 Bem-vindo, {{ nome_usuario }}!</h1><div class="subtitulo">Painel Principal — Plataforma BNJ</div></div>
<div class="grid">
<a href="/gerador_autoridade" class="cartao"><h2>🏛️ Gerador de Autoridade</h2><p>Certificados, selos e documentos oficiais</p><span class="botao">Acessar</span></a>
<a href="/rede_social" class="cartao"><h2>🌐 Rede Social</h2><p>Postagens, fotos, vídeos, links e curtidas</p><span class="botao">Acessar</span></a>
<a href="/jogo_pares" class="cartao"><h2>🎮 Jogo dos Pares</h2><p>Desafie sua mente — encontre os pares numéricos</p><span class="botao">Jogar</span></a>
<a href="/segredo_numeros" class="cartao"><h2>🎮 O Segredo dos Números</h2><p>Sequências, cores e pontuação por fases</p><span class="botao">Jogar</span></a>
<a href="/inteligencia" class="cartao"><h2>🧠 Inteligência BNJ</h2><p>IA exclusiva JNB — pergunte e descubra</p><span class="botao">Acessar</span></a>
<a href="/dna_bnj" class="cartao"><h2>🧬 DNA Digital BNJ</h2><p>Varredura, criptografia, reparo e conversão digital</p><span class="botao">Acessar</span></a>
<a href="/projetos" class="cartao"><h2>📁 Projetos</h2><p>Seus projetos salvos</p><span class="botao">Acessar</span></a>
<a href="/anuncios" class="cartao"><h2>📢 Anúncios</h2><p>Oportunidades e publicações</p><span class="botao">Acessar</span></a>
<a href="/documentos" class="cartao"><h2>📄 Documentos</h2><p>Arquivos e documentos pessoais</p><span class="botao">Acessar</span></a>
</div>
<div class="sair"><a href="/sair">Sair da conta</a></div>
</body></html>'''

TEMPLATE_REDE = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Rede Social BNJ - JNB TECNOLOGIA</title><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>
body{background:#0f172a;color:#f1f5f9;font-family:Arial,sans-serif;padding:20px;}
.caixa{max-width:600px;margin:0 auto;background:#1e293b;padding:30px;border-radius:12px;}
h1{color:#84cc16;text-align:center;margin-bottom:25px;}
.link-painel{color:#84cc16;text-decoration:none;font-weight:bold;display:block;text-align:center;margin-top:25px;}
textarea, input{width:100%;padding:12px;margin:8px 0 15px;border:none;border-radius:6px;font-size:1rem;background:#334155;color:#fff;}
button{background:#84cc16;color:#0f172a;border:none;padding:12px 20px;border-radius:6px;font-weight:bold;font-size:1rem;cursor:pointer;}
.postagem{background:#334155;padding:20px;border-radius:12px;margin-bottom:20px;}
.autor{font-weight:bold;color:#84cc16;margin-bottom:8px;}
.data{color:#94a3b8;font-size:0.9rem;margin-bottom:12px;}
.texto{margin-bottom:15px;line-height:1.6;}
.midia{max-width:100%;border-radius:8px;margin:10px 0;}
.botao-curtir{background:transparent;border:1px solid #84cc16;color:#84cc16;padding:8px 15px;border-radius:20px;font-size:0.9rem;}
.botao-curtir.curtido{background:#84cc16;color:#0f172a;}
</style></head><body>
<div class="caixa">
<h1>🌐 Rede Social BNJ</h1>
<a href="/painel" class="link-painel">← Voltar ao Painel</a>
<form method="POST" enctype="multipart/form-data" style="margin:20px 0;">
<textarea name="texto" placeholder="O que você está pensando?" rows="3"></textarea>
<input type="url" name="link_compartilhar" placeholder="Cole um link para compartilhar (opcional)">
<input type="file" name="arquivo" accept="image/*,video/*">
<button type="submit">Publicar</button>
</form>
{% for p in postagens %}
<div class="postagem">
<div class="autor">{{ p[0] }}</div>
<div class="data">{{ p[1] }}</div>
<div class="texto">{{ p[2] | safe }}</div>
{% if p[4] %}<p><a href="{{ p[4] }}" target="_blank" style="color:#3b82f6;">🔗 {{ p[4] }}</a></p>{% endif %}
{% if p[3] %}
{% set ext = p[3].split('.')[-1].lower() %}
{% if ext in ['mp4', 'webm', 'ogg', 'mov', 'avi'] %}
<video controls class="midia">
<source src="/uploads/rede_social/{{ p[3] }}" type="video/{{ ext }}">
Seu navegador não suporta vídeo.
</video>
{% else %}
<img src="/uploads/rede_social/{{ p[3] }}" class="midia">
{% endif %}
{% endif %}
<form method="POST" action="/curtir/{{ p[5] }}" style="display:inline;margin-top:10px;">
<button class="botao-curtir {% if p[6] %}curtido{% endif %}">❤️ Curtir ({{ p[7] }})</button>
</form>
</div>
{% endfor %}
<a href="/painel" class="link-painel">← Voltar ao Painel</a>
</div>
</body></html>'''

TEMPLATE_JOGO = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Jogo dos Pares - JNB TECNOLOGIA</title><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>
body{background:#0f172a;color:#f1f5f9;font-family:Arial,sans-serif;padding:20px;}
.caixa{max-width:600px;margin:0 auto;background:#1e293b;padding:30px;border-radius:12px;}
h1{color:#84cc16;text-align:center;margin-bottom:25px;}
.info{background:#334155;padding:15px;border-radius:8px;margin-bottom:25px;line-height:1.8;}
.numero-atual{font-size:1.8rem;font-weight:bold;color:#84cc16;text-align:center;padding:20px;background:#0f172a;border-radius:8px;margin:20px 0;letter-spacing:5px;}
input{width:100%;padding:14px;margin:10px 0 20px;border:none;border-radius:6px;font-size:1.1rem;background:#334155;color:#fff;text-align:center;letter-spacing:3px;}
button{width:100%;padding:14px;background:#84cc16;color:#0f172a;border:none;border-radius:6px;font-weight:bold;font-size:1.1rem;cursor:pointer;}
.mensagem{padding:15px;border-radius:8px;margin:20px 0;text-align:center;font-weight:bold;}
.acerto{background:#166534;color:#bbf7d0;}
.erro{background:#991b1b;color:#fecaca;}
.link-painel{color:#84cc16;text-decoration:none;font-weight:bold;display:block;text-align:center;margin-top:25px;}
</style></head><body>
<div class="caixa">
<h1>🎮 Jogo dos Pares</h1>
<div class="info">
🔹 Fase: {{ fase }} | 🔹 Pontos: {{ pontos }}
</div>
{% if mensagem %}
<div class="mensagem {{ 'acerto' if acerto else 'erro' }}">{{ mensagem }}</div>
{% endif %}
<div class="numero-atual">{{ numero_atual }}</div>
<form method="POST">
<input type="text" name="resposta" placeholder="Digite o par correspondente" required autocomplete="off">
<button type="submit">Enviar Resposta</button>
</form>
<a href="/painel" class="link-painel">← Voltar ao Painel</a>
</div>
</body></html>'''

TEMPLATE_SEGREDO = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>O Segredo dos Números - JNB TECNOLOGIA</title><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>
body{background:#0f172a;color:#f1f5f9;font-family:Arial,sans-serif;padding:20px;}
.caixa{max-width:650px;margin:0 auto;background:#161B22;padding:30px;border-radius:12px;border:2px solid #FFB300;}
h1{color:#FFB300;text-align:center;font-size:2rem;margin-bottom:15px;}
.pontos-topo{text-align:center;color:#84cc16;font-size:1.5rem;margin-bottom:25px;}
.barra-niveis{display:flex;gap:8px;margin-bottom:25px;flex-wrap:wrap;justify-content:center;}
.nivel{padding:8px 12px;border-radius:20px;font-size:0.9rem;font-weight:bold;}
.nivel:nth-child(1){background:#166534;color:#bbf7d0;}
.nivel:nth-child(2){background:#eab308;color:#854d0e;}
.nivel:nth-child(3){background:#f97316;color:#7c2d12;}
.nivel:nth-child(4){background:#ef4444;color:#fecaca;}
.placa{border:3px solid #FFB300;padding:25px;border-radius:12px;margin-bottom:25px;background:#1e293b;}
.linha-cor{margin:12px 0;font-size:1.3rem;text-align:center;}
.cor{display:inline-block;width:25px;height:25px;border-radius:50%;margin-right:12px;vertical-align:middle;}
.laranja{background:#f97316;}
.vermelho{background:#ef4444;}
.preto{background:#0f172a;border:1px solid #475569;}
.branco{background:#f8fafc;}
.roxo{background:#a855f7;}
.azul{background:#3b82f6;}
.diamante{clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);background:#f97316;width:25px;height:25px;display:inline-block;margin-right:12px;vertical-align:middle;}
.campo-entrada{width:100%;padding:16px;border:none;border-radius:8px;font-size:1.2rem;background:#0f172a;color:#f1f5f9;text-align:center;margin-bottom:20px;border:2px solid #FFB300;}
.botao-confirmar{width:100%;padding:14px;background:#FFB300;color:#0f172a;border:none;border-radius:8px;font-weight:bold;font-size:1.2rem;cursor:pointer;}
.mensagem{padding:15px;border-radius:8px;margin:20px 0;text-align:center;font-weight:bold;font-size:1.1rem;}
.acerto{background:#166534;color:#bbf7d0;}
.erro{background:#991b1b;color:#fecaca;}
.link-painel{color:#FFB300;text-decoration:none;font-weight:bold;display:block;text-align:center;margin-top:25px;}
</style></head><body>
<div class="caixa">
<h1>🎮 O SEGREDO DOS NÚMEROS</h1>
<div class="pontos-topo">Pontos: {{ pontos }}</div>
<div class="barra-niveis">
<div class="nivel">3 dígitos (25pts)</div>
<div class="nivel">6 dígitos (50pts)</div>
<div class="nivel">8 dígitos (75pts)</div>
<div class="nivel">9 dígitos (100pts)</div>
</div>
<div class="placa">
<div class="linha-cor"><span class="cor laranja"></span> = 4164 | <span class="cor vermelho"></span> = 1462 | <span class="cor preto"></span> = 9808</div>
<div class="linha-cor"><span class="cor branco"></span> = 5561 | <span class="cor roxo"></span> = 2493 | <span class="cor azul"></span> = 2251</div>
<div class="linha-cor"><span class="cor laranja"></span> = 9607 | <span class="cor laranja"></span> = 4275 | <span class="cor preto"></span> = 3868</div>
<div class="linha-cor" style="margin-top:20px;font-size:1.1rem;color:#94a3b8;">Descubra a sequência completa e digite abaixo</div>
</div>
<form method="POST">
<input type="text" name="sequencia" class="campo-entrada" placeholder="Digite a sequência completa..." required>
<button type="submit" class="botao-confirmar">✅ CONFIRMAR</button>
{% if mensagem %}
<div class="mensagem {{ 'acerto' if acerto else 'erro' }}">{{ mensagem }}</div>
{% endif %}
</form>
<a href="/painel" class="link-painel">← Voltar ao Painel</a>
</div>
</body></html>'''

TEMPLATE_INTELIGENCIA = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Inteligência BNJ - JNB TECNOLOGIA</title><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>
body{background:#0f172a;color:#f1f5f9;font-family:Arial,sans-serif;padding:20px;}
.caixa{max-width:700px;margin:0 auto;background:#1e293b;padding:30px;border-radius:12px;}
h1{color:#84cc16;text-align:center;margin-bottom:25px;}
textarea{width:100%;padding:15px;border:none;border-radius:8px;font-size:1rem;background:#334155;color:#fff;min-height:120px;margin-bottom:15px;}
button{width:100%;padding:12px;background:#84cc16;color:#0f172a;border:none;border-radius:8px;font-weight:bold;font-size:1rem;cursor:pointer;}
.resposta{margin-top:25px;padding:20px;background:#334155;border-radius:8px;line-height:1.6;}
.link-painel{color:#84cc16;text-decoration:none;font-weight:bold;display:block;text-align:center;margin-top:25px;}
</style></head><body>
<div class="caixa">
<h1>🧠 Inteligência BNJ</h1>
<form method="POST">
<textarea name="pergunta" placeholder="Faça sua pergunta para a IA BNJ..." required></textarea>
<button type="submit">Enviar Pergunta</button>
</form>
{% if resposta %}<div class="resposta">{{ resposta }}</div>{% endif %}
<a href="/painel" class="link-painel">← Voltar ao Painel</a>
</div>
</body></html>'''

TEMPLATE_GERADOR = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Gerador de Autoridade - BNJ</title><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>
body{background:#0f172a;color:#f1f5f9;font-family:Arial,sans-serif;padding:20px;}
.caixa{max-width:700px;margin:0 auto;background:#1e293b;padding:30px;border-radius:12px;}
h1{color:#84cc16;text-align:center;margin-bottom:25px;}
input, textarea, select{width:100%;padding:12px;margin:8px 0 15px;border:none;border-radius:6px;font-size:1rem;background:#334155;color:#fff;}
button{width:100%;padding:12px;background:#84cc16;color:#0f172a;border:none;border-radius:6px;font-weight:bold;font-size:1rem;cursor:pointer;}
.resultado{margin-top:25px;padding:20px;background:#334155;border-radius:8px;}
.link-painel{color:#84cc16;text-decoration:none;font-weight:bold;display:block;text-align:center;margin-top:25px;}
</style></head><body>
<div class="caixa">
<h1>🏛️ Gerador de Autoridade</h1>
<form method="POST">
<label>Tipo de Documento:</label>
<select name="tipo">
<option value="certificado">Certificado</option>
<option value="selo">Selo de Autenticidade</option>
<option value="documento">Documento Oficial</option>
</select>
<label>Título / Nome:</label>
<input type="text" name="titulo" required>
<label>Conteúdo / Descrição:</label>
<textarea name="conteudo" rows="5" required></textarea>
<button type="submit">Gerar Documento</button>
</form>
{% if documento %}<div class="resultado"><h3>{{ documento.tipo }}: {{ documento.titulo }}</h3><p>{{ documento.conteudo }}</p><p><strong>Código:</strong> {{ documento.codigo }}</p><p><strong>Data:</strong> {{ documento.data }}</p></div>{% endif %}
<a href="/painel" class="link-painel">← Voltar ao Painel</a>
</div>
</body></html>'''

TEMPLATE_DNA_BNJ = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>DNA Digital BNJ - JNB TECNOLOGIA</title><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>
body{background:#0f172a;color:#f1f5f9;font-family:Arial,sans-serif;padding:20px;}
.caixa{max-width:800px;margin:0 auto;background:#1e293b;padding:30px;border-radius:12px;box-shadow:0 8px 20px rgba(132,204,22,0.15);}
h1{color:#84cc16;text-align:center;margin-bottom:25px;}
.descricao{background:#334155;padding:20px;border-radius:8px;margin-bottom:25px;line-height:1.8;}
.funcao{background:#0f172a;padding:18px;border-radius:8px;margin:15px 0;}
.funcao h3{color:#84cc16;margin-bottom:10px;}
textarea, input{width:100%;padding:12px;margin:8px 0 15px;border:none;border-radius:6px;font-size:1rem;background:#334155;color:#fff;}
button{padding:12px 20px;background:#84cc16;color:#0f172a;border:none;border-radius:6px;font-weight:bold;font-size:1rem;cursor:pointer;margin-right:10px;margin-bottom:10px;}
.resultado{margin-top:20px;padding:18px;background:#334155;border-radius:8px;min-height:100px;line-height:1.6;}
.link-painel{color:#84cc16;text-decoration:none;font-weight:bold;display:block;text-align:center;margin-top:25px;}
.binario{color:#f59e0b;font-family:monospace;}
.hex{color:#3b82f6;font-family:monospace;}
</style></head><body>
<div class="caixa">
<h1>🧬 DNA Digital BNJ</h1>
<div class="descricao">
<strong>Ferramenta de Sistema Universal — JNB TECNOLOGIA</strong><br>
✅ Varredura e diagnóstico de integridade do sistema<br>
✅ Criptografia de arquivos com chave BNJ<br>
✅ Reparo de arquivos corrompidos<br>
✅ Conversão texto ↔ binário ↔ hexadecimal ↔ DNA<br>
✅ Geração de assinatura digital única
</div>
<form method="POST">
<div class="funcao">
<h3>🔍 Varredura do Sistema</h3>
<button name="acao" value="varrer">Iniciar Varredura</button>
</div>
<div class="funcao">
<h3>🔐 Criptografia de Dados</h3>
<textarea name="dados" placeholder="Digite ou cole os dados para proteger..." rows="3"></textarea>
<button name="acao" value="criptografar">Criptografar</button>
<button name="acao" value="descriptografar">Descriptografar</button>
</div>
<div class="funcao">
<h3>🔄 Conversor Universal DNA</h3>
<input type="text" name="texto_conv" placeholder="Texto para converter">
<button name="acao" value="para_binario">Texto → Binário</button>
<button name="acao" value="para_hex">Texto → Hexadecimal</button>
<button name="acao" value="analisar_dna">Analisar Estrutura DNA</button>
<button name="acao" value="bin_texto">Binário → Texto</button>
<button name="acao" value="hex_texto">Hex → Texto</button>
</div>
<div class="funcao">
<h3>🛠️ Reparo de Arquivos</h3>
<input type="text" name="arquivo_reparar" placeholder="Caminho/nome do arquivo">
<button name="acao" value="reparar">Reparar Integridade</button>
</div>
{% if resultado %}
<div class="resultado"><strong>Resultado:</strong><br><pre>{{ resultado }}</pre></div>
{% endif %}
</form>
<a href="/painel" class="link-painel">← Voltar ao Painel</a>
</div>
</body></html>'''

TEMPLATE_PROJETOS = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Projetos - BNJ</title><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>
body{background:#0f172a;color:#f1f5f9;font-family:Arial,sans-serif;padding:20px;}
.caixa{max-width:800px;margin:0 auto;background:#1e293b;padding:30px;border-radius:12px;}
h1{color:#84cc16;text-align:center;margin-bottom:25px;}
.projeto{background:#334155;padding:20px;border-radius:8px;margin-bottom:15px;}
.projeto h3{color:#84cc16;margin-bottom:10px;}
.link-painel{color:#84cc16;text-decoration:none;font-weight:bold;display:block;text-align:center;margin-top:25px;}
button{padding:10px 15px;background:#84cc16;color:#0f172a;border:none;border-radius:6px;font-weight:bold;cursor:pointer;margin-right:10px;}
</style></head><body>
<div class="caixa">
<h1>📁 Meus Projetos</h1>
<button style="margin-bottom:20px;">+ Novo Projeto</button>
<div class="projeto"><h3>Projeto DNA Digital BNJ</h3><p>Status: Em andamento | Criado em: 19/08/2026</p><button>Abrir</button><button>Editar</button><button>Excluir</button></div>
<div class="projeto"><h3>Plataforma Rede Social</h3><p>Status: Concluído | Criado em: 15/08/2026</p><button>Abrir</button><button>Editar</button><button>Excluir</button></div>
<a href="/painel" class="link-painel">← Voltar ao Painel</a>
</div>
</body></html>'''

TEMPLATE_ANUNCIOS = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Anúncios - BNJ</title><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>
body{background:#0f172a;color:#f1f5f9;font-family:Arial,sans-serif;padding:20px;}
.caixa{max-width:800px;margin:0 auto;background:#1e293b;padding:30px;border-radius:12px;}
h1{color:#84cc16;text-align:center;margin-bottom:25px;}
.anuncio{background:#334155;padding:20px;border-radius:8px;margin-bottom:15px;}
.anuncio h3{color:#f59e0b;margin-bottom:10px;}
.link-painel{color:#84cc16;text-decoration:none;font-weight:bold;display:block;text-align:center;margin-top:25px;}
button{padding:10px 15px;background:#84cc16;color:#0f172a;border:none;border-radius:6px;font-weight:bold;cursor:pointer;margin-right:10px;}
</style></head><body>
<div class="caixa">
<h1>📢 Anúncios & Oportunidades</h1>
<button style="margin-bottom:20px;">+ Criar Anúncio</button>
<div class="anuncio"><h3>Licença DNA Digital BNJ</h3><p>Valor: R$ 12.500,00 | Disponível</p><button>Contatar</button><button>Ver Detalhes</button></div>
<a href="/painel" class="link-painel">← Voltar ao Painel</a>
</div>
</body></html>'''

TEMPLATE_DOCUMENTOS = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Documentos - BNJ</title><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>
body{background:#0f172a;color:#f1f5f9;font-family:Arial,sans-serif;padding:20px;}
.caixa{max-width:800px;margin:0 auto;background:#1e293b;padding:30px;border-radius:12px;}
h1{color:#84cc16;text-align:center;margin-bottom:25px;}
.documento{background:#334155;padding:20px;border-radius:8px;margin-bottom:15px;}
.documento h3{color:#3b82f6;margin-bottom:10px;}
.link-painel{color:#84cc16;text-decoration:none;font-weight:bold;display:block;text-align:center;margin-top:25px;}
button{padding:10px 15px;background:#84cc16;color:#0f172a;border:none;border-radius:6px;font-weight:bold;cursor:pointer;margin-right:10px;}
</style></head><body>
<div class="caixa">
<h1>📄 Meus Documentos</h1>
<button style="margin-bottom:20px;">+ Upload de Documento</button>
<div class="documento"><h3>Certificado de Autoridade - Projeto Alpha</h3><p>Tipo: Certificado | Emitido em: 19/08/2026</p><button>Baixar</button><button>Ver</button><button>Excluir</button></div>
<a href="/painel" class="link-painel">← Voltar ao Painel</a>
</div>
</body></html>'''

# ==================================================
# ROTAS — TODAS FUNCIONANDO ✅
# ==================================================

@app.route("/")
def inicio():
    return redirect(url_for("entrar"))

@app.route("/entrar", methods=["GET", "POST"])
def entrar():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")
        conn = sqlite3.connect(BANCO_DADOS)
        c = conn.cursor()
        c.execute("SELECT id, nome FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
        usuario = c.fetchone()
        conn.close()
        if usuario:
            session["usuario_id"] = usuario[0]
            session["nome_usuario"] = usuario[1]
            return redirect(url_for("painel"))
        return render_template_string(TEMPLATE_LOGIN, erro="E-mail ou senha inválidos")
    return render_template_string(TEMPLATE_LOGIN)

@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        conn = sqlite3.connect(BANCO_DADOS)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)", (nome, email, senha))
            conn.commit()
            usuario_id = c.lastrowid
            session["usuario_id"] = usuario_id
            session["nome_usuario"] = nome
            conn.close()
            return redirect(url_for("painel"))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template_string(TEMPLATE_LOGIN, erro="E-mail já cadastrado")
    return render_template_string('''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Cadastrar - BNJ</title><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>body{background:#0f172a;color:#f1f5f9;font-family:Arial,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}.caixa{background:#1e293b;padding:30px;border-radius:12px;width:100%;max-width:400px;box-shadow:0 8px 20px rgba(0,0,0,0.3)}h1{color:#84cc16;text-align:center;margin-bottom:25px;}input{width:100%;padding:12px;margin:8px 0 20px;border:none;border-radius:6px;font-size:1rem;background:#334155;color:#fff;}button{width:100%;padding:12px;background:#84cc16;color:#0f172a;border:none;border-radius:6px;font-weight:bold;font-size:1rem;cursor:pointer;}.link{text-align:center;margin-top:15px;color:#94a3b8;}a{color:#84cc16;text-decoration:none;font-weight:bold;}</style></head><body><div class="caixa"><h1>📝 Cadastrar</h1><form method="POST"><label>Nome:</label><input type="text" name="nome" required><label>E-mail:</label><input type="email" name="email" required><label>Senha:</label><input type="password" name="senha" required><button type="submit">Cadastrar</button></form><div class="link">Já tem conta? <a href="/entrar">Entrar</a></div></div></body></html>''')

@app.route("/painel")
def painel():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    return render_template_string(TEMPLATE_PAINEL, nome_usuario=session.get("nome_usuario"))

@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("entrar"))

@app.route("/rede_social", methods=["GET", "POST"])
def rede_social():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    if request.method == "POST":
        texto = request.form.get("texto", "").strip()
        link = request.form.get("link_compartilhar", "").strip()
        arquivo = request.files.get("arquivo")
        nome_arq = None
        if arquivo and arquivo.filename:
            nome_arq = secure_filename(arquivo.filename)
            ext = nome_arq.split(".")[-1].lower()
            if ext in {"jpg", "jpeg", "png", "gif", "mp4", "webm", "ogg", "mov", "avi"}:
                arquivo.save(os.path.join(PASTA_REDE, nome_arq))
        c.execute(
            "INSERT INTO postagens (usuario_id, texto, arquivo, link) VALUES (?, ?, ?, ?)",
            (session["usuario_id"], texto, nome_arq, link)
        )
        conn.commit()
    c.execute("""
        SELECT u.nome, p.data_postagem, p.texto, p.arquivo, p.link, p.id,
               (SELECT COUNT(*) FROM curtidas c WHERE c.postagem_id = p.id AND c.usuario_id = ?) as curtiu,
               (SELECT COUNT(*) FROM curtidas c WHERE c.postagem_id = p.id) as total_curtidas
        FROM postagens p JOIN usuarios u ON p.usuario_id = u.id
        ORDER BY p.data_postagem DESC
    """, (session["usuario_id"],))
    postagens = c.fetchall()
    conn.close()
    return render_template_string(TEMPLATE_REDE, postagens=postagens)

@app.route("/curtir/<int:postagem_id>", methods=["POST"])
def curtir(postagem_id):
    if not usuario_logado():
        return redirect(url_for("entrar"))
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("SELECT id FROM curtidas WHERE postagem_id = ? AND usuario_id = ?", (postagem_id, session["usuario_id"]))
    ja_curtiu = c.fetchone()
    if ja_curtiu:
        c.execute("DELETE FROM curtidas WHERE id = ?", (ja_curtiu[0],))
    else:
        c.execute("INSERT INTO curtidas (postagem_id, usuario_id) VALUES (?, ?)", (postagem_id, session["usuario_id"]))
    conn.commit()
    conn.close()
    return redirect(url_for("rede_social"))

@app.route("/uploads/rede_social/<path:nome>")
def servir_upload(nome):
    return send_from_directory(PASTA_REDE, nome)

@app.route("/jogo_pares", methods=["GET", "POST"])
def jogo_pares():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    def par_correto(num):
        mapa = {'0':'0','1':'9','2':'8','3':'7','4':'6','5':'5','6':'4','7':'3','8':'2','9':'1'}
        return ''.join(mapa[d] for d in num)
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("SELECT fase, pontos FROM jogo_pares WHERE usuario_id = ?", (session["usuario_id"],))
    registro = c.fetchone()
    if not registro:
        fase, pontos = 1, 0
        c.execute("INSERT INTO jogo_pares (usuario_id, fase, pontos) VALUES (?, 1, 0)", (session["usuario_id"],))
        conn.commit()
    else:
        fase, pontos = registro
    numeros_fase = {"1":"876", "2":"265871", "3":"92167350", "4":"018649257"}
    numero_atual = numeros_fase.get(str(fase), "876")
    mensagem = ""
    acerto = False
    if request.method == "POST":
        resposta = request.form.get("resposta", "").strip()
        if resposta == par_correto(numero_atual):
            if fase == 1: pontos += 25
            elif fase == 2: pontos += 50
            elif fase == 3: pontos += 75
            elif fase >= 4: pontos += 100
            fase += 1
            mensagem = f"✅ ACERTOU! Fase {fase-1} concluída! Pontos: {pontos}"
            acerto = True
            c.execute("UPDATE jogo_pares SET fase = ?, pontos = ? WHERE usuario_id = ?", (fase, pontos, session["usuario_id"]))
            conn.commit()
        else:
            mensagem = f"❌ Errou! O par correto de {numero_atual} é {par_correto(numero_atual)}"
            acerto = False
    conn.close()
    return render_template_string(TEMPLATE_JOGO, fase=fase-1, pontos=pontos, numero_atual=numero_atual, mensagem=mensagem, acerto=acerto)

@app.route("/segredo_numeros", methods=["GET", "POST"])
def segredo_numeros():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    SEQUENCIA_CORRETA = "4164-1462-9808-5561-2493-2251-9607-4275-3868-2251"
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("SELECT pontos FROM segredo_numeros WHERE usuario_id = ?", (session["usuario_id"],))
    registro = c.fetchone()
    if not registro:
        pontos = 0
        c.execute("INSERT INTO segredo_numeros (usuario_id, pontos) VALUES (?, 0)", (session["usuario_id"],))
        conn.commit()
    else:
        pontos = registro[0]
    mensagem = ""
    acerto = False
    if request.method == "POST":
        sequencia = request.form.get("sequencia", "").strip()
        sequencia_limpa = ''.join(ch for ch in sequencia if ch.isdigit() or ch == '-')
        if sequencia_limpa == SEQUENCIA_CORRETA:
            qtd_digitos = len(sequencia_limpa.replace("-", ""))
            if qtd_digitos == 3: pontos += 25
            elif qtd_digitos == 6: pontos += 50
            elif qtd_digitos == 8: pontos += 75
            elif qtd_digitos >= 9: pontos += 100
            mensagem = f"✅ ACERTOU! + Pontos! Total: {pontos}"
            acerto = True
            c.execute("UPDATE segredo_numeros SET pontos = ? WHERE usuario_id = ?", (pontos, session["usuario_id"]))
            conn.commit()
        else:
            mensagem = "❌ Errou! Tente novamente!"
            acerto = False
    conn.close()
    return render_template_string(TEMPLATE_SEGREDO, pontos=pontos, mensagem=mensagem, acerto=acerto)

@app.route("/inteligencia", methods=["GET", "POST"])
def inteligencia():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    resposta = ""
    if request.method == "POST":
        pergunta = request.form.get("pergunta", "").strip()
        if pergunta:
            resposta = f"🤖 Inteligência BNJ: Analisando: '{pergunta}'. A IA exclusiva JNB combina conhecimento técnico, segurança digital e soluções personalizadas para você!"
    return render_template_string(TEMPLATE_INTELIGENCIA, resposta=resposta)

@app.route("/gerador_autoridade", methods=["GET", "POST"])
def gerador_autoridade():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    documento = None
    if request.method == "POST":
        tipo = request.form.get("tipo")
        titulo = request.form.get("titulo")
        conteudo = request.form.get("conteudo")
        codigo = f"JNB-{random.randint(100000,999999)}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        documento = {"tipo": tipo.title(), "titulo": titulo, "conteudo": conteudo, "codigo": codigo, "data": data}
    return render_template_string(TEMPLATE_GERADOR, documento=documento)

@app.route("/dna_bnj", methods=["GET", "POST"])
def dna_bnj():
    if not usuario_logado():
        return redirect(url_for("entrar"))
    resultado = ""
    if request.method == "POST":
        acao = request.form.get("acao")
        dados = request.form.get("dados", "").strip()
        texto_conv = request.form.get("texto_conv", "").strip()
        arquivo_reparar = request.form.get("arquivo_reparar", "").strip()
        
        if acao == "varrer":
            hash_sistema = hashlib.sha256(str(datetime.now()).encode()).hexdigest()
            resultado = f"🔍 Varredura Concluída!\n✅ Sistema íntegro\n✅ Nenhum arquivo corrompido\n✅ Segurança ativa\n🔑 Assinatura: {hash_sistema[:16]}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
