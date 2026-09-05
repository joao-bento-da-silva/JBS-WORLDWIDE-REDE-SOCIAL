 # ==================================================
# JNB SOCIAL NETWORK — CÓDIGO PROFISSIONAL E MODERNO
# ==================================================

from datetime import datetime
import hashlib
import os
import sqlite3
from flask import Flask, redirect, render_template_string, request, session, url_for

app = Flask(__name__)

# ==============================================
# CONFIGURAÇÕES E CHAVES
# ==============================================
app.secret_key = os.getenv("SECRET_KEY", "chave_secreta_rede_social_jnb_pro_2026")
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 31536000

# ==============================================
# BANCO DE DADOS HÍBRIDO (POSTGRES / SQLITE)
# ==============================================
def get_db():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        try:
            import psycopg2
            import psycopg2.extras
            if database_url.startswith("postgres://"):
                database_url = database_url.replace("postgres://", "postgresql://", 1)
            conn = psycopg2.connect(database_url, cursor_factory=psycopg2.extras.DictCursor)
            return conn, "postgres"
        except Exception as e:
            print(f"Erro Postgres: {e}")

    conn = sqlite3.connect("jnb_rede_social.db")
    conn.row_factory = sqlite3.Row
    return conn, "sqlite"

def init_db():
    conn, db_type = get_db()
    c = conn.cursor()
    pk_auto = "SERIAL PRIMARY KEY" if db_type == "postgres" else "INTEGER PRIMARY KEY AUTOINCREMENT"

    c.execute(f"""CREATE TABLE IF NOT EXISTS usuarios
                 (id {pk_auto}, nome TEXT, username TEXT UNIQUE, email TEXT UNIQUE, 
                  senha_hash TEXT, bio TEXT DEFAULT '', avatar_url TEXT DEFAULT '', data_cadastro TEXT)""")

    c.execute(f"""CREATE TABLE IF NOT EXISTS postagens
                 (id {pk_auto}, usuario_id INTEGER, conteudo TEXT, 
                  imagem_url TEXT DEFAULT '', data_hora TEXT)""")

    c.execute(f"""CREATE TABLE IF NOT EXISTS curtidas
                 (id {pk_auto}, usuario_id INTEGER, post_id INTEGER)""")

    c.execute(f"""CREATE TABLE IF NOT EXISTS comentarios
                 (id {pk_auto}, usuario_id INTEGER, post_id INTEGER, 
                  texto TEXT, data_hora TEXT)""")

    c.execute(f"""CREATE TABLE IF NOT EXISTS seguidores
                 (id {pk_auto}, seguidor_id INTEGER, seguido_id INTEGER)""")

    conn.commit()
    conn.close()

init_db()

def usuario_logado():
    return "usuario_id" in session

