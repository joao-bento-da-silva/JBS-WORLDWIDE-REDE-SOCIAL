 # ==================================================
# © 2026 JNB TECNOLOGIA — CHAVE FIXA + USUÁRIO ÚNICO
# PORTA 5000 ✅ CADA UM COM SUA CHAVE ✅ NUNCA MUDA ✅
# REDE · JOGOS · IA · DNA — TUDO FUNCIONAL ✅
# ==================================================

from flask import Flask, request, session, redirect, url_for, render_template_string, send_from_directory, make_response
import sqlite3
import os
import random
import hashlib
import base64
from datetime import datetime
from werkzeug.utils import secure_filename

# 🔑 CHAVE MESTRA — FIXA, NUNCA MUDA. NÃO ALTERAR!
CHAVE_MESTRA = "JNB_TECNOLOGIA_2026_FIXA_NAO_MUDA_1234567890"

app = Flask(__name__)
app.secret_key = CHAVE_MESTRA
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 315360000

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4", "mov", "avi", "webm", "bnj"}
BANCO_DADOS = "jnb_dados.db"

def init_db():
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha_hash TEXT NOT NULL,
        chave_usuario TEXT NOT NULL,
        pontos INTEGER DEFAULT 0,
        data_cadastro TEXT NOT NULL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS postagens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        texto TEXT,
        arquivo TEXT,
        data_postagem TEXT NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS curtidas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        postagem_id INTEGER NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (postagem_id) REFERENCES postagens(id),
        UNIQUE(usuario_id, postagem_id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS ia_conhecimento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pergunta TEXT NOT NULL,
        resposta TEXT NOT NULL,
        data_criado TEXT NOT NULL
    )""")
    conn.commit()
    conn.close()

init_db()

def gerar_chave_usuario():
    return base64.b64encode(os.urandom(32)).decode('utf-8')

def usuario_logado():
    return 'usuario_id' in session

def responder_ia(pergunta):
    p = pergunta.lower().strip()
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("SELECT resposta FROM ia_conhecimento WHERE pergunta LIKE ?", (f"%{p}%",))
    r = c.fetchone()
    conn.close()
    if r: return r[0]
    respostas = {
        "brasil": "O Brasil foi descoberto em 22 de abril de 1500 por Pedro Álvares Cabral.",
        "jogo cartas": "🃏 Y=Y, A=Z, Z=A, B=X, X=B, C=G, G=C, D=F, F=D, E=E",
        "jogo numeros": "🎮 0=0, 1=9, 2=8, 3=7, 4=6, 5=5, 6=4, 7=3, 8=2, 9=1",
        "cadastro": "✅ Seu cadastro é permanente, seus dados ficam para sempre."
    }
    for k, v in respostas.items():
        if k in p: return v
    return "Não sei essa ainda. Vou aprendendo com o tempo!"

@app.route("/")
def inicio():
    if usuario_logado(): return redirect(url_for("plataforma"))
    return render_template_string('''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>JNB TECNOLOGIA</title>
<style>*{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif;}
body{background:linear-gradient(180deg,#0f172a,#1e293b);color:#e2e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center;}
.caixa{background:rgba(15,23,42,0.8);padding:40px;border-radius:12px;border:1px solid #f59e0b;width:90%;max-width:400px;}
h1{color:#f59e0b;text-align:center;margin-bottom:30px;}
input{width:100%;padding:12px;margin:8px 0;background:#020617;border:1px solid #334155;color:white;border-radius:6px;}
button{width:100%;padding:12px;background:#f59e0b;color:#1e1b16;border:none;border-radius:6px;font-weight:bold;cursor:pointer;}
.link{text-align:center;margin-top:15px;font-size:14px;color:#94a3b8;}
.link a{color:#f59e0b;text-decoration:none;}</style></head>
<body><div class="caixa"><h1>JNB TECNOLOGIA</h1>
<form action="/entrar" method="POST"><input type="email" name="email" placeholder="E-mail" required>
<input type="password" name="senha" placeholder="Senha" required><button>Entrar</button></form>
<div class="link">Não tem conta? <a href="/cadastrar">Cadastre-se — Permanente ✅</a></div></div></body></html>''')

@app.route("/cadastrar", methods=["GET","POST"])
def cadastrar():
    if request.method == "POST":
        nome = request.form.get("nome","").strip()
        email = request.form.get("email","").strip()
        senha = request.form.get("senha","").strip()
        if not nome or not email or not senha: return "Preencha tudo", 400
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        chave = gerar_chave_usuario()
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            conn = sqlite3.connect(BANCO_DADOS)
            c = conn.cursor()
            c.execute("INSERT INTO usuarios (nome,email,senha_hash,chave_usuario,data_cadastro) VALUES (?,?,?,?,?)",
                     (nome,email,senha_hash,chave,agora))
            conn.commit()
            conn.close()
            return redirect(url_for("inicio"))
        except: return "E-mail já cadastrado", 400
    return render_template_string('''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Cadastrar</title>
<style>body{background:linear-gradient(180deg,#0f172a,#1e293b);color:#e2e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center;}
.caixa{background:rgba(15,23,42,0.8);padding:40px;border-radius:12px;border:1px solid #f59e0b;width:90%;max-width:400px;}
h1{color:#f59e0b;text-align:center;margin-bottom:30px;}
input{width:100%;padding:12px;margin:8px 0;background:#020617;border:1px solid #334155;color:white;border-radius:6px;}
button{width:100%;padding:12px;background:#f59e0b;color:#1e1b16;border:none;border-radius:6px;font-weight:bold;cursor:pointer;}</style></head>
<body><div class="caixa"><h1>Cadastrar ✅ Permanente</h1>
<form method="POST"><input name="nome" placeholder="Seu nome" required>
<input name="email" placeholder="E-mail" required>
<input type="password" name="senha" placeholder="Senha" required>
<button>Cadastrar</button></form></div></body></html>''')

@app.route("/entrar", methods=["POST"])
def entrar():
    email = request.form.get("email","").strip()
    senha = request.form.get("senha","").strip()
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("SELECT id,nome FROM usuarios WHERE email=? AND senha_hash=?", (email,senha_hash))
    user = c.fetchone()
    conn.close()
    if user:
        session['usuario_id'] = user[0]
        session['nome_usuario'] = user[1]
        return redirect(url_for("plataforma"))
    return "Dados inválidos", 400

@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("inicio"))

@app.route("/uploads/<nome>")
def uploads(nome):
    return send_from_directory(app.config["UPLOAD_FOLDER"], nome)

@app.route("/resposta_ia", methods=["POST"])
def resposta_ia():
    if not usuario_logado(): return redirect(url_for("inicio"))
    pergunta = request.form.get("pergunta","").strip()
    if not pergunta: return "Pergunte algo!"
    return responder_ia(pergunta)

@app.route("/jogo_cartas", methods=["GET","POST"])
def jogo_cartas():
    if not usuario_logado(): return redirect(url_for("inicio"))
    REGRAS = {'Y':'Y','A':'Z','Z':'A','B':'X','X':'B','C':'G','G':'C','D':'F','F':'D','E':'E'}
    if "fase_carta" not in session: session["fase_carta"] = 1
    if "pontos_carta" not in session: session["pontos_carta"] = 0
    fases = [['Y','A','B'],['C','D','E','F','G','X'],['Y','A','B','C','D','E','F','G','X'],['Y','A','B','C','D','E','F','G','X']]
    valores = [100,300,500,1000]
    fase = session["fase_carta"]
    cartas = fases[fase-1]
    if request.method == "POST":
        escolha = request.form.get("carta","")
        alvo = random.choice(cartas)
        correta = REGRAS.get(alvo)
        if escolha == correta:
            session["pontos_carta"] += valores[fase-1]
            if fase < 4: session["fase_carta"] += 1
        else:
            session["fase_carta"] = 1
    return render_template_string('''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>🃏 Jogo das Cartas</title>
<style>body{background:#0f172a;color:white;min-height:100vh;padding:20px;font-family:Arial;}
.carta{display:inline-block;width:80px;height:120px;background:linear-gradient(45deg,#f59e0b,#d97706);border-radius:8px;line-height:120px;text-align:center;font-size:30px;font-weight:bold;margin:10px;cursor:pointer;box-shadow:2px 4px 8px rgba(0,0,0,0.3);}
.carta:hover{transform:scale(1.05);}
.voltar{color:#f59e0b;text-decoration:none;display:inline-block;margin-bottom:20px;}</style></head>
<body><a href="/plataforma" class="voltar">← Voltar</a>
<h1>🃏 Fase {{fase}} — Pontos: {{pontos}}</h1>
<form method="POST">
{% for c in cartas %}<button class="carta" name="carta" value="{{c}}">{{c}}</button>{% endfor %}
</form></body></html>''', fase=fase, pontos=session["pontos_carta"], cartas=cartas)

@app.route("/jogo_numeros", methods=["GET","POST"])
def jogo_numeros():
    if not usuario_logado(): return redirect(url_for("inicio"))
    TABELA = {'0':'0','1':'9','2':'8','3':'7','4':'6','5':'5','6':'4','7':'3','8':'2','9':'1'}
    if "fase_num" not in session: session["fase_num"] = 1
    if "pontos_num" not in session: session["pontos_num"] = 0
    digitos = [3,4,5,6]
    valores = [250000,2500000,25000000,1000000000]
    fase = session["fase_num"]
    if request.method == "POST":
        resposta = request.form.get("resposta","").strip()
        numero = session.get("num_gerado","")
        correta = "".join(TABELA[d] for d in numero)
        if resposta == correta:
            session["pontos_num"] += valores[fase-1]
            if fase < 4: session["fase_num"] += 1
        else:
            session["fase_num"] = 1
        session.pop("num_gerado", None)
    num = "".join(random.choice(list(TABELA.keys())) for _ in range(digitos[fase-1]))
    session["num_gerado"] = num
    return render_template_string('''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>🎮 Jogo dos Números</title>
<style>body{background:#0f172a;color:white;min-height:100vh;padding:20px;font-family:Arial;}
.voltar{color:#f59e0b;text-decoration:none;}</style></head>
<body><a href="/plataforma" class="voltar">← Voltar</a>
<h1>🎮 Fase {{fase}} — Pontos: {{pontos}}</h1>
<h2>Número: {{num}}</h2>
<form method="POST"><input name="resposta" placeholder="Digite o número convertido..." required style="padding:12px;font-size:18px;width:300px;">
<button type="submit" style="padding:12px 24px;background:#f59e0b;color:black;border:none;border-radius:6px;font-weight:bold;margin-left:10px;">Enviar</button>
</form></body></html>''', fase=fase, pontos=session["pontos_num"], num=num)

@app.route("/plataforma", methods=["GET","POST"])
def plataforma():
    if not usuario_logado(): return redirect(url_for("inicio"))
    usuario_id = session['usuario_id']
    nome_usuario = session['nome_usuario']
    
    conn = sqlite3.connect(BANCO_DADOS)
    c = conn.cursor()
    c.execute("SELECT chave_usuario, pontos FROM usuarios WHERE id=?", (usuario_id,))
    dados = c.fetchone()
    chave_usuario = dados[0]
    pontos_totais = dados[1]
    
    if request.method == "POST" and "texto_post" in request.form:
        texto = request.form.get("texto_post","").strip()
        arquivo_nome = None
        if 'arquivo' in request.files:
            arq = request.files['arquivo']
            if arq.filename:
                ext = arq.filename.rsplit('.',1)[-1].lower()
                if ext in ALLOWED_EXTENSIONS:
                    arquivo_nome = secure_filename(f"{usuario_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}")
                    arq.save(os.path.join(app.config["UPLOAD_FOLDER"], arquivo_nome))
        if texto or arquivo_nome:
            c.execute("INSERT INTO postagens (usuario_id,texto,arquivo,data_postagem) VALUES (?,?,?,?)",
                     (usuario_id,texto,arquivo_nome,datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
        return redirect(url_for("plataforma"))
    
    if "curtir" in request.args:
        post_id = request.args.get("curtir")
        try:
            c.execute("INSERT INTO curtidas (usuario_id,postagem_id) VALUES (?,?)", (usuario_id,post_id))
        except:
            c.execute("DELETE FROM curtidas WHERE usuario_id=? AND postagem_id=?", (usuario_id,post_id))
        conn.commit()
        return redirect(url_for("plataforma", _anchor=f"post-{post_id}"))
    
    c.execute("""SELECT p.id,p.texto,p.arquivo,p.data_postagem,u.nome,
       (SELECT COUNT(*) FROM curtidas WHERE postagem_id=p.id) as curtidas
       FROM postagens p JOIN usuarios u ON p.usuario_id=u.id ORDER BY p.data_postagem DESC""")
    posts = c.fetchall()
    conn.close()
    
    posts_html = ""
    for p in posts:
        posts_html += f'''<div id="post-{p[0]}" style="background:#1e293b;padding:15px;border-radius:8px;margin-bottom:15px;">
        <strong style="color:#f59e0b;">{p[4]}</strong> <small style="color:#94a3b8;">{p[3]}</small>
        <p style="margin:10px 0;">{p[1] or ''}</p>
        {f'<img src="/uploads/{p[2]}" style="max-width:100%;border-radius:6px;">' if p[2] and p[2].lower().endswith(('jpg','jpeg','png','gif')) else ''}
        {f'<video controls style="max-width:100%;border-radius:6px;"><source src="/uploads/{p[2]}"></video>' if p[2] and p[2].lower().endswith(('mp4','mov','avi','webm')) else ''}
        <div style="margin-top:10px;"><a href="/plataforma?curtir={p[0]}#post-{p[0]}" style="color:#f59e0b;text-decoration:none;">👍 {p[5]} Curtidas</a></div></div>'''
    
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Plataforma — JNB TECNOLOGIA</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{{background:#0f172a;color:#e2e8f0;min-height:100vh;padding:20px;font-family:Arial,sans-serif;max-width:900px;margin:0 auto;}}
.tabs{{display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap;}}
.tab{{padding:10px 16px;background:#1e293b;border:none;color:white;border-radius:6px;cursor:pointer;}}
.tab.ativo{{background:#f59e0b;color:black;font-weight:bold;}}
.aba{{display:none;}}
.aba.visivel{{display:block;}}
input,textarea{{width:100%;padding:12px;margin:6px 0;background:#1e293b;border:1px solid #475569;color:white;border-radius:6px;}}
button{{padding:10px 20px;background:#f59e0b;color:black;border:none;border-radius:6px;font-weight:bold;cursor:pointer;}}
.cx-chave{{background:#1e293b;padding:10px;border-radius:6px;border-left:3px solid #f59e0b;word-break:break-all;font-family:monospace;color:#fcd34d;}}
</style></head>
<body>
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
<h1 style="color:#f59e0b;">⚡ JNB TECNOLOGIA</h1>
<div><span>Olá, {nome_usuario} | Pontos: {pontos_totais}</span> <a href="/sair" style="color:#f87171;margin-left:10px;">Sair</a></div>
</div>

<div class="tabs">
<button class="tab ativo" onclick="mostrarAba('inicio')">Início</button>
<button class="tab" onclick="mostrarAba('jogos')">🎮 Jogos</button>
<button class="tab" onclick="mostrarAba('ia')">🤖 IA</button>
<button class="tab" onclick="mostrarAba('dna')">🧬 DNA</button>
</div>

<!-- ABA INÍCIO -->
<div id="aba-inicio" class="aba visivel">
<h2>📢 Postar</h2>
<form method="POST" enctype="multipart/form-data">
<textarea name="texto_post" placeholder="Escreva algo..." rows="3"></textarea>
<input type="file" name="arquivo" accept="image/*,video/*">
<button type="submit">📤 Publicar</button>
</form>
<h2 style="margin-top:30px;">📰 Publicações</h2>
{posts_html}
</div>

<!-- ABA JOGOS -->
<div id="aba-jogos" class="aba">
<h2>🎮 Jogos Disponíveis</h2>
<div style="display:grid;gap:15px;">
<a href="/jogo_cartas" style="background:#1e293b;padding:20px;border-radius:8px;text-decoration:none;color:white;"><h3>🃏 Jogo das Cartas</h3><p>Descubra a carta correspondente</p></a>
<a href="/jogo_numeros" style="background:#1e293b;padding:20px;border-radius:8px;text-decoration:none;color:white;"><h3>🎮 Jogo dos Números</h3><p>Decifre o número convertido</p></a>
</div>
</div>

<!-- ABA IA -->
<div id="aba-ia" class="aba">
<h2>🤖 Inteligência</h2>
<div id="caixa-ia" style="background:#1e293b;padding:15px;border-radius:8px;height:300px;overflow-y:auto;margin-bottom:15px;"></div>
<div style="display:flex;gap:8px;">
<input type="text" id="pergunta-ia" placeholder="Pergunte algo..." style="flex:1;">
<button onclick="perguntarIA()">Enviar</button>
</div>
</div>

<!-- ABA DNA -->
<div id="aba-dna" class="aba">
<h2>🧬 DNA — Criptografia Individual</h2>
<p><strong>Sua chave (guarde bem!):</strong></p>
<div class="cx-chave">{chave_usuario}</div>
<p style="margin-top:15px;">Digite o texto para criptografar OU cole o código DNA para decodificar:</p>
<textarea id="dna-entrada" placeholder="Texto ou DNA..." rows="5"></textarea>
<div style="display:flex;gap:10px;margin:10px 0;">
<button onclick="criptoDNA()">🔒 Criptografar</button>
<button onclick="decriptoDNA()">🔓 Decodificar</button>
<button onclick="limparDNA()">🧹 Limpar</button>
</div>
<div id="dna-saida" style="background:#1e293b;padding:15px;border-radius:8px;white-space:pre-wrap;word-break:break-all;display:none;"></div>
</div>

<script>
function mostrarAba(nome){{
    document.querySelectorAll('.aba').forEach(a=>a.classList.remove('visivel'));
    document.querySelectorAll('.tab').forEach(t=>t.classList.remove('ativo'));
    document.getElementById('aba-'+nome).classList.add('visivel');
    event.target.classList.add('ativo');
}}

async function perguntarIA(){{
    const p = document.getElementById('pergunta-ia').value;
    if(!p)return;
    const caixa = document.getElementById('caixa-ia');
    caixa.innerHTML += '<div style="text-align:right;margin:8px 0;"><span style="background:#f59e0b;color:black;padding:6px 10px;border-radius:12px;display:inline-block;max-width:80%;">'+p+'</span></div>';
    document.getElementById('pergunta-ia').value='';
    const r = await fetch('/resposta_ia', {{method:'POST',headers:{{'Content-Type':'application/x-www-form-urlencoded'}},body:'pergunta='+encodeURIComponent(p)}});
    const resp = await r.text();
    caixa.innerHTML += '<div style="text-align:left;margin:8px 0;"><span style="background:#3b82f6;color:white;padding:6px 10px;border-radius:12px;display:inline-block;max-width:80%;">'+resp+'</span></div>';
    caixa.scrollTop = caixa.scrollHeight;
}}

const CHAVE_DNA = "{chave_usuario}";

function textoParaDNA(texto, chave){{
    let dna = '';
    let bitsChave = Array.from(chave).map(c => c.charCodeAt(0) % 2);
    let bitPos = 0;
    for(let i=0;i<texto.length;i++){{
        let bin = texto.charCodeAt(i).toString(2).padStart(8,'0');
        for(let b of bin){{
            let cBit = bitsChave[bitPos % bitsChave.length];
            let bitFinal = (parseInt(b) ^ cBit) ? '1' : '0';
            dna += bitFinal === '1' ? 'GC' : 'AT';
            bitPos++;
        }}
    }}
    return dna;
}}

function DNASobreTexto(dna, chave){{
    if(!dna.includes('AT') && !dna.includes('GC')) return null;
    let bitsChave = Array.from(chave).map(c => c.charCodeAt(0) % 2);
    let bits = '';
    for(let i=0;i<dna.length;i+=2){{
        let par = dna.substr(i,2);
        if(par!=='AT' && par!=='GC') continue;
        let bit = par === 'GC' ? '1' : '0';
        let cBit = bitsChave[Math.floor(i/2) % bitsChave.length];
        bits += (parseInt(bit) ^ cBit) ? '1' : '0';
    }}
    let texto = '';
    for(let i=0;i+8<=bits.length;i+=8){{
        texto += String.fromCharCode(parseInt(bits.substr(i,8),2));
    }}
    return texto;
}}

function criptoDNA(){{
    const t = document.getElementById('dna-entrada').value;
    if(!t)return;
    const dna = textoParaDNA(t, CHAVE_DNA);
    const saida = document.getElementById('dna-saida');
    saida.style.display = 'block';
    saida.textContent = '=== DNA GERADO ===\\n' + dna + '\\n\\nGuarde esse código! Só VOCÊ consegue decodificar.';
}}

function decriptoDNA(){{
    const dna = document.getElementById('dna-entrada').value.replace('JNB-DNA-ENCRYPTED','').trim();
    if(!dna)return;
    const t = DNASobreTexto(dna, CHAVE_DNA);
    const saida = document.getElementById('dna-saida');
    saida.style.display = 'block';
    if(t){{ saida.textContent = '=== TEXTO ORIGINAL ===\\n' + t; }}
    else{{ saida.textContent = '❌ Não foi possível decodificar. Verifique se é o DNA correto e sua conta.'; }}
}}

function limparDNA(){{
    document.getElementById('dna-entrada').value='';
    document.getElementById('dna-saida').style.display='none';
}}
</script>
</body></html>'''

# ==================================================
# 🚀 PORTA 5000 — NO FINAL ✅
# ==================================================
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