# ==============================================
# LAYOUT DASHBOARD / REDE SOCIAL (DESIGN PROFISSIONAL)
# ==============================================
LAYOUT = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JNB Network — Rede Social</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-body: #0b0f19;
            --bg-card: rgba(17, 24, 39, 0.75);
            --bg-card-hover: rgba(31, 41, 55, 0.6);
            --border-color: rgba(255, 255, 255, 0.08);
            --accent-primary: #38bdf8;
            --accent-gradient: linear-gradient(135deg, #0284c7, #38bdf8);
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --input-bg: rgba(15, 23, 42, 0.6);
        }

        * { margin:0; padding:0; box-sizing:border-box; font-family: 'Plus Jakarta Sans', sans-serif; }
        body { background: var(--bg-body); color: var(--text-main); min-height: 100vh; background-image: radial-gradient(circle at 50% 0%, rgba(56, 189, 248, 0.05) 0%, transparent 60%); }

        /* HEADER NAV */
        .header { background: rgba(11, 15, 25, 0.85); backdrop-filter: blur(16px); border-bottom: 1px solid var(--border-color); position: sticky; top: 0; z-index: 100; height: 65px; display: flex; align-items: center; }
        .nav-inner { width: 100%; max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 22px; font-weight: 800; background: linear-gradient(135deg, #ffffff, var(--accent-primary)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-decoration: none; display: flex; align-items: center; gap: 8px; }

        /* MAIN GRID LAYOUT */
        .layout-grid { max-width: 1200px; margin: 25px auto; padding: 0 20px; display: grid; grid-template-columns: 240px 1fr 300px; gap: 25px; }
        @media (max-width: 1024px) { .layout-grid { grid-template-columns: 80px 1fr; } .sidebar-right { display: none; } }
        @media (max-width: 640px) { .layout-grid { grid-template-columns: 1fr; } .sidebar-left { display: none; } }

        /* SIDEBAR LEFT */
        .nav-menu { display: flex; flex-direction: column; gap: 8px; position: sticky; top: 90px; }
        .nav-item { display: flex; align-items: center; gap: 12px; padding: 12px 16px; color: var(--text-muted); text-decoration: none; font-weight: 600; font-size: 15px; border-radius: 12px; transition: all 0.2s; }
        .nav-item:hover, .nav-item.active { background: rgba(56, 189, 248, 0.1); color: var(--accent-primary); }

        /* FEED / MAIN CONTENT */
        .feed-container { max-width: 640px; margin: 0 auto; width: 100%; }
        .card { background: var(--bg-card); backdrop-filter: blur(12px); border: 1px solid var(--border-color); border-radius: 20px; padding: 20px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }

        /* FORMS */
        input, textarea { width: 100%; padding: 14px 16px; margin: 8px 0 14px; background: var(--input-bg); border: 1px solid var(--border-color); border-radius: 12px; color: #fff; font-size: 14px; outline: none; transition: 0.2s; }
        input:focus, textarea:focus { border-color: var(--accent-primary); box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.15); }
        .btn-primary { width: 100%; padding: 12px; background: var(--accent-gradient); color: #fff; font-weight: 700; border: none; border-radius: 12px; cursor: pointer; transition: 0.2s; box-shadow: 0 4px 15px rgba(2, 132, 199, 0.3); }
        .btn-primary:hover { opacity: 0.95; transform: translateY(-1px); }

        /* POST CARD */
        .post-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        .user-info { display: flex; align-items: center; gap: 12px; }
        .avatar { width: 44px; height: 44px; border-radius: 50%; background: linear-gradient(135deg, #1e293b, #0f172a); display: flex; align-items: center; justify-content: center; font-weight: 700; color: var(--accent-primary); border: 1px solid var(--border-color); font-size: 16px; }
        .post-time { font-size: 12px; color: var(--text-muted); }
        .post-content { font-size: 15px; line-height: 1.6; color: #e5e7eb; margin-bottom: 15px; white-space: pre-line; }
        .post-actions { display: flex; gap: 20px; border-top: 1px solid var(--border-color); padding-top: 12px; }
        .action-btn { background: none; border: none; color: var(--text-muted); padding: 6px 12px; font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 6px; cursor: pointer; border-radius: 8px; transition: 0.2s; }
        .action-btn:hover { background: rgba(255, 255, 255, 0.05); color: var(--accent-primary); }

        /* COMENTÁRIOS */
        .comments-section { margin-top: 12px; padding-top: 12px; border-top: 1px dashed var(--border-color); }
        .comment-item { font-size: 13px; margin-bottom: 8px; background: rgba(31, 41, 55, 0.4); padding: 10px 14px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.03); }

        /* SIDEBAR RIGHT WIDGETS */
        .widget { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 20px; padding: 20px; margin-bottom: 20px; }
        .widget-title { font-size: 16px; font-weight: 700; margin-bottom: 14px; color: var(--text-main); }
    </style>
</head>
<body>
    <div class="header">
        <div class="nav-inner">
            <a href="/" class="logo">⚡ JNB Network</a>
            <div>
                {% if session.usuario_id %}
                    <a href="/perfil/{{ session.username }}" style="color:var(--text-main); text-decoration:none; font-weight:600; font-size:14px;">@{{ session.username }}</a>
                {% endif %}
            </div>
        </div>
    </div>

    <div class="layout-grid">
        <!-- SIDEBAR ESQUERDA -->
        <div class="sidebar-left">
            <div class="nav-menu">
                {% if session.usuario_id %}
                    <a href="/" class="nav-item active">🏠 Feed Principal</a>
                    <a href="/perfil/{{ session.username }}" class="nav-item">👤 Meu Perfil</a>
                    <a href="/sair" class="nav-item" style="color: #f87171;">🚪 Sair</a>
                {% else %}
                    <a href="/entrar" class="nav-item">🔑 Entrar</a>
                    <a href="/cadastro" class="nav-item">✨ Criar Conta</a>
                {% endif %}
            </div>
        </div>

        <!-- CONTEÚDO CENTRAL -->
        <div class="feed-container">
            {{ conteudo | safe }}
        </div>

        <!-- SIDEBAR DIREITA -->
        <div class="sidebar-right">
            <div class="widget">
                <div class="widget-title">📌 Sobre a JNB Network</div>
                <p style="font-size: 13px; color: var(--text-muted); line-height: 1.5;">
                    Sua comunidade exclusiva para compartilhamento de conteúdo, ideias e interações em tempo real.
                </p>
            </div>
        </div>
    </div>
</body>
</html>
"""

# ==============================================
# ROTAS E LÓGICA DO FEED E INTERAÇÕES
# ==============================================
@app.route("/", methods=["GET", "POST"])
def feed():
    if not usuario_logado():
        return redirect(url_for("entrar"))

    conn, db_type = get_db()
    c = conn.cursor()
    param = "%s" if db_type == "postgres" else "?"

    if request.method == "POST":
        conteudo_post = request.form.get("conteudo", "").strip()
        imagem_url = request.form.get("imagem_url", "").strip()
        if conteudo_post:
            c.execute(f"INSERT INTO postagens (usuario_id, conteudo, imagem_url, data_hora) VALUES ({param}, {param}, {param}, {param})",
                      (session["usuario_id"], conteudo_post, imagem_url, datetime.now().strftime("%d/%m/%Y %H:%M")))
            conn.commit()

    c.execute("""
        SELECT p.id, p.conteudo, p.imagem_url, p.data_hora, u.nome, u.username,
               (SELECT COUNT(*) FROM curtidas WHERE post_id = p.id) as total_curtidas
        FROM postagens p
        JOIN usuarios u ON p.usuario_id = u.id
        ORDER BY p.id DESC
    """)
    posts = c.fetchall()

    posts_html = ""
    for p in posts:
        c.execute(f"SELECT c.texto, u.username FROM comentarios c JOIN usuarios u ON c.usuario_id = u.id WHERE c.post_id = {param} ORDER BY c.id ASC", (p['id'],))
        comentarios = c.fetchall()

        comentarios_html = "".join([f"<div class='comment-item'><strong>@{cm['username']}</strong> {cm['texto']}</div>" for cm in comentarios])

        posts_html += f"""
        <div class="card">
            <div class="post-header">
                <div class="user-info">
                    <div class="avatar">{p['username'][0].upper()}</div>
                    <div>
                        <a href="/perfil/{p['username']}" style="color:#fff; text-decoration:none; font-weight:700; font-size:15px;">{p['nome']}</a>
                        <div class="post-time">@{p['username']} • {p['data_hora']}</div>
                    </div>
                </div>
            </div>
            <div class="post-content">{p['conteudo']}</div>
            {f'<img src="{p["imagem_url"]}" style="width:100%; border-radius:14px; margin-bottom:15px; border:1px solid var(--border-color);">' if p['imagem_url'] else ''}
            
            <div class="post-actions">
                <form action="/curtir/{p['id']}" method="POST" style="margin:0;">
                    <button type="submit" class="action-btn">❤️ {p['total_curtidas']} Curtidas</button>
                </form>
            </div>

            <div class="comments-section">
                {comentarios_html}
                <form action="/comentar/{p['id']}" method="POST" style="margin-top:10px;">
                    <input type="text" name="texto" placeholder="Escreva um comentário..." style="margin-bottom:8px; padding:10px 14px;" required>
                    <button type="submit" class="btn-primary" style="padding:8px; font-size:12px;">Comentar</button>
                </form>
            </div>
        </div>
        """

    conn.close()

    return render_template_string(LAYOUT, conteudo=f"""
    <div class="card">
        <h3 style="margin-bottom:12px; font-size:16px;">No que você está pensando?</h3>
        <form method="POST">
            <textarea name="conteudo" rows="3" placeholder="Compartilhe novidades, projetos ou ideias com sua rede..." required></textarea>
            <input type="url" name="imagem_url" placeholder="URL da imagem (opcional)">
            <button type="submit" class="btn-primary">Publicar</button>
        </form>
    </div>
    {posts_html if posts_html else '<p style="text-align:center; color:var(--text-muted); padding:30px;">Nenhuma publicação no feed ainda.</p>'}
    """)

@app.route("/curtir/<int:post_id>", methods=["POST"])
def curtir(post_id):
    if not usuario_logado():
        return redirect(url_for("entrar"))

    conn, db_type = get_db()
    c = conn.cursor()
    param = "%s" if db_type == "postgres" else "?"

    c.execute(f"SELECT id FROM curtidas WHERE usuario_id = {param} AND post_id = {param}", (session["usuario_id"], post_id))
    curtida = c.fetchone()

    if curtida:
        c.execute(f"DELETE FROM curtidas WHERE id = {param}", (curtida["id"],))
    else:
        c.execute(f"INSERT INTO curtidas (usuario_id, post_id) VALUES ({param}, {param})", (session["usuario_id"], post_id))

    conn.commit()
    conn.close()
    return redirect(url_for("feed"))

@app.route("/comentar/<int:post_id>", methods=["POST"])
def comentar(post_id):
    if not usuario_logado():
        return redirect(url_for("entrar"))

    texto = request.form.get("texto", "").strip()
    if texto:
        conn, db_type = get_db()
        c = conn.cursor()
        param = "%s" if db_type == "postgres" else "?"
        c.execute(f"INSERT INTO comentarios (usuario_id, post_id, texto, data_hora) VALUES ({param}, {param}, {param}, {param})",
                  (session["usuario_id"], post_id, texto, datetime.now().strftime("%d/%m/%Y %H:%M")))
        conn.commit()
        conn.close()

    return redirect(url_for("feed"))

@app.route("/perfil/<username>")
def perfil(username):
    conn, db_type = get_db()
    c = conn.cursor()
    param = "%s" if db_type == "postgres" else "?"

    c.execute(f"SELECT * FROM usuarios WHERE username = {param}", (username,))
    user = c.fetchone()

    if not user:
        conn.close()
        return "Usuário não encontrado."

    c.execute(f"SELECT COUNT(*) FROM seguidores WHERE seguido_id = {param}", (user["id"],))
    seguidores = c.fetchone()[0]

    c.execute(f"SELECT COUNT(*) FROM seguidores WHERE seguidor_id = {param}", (user["id"],))
    seguindo = c.fetchone()[0]

    c.execute(f"SELECT * FROM postagens WHERE usuario_id = {param} ORDER BY id DESC", (user["id"],))
    posts = c.fetchall()

    conn.close()

    return render_template_string(LAYOUT, conteudo=f"""
    <div class="card" style="text-align:center;">
        <div class="avatar" style="width:80px; height:80px; font-size:32px; margin: 0 auto 15px;">{user['username'][0].upper()}</div>
        <h2>{user['nome']}</h2>
        <p style="color:var(--text-muted); font-size:14px; margin-bottom:12px;">@{user['username']}</p>
        <p style="margin-bottom:20px; font-size:14px;">{user['bio'] if user['bio'] else 'Sem biografia informada.'}</p>
        
        <div style="display:flex; justify-content:center; gap:30px; border-top:1px solid var(--border-color); padding-top:15px;">
            <div><strong>{len(posts)}</strong> <div style="color:var(--text-muted); font-size:12px;">Posts</div></div>
            <div><strong>{seguidores}</strong> <div style="color:var(--text-muted); font-size:12px;">Seguidores</div></div>
            <div><strong>{seguindo}</strong> <div style="color:var(--text-muted); font-size:12px;">Seguindo</div></div>
        </div>
    </div>
    """)

# ==============================================
# AUTENTICAÇÃO E CRIAR CONTA NATIVA
# ==============================================
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome")
        username = request.form.get("username").strip().lower()
        email = request.form.get("email")
        senha = request.form.get("senha")

        conn, db_type = get_db()
        c = conn.cursor()
        param = "%s" if db_type == "postgres" else "?"
        try:
            c.execute(f"INSERT INTO usuarios (nome, username, email, senha_hash, data_cadastro) VALUES ({param}, {param}, {param}, {param}, {param})",
                      (nome, username, email, hashlib.sha256(senha.encode()).hexdigest(), datetime.now().strftime("%d/%m/%Y")))
            conn.commit()
            
            c.execute(f"SELECT id FROM usuarios WHERE username = {param}", (username,))
            user = c.fetchone()
            session["usuario_id"] = user["id"]
            session["username"] = username
            return redirect(url_for("feed"))
        except Exception as e:
            return f"Erro ao realizar cadastro: {str(e)}"
        finally:
            conn.close()

    return render_template_string(LAYOUT, conteudo="""
    <div class="card" style="max-width: 420px; margin: 20px auto;">
        <h2 style="margin-bottom:6px; font-size:22px;">Criar sua Conta</h2>
        <p style="color:var(--text-muted); font-size:13px; margin-bottom:20px;">Cadastre-se para acessar a JNB Network.</p>
        <form method="POST">
            <input type="text" name="nome" placeholder="Nome Completo" required>
            <input type="text" name="username" placeholder="Nome de usuário (@exemplo)" required>
            <input type="email" name="email" placeholder="E-mail" required>
            <input type="password" name="senha" placeholder="Senha" required>
            <button type="submit" class="btn-primary">Criar Conta</button>
        </form>
        <div style="text-align:center; margin-top:15px; font-size:13px; color:var(--text-muted);">
            Já possui uma conta? <a href="/entrar" style="color:var(--accent-primary); text-decoration:none;">Entrar</a>
        </div>
    </div>
    """)

@app.route("/entrar", methods=["GET", "POST"])
def entrar():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        conn, db_type = get_db()
        c = conn.cursor()
        param = "%s" if db_type == "postgres" else "?"
        c.execute(f"SELECT id, username, senha_hash FROM usuarios WHERE email = {param}", (email,))
        user = c.fetchone()
        conn.close()

        if user and user["senha_hash"] == hashlib.sha256(senha.encode()).hexdigest():
            session["usuario_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("feed"))
        return "Dados incorretos."

    return render_template_string(LAYOUT, conteudo="""
    <div class="card" style="max-width: 420px; margin: 20px auto;">
        <h2 style="margin-bottom:6px; font-size:22px;">Acessar a Conta</h2>
        <p style="color:var(--text-muted); font-size:13px; margin-bottom:20px;">Entre com suas credenciais.</p>
        <form method="POST">
            <input type="email" name="email" placeholder="Seu E-mail" required>
            <input type="password" name="senha" placeholder="Sua Senha" required>
            <button type="submit" class="btn-primary">Entrar</button>
        </form>
        <div style="text-align:center; margin-top:15px; font-size:13px; color:var(--text-muted);">
            Não tem uma conta? <a href="/cadastro" style="color:var(--accent-primary); text-decoration:none;">Cadastre-se</a>
        </div>
    </div>
    """)

@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("entrar"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
