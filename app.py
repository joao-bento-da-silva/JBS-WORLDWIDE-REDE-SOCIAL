     <input type="password" name="senha" placeholder="{t["senha"]}" required minlength="6">
    <button>{t["criar_conta"]}</button>
    <a href="/entrar">{t["ja_possui"]}</a>
    <a href="/">Voltar</a>
    </form></div></body></html>
    ''')

# ==================== LOGIN ====================
@app.route("/entrar", methods=["GET","POST"])
def entrar():
    t = IDIOMAS[pegar_idioma()]; msg=request.args.get("msg",""); erro=""
    if request.method == "POST":
        e = request.form["email"].strip().lower()
        s = request.form["senha"].strip()
        conn = conectar()
        u = conn.execute("SELECT id FROM usuarios WHERE email=? AND senha=?", (e,s)).fetchone()
        conn.close()
        if u:
            session["usuario_id"] = u[0]
            return redirect(url_for("feed"))
        erro = t["erro_dados"]
    return render_template_string(f'''
    <html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{t["entrar"]}</title><style>
    *{{margin:0;padding:0;box-sizing:border-box;font-family:Arial}}
    body{{background:linear-gradient(135deg,#020617 0%,#051020 40%,#03141a 100%);color:white;min-height:100vh;display:flex;align-items:center;justify-content:center}}
    .caixa{{width:90%;max-width:480px;background:rgba(8,18,35,0.9);padding:40px;border-radius:18px;border:1px solid rgba(34,197,94,0.25);box-shadow:0 0 50px rgba(59,130,246,0.12)}}
    h2{{text-align:center;color:#22c55e;margin-bottom:28px;font-size:28px}}
    .ok{{background:#166534;color:white;padding:16px;border-radius:12px;margin-bottom:22px;text-align:center;border:1px solid rgba(22,163,74,0.35)}}
    .erro{{background:#b91c1c;color:white;padding:16px;border-radius:12px;margin-bottom:22px;text-align:center;border:1px solid rgba(220,38,38,0.35)}}
    input{{width:100%;padding:16px;margin:12px 0;background:rgba(10,30,55,0.8);border:1px solid rgba(96,165,250,0.3);border-radius:12px;color:white;font-size:17px}}
    button{{width:100%;padding:16px;background:linear-gradient(90deg,#22c55e,#15803d);border:none;border-radius:12px;font-weight:bold;font-size:19px;color:#020617;box-shadow:0 4px 20px rgba(34,197,94,0.35);margin-top:10px}}
    a{{display:block;text-align:center;color:#60a5fa;margin-top:20px;text-decoration:none}}
    </style></head><body><div class="caixa">
    <h2>{t["entrar"]}</h2>
    {f'<div class="ok">{msg}</div>' if msg else ''}
    {f'<div class="erro">{erro}</div>' if erro else ''}
    <form method="POST">
    <input type="email" name="email" placeholder="{t["email"]}" required>
    <input type="password" name="senha" placeholder="Senha" required>
    <button>{t["acessar"]}</button>
    <a href="/cadastrar">{t["nao_possui"]}</a>
    <a href="/">Voltar</a>
    </form></div></body></html>
    ''')

# ==================== FEED ====================
@app.route("/feed", methods=["GET","POST"])
def feed():
    if not logado(): return redirect(url_for("entrar"))
    t = IDIOMAS[pegar_idioma()]
    if request.method == "POST":
        texto = request.form.get("texto","").strip()
        vis = request.form.get("visibilidade","publico")
        faixa = request.form.get("faixa_etaria","todos")
        arq = request.files.get("arquivo")
        nome_arq = tipo_arq = None
        
        if not verificar_conteudo(texto):
            return redirect(url_for("feed", erro=t["erro_conteudo"]))
        
        if arq and arq.filename:
            ext = arq.filename.rsplit(".",1)[1].lower()
            if ext in TIPOS_PERMITIDOS:
                nome_arq = secure_filename(arq.filename)
                arq.save(os.path.join(UPLOAD_FOLDER, nome_arq))
                tipo_arq = ext
        
        conn = conectar()
        conn.execute("INSERT INTO publicacoes VALUES (NULL,?,?,?,?,?, CURRENT_TIMESTAMP)",
                     (session["usuario_id"],texto,vis,faixa,nome_arq,tipo_arq))
        conn.commit()
        conn.close()
        return redirect(url_for("feed"))
    
    conn = conectar()
    pubs = conn.execute('''
        SELECT p.*, u.nome FROM publicacoes p 
        JOIN usuarios u ON p.usuario_id = u.id
        WHERE p.visibilidade = 'publico' OR p.usuario_id = ?
        ORDER BY p.data_publicacao DESC
    ''', (session["usuario_id"],)).fetchall()
    conn.close()
    
    html_pubs = ""
    for p in pubs:
        html_pubs += f"<div style='background:rgba(8,18,35,0.9);padding:22px;border-radius:16px;margin-bottom:22px;border:1px solid rgba(96,165,250,0.25);box-shadow:0 2px 15px rgba(0,0,0,0.3)'>"
        html_pubs += f"<strong style='color:#22c55e;font-size:18px;'>{p[1]}</strong>"
        html_pubs += f"<p style='margin:16px 0;color:#e2e8f0;line-height:1.7;'>{p[2] if p[2] else ''}</p>"
        if p[5]:
            if p[6] in ["png","jpg","jpeg","gif","webp"]:
                html_pubs += f"<img src='/midia/{p[5]}' style='max-width:100%;border-radius:12px;margin:12px 0;'>"
            else:
                html_pubs += f"<video controls src='/midia/{p[5]}' style='max-width:100%;border-radius:12px;margin:12px 0;'></video>"
        html_pubs += f"<br><small style='color:#94a3b8;'>Quem ve: {p[3]} | Faixa etaria: {p[4]}</small></div>"
    
    return render_template_string(f'''
    <html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Feed — JBS WORLDWIDE</title><style>
    *{{margin:0;padding:0;box-sizing:border-box;font-family:Arial}}
    body{{background:linear-gradient(135deg,#020617 0%,#051020 40%,#03141a 100%);color:white;padding:25px;max-width:780px;margin:0 auto}}
    .topo{{display:flex;justify-content:space-between;align-items:center;padding-bottom:22px;border-bottom:1px solid rgba(34,197,94,0.25)}}
    .topo h1{{color:#22c55e;font-size:26px}}
    .sair{{color:#ef4444;text-decoration:none;font-weight:bold;font-size:17px}}
    .form{{background:rgba(8,18,35,0.9);padding:22px;border-radius:16px;margin:28px 0;border:1px solid rgba(34,197,94,0.25)}}
    textarea, select, input{{width:100%;padding:14px;margin:10px 0;background:rgba(10,30,55,0.8);border:1px solid rgba(96,165,250,0.3);border-radius:10px;color:white;font-size:16px}}
    button{{padding:14px 28px;background:linear-gradient(90deg,#22c55e,#15803d);border:none;border-radius:10px;font-weight:bold;font-size:17px;color:#020617;box-shadow:0 4px 15px rgba(34,197,94,0.35)}}
    </style></head><body>
    <div class="topo"><h1>JBS WORLDWIDE</h1><a href="/sair" class="sair">{t["sair"]}</a></div>
    <div class="form">
    <form method="POST" enctype="multipart/form-data">
    <textarea name="texto" rows="4" placeholder="{t["o_que_pensa"]}"></textarea>
    <select name="visibilidade">
    {"".join([f"<option value='{v[0]}'>{v[1]}</option>" for v in VISIBILIDADE])}
    </select>
    <select name="faixa_etaria">
    {"".join([f"<option value='{f[0]}'>{f[1]}</option>" for f in FAIXA_ETARIA])}
    </select>
    <input type="file" name="arquivo" accept="image/*,video/*">
    <button type="submit">{t["publicar"]}</button>
    </form></div>
    {html_pubs}
    </body></html>
    ''')

@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("inicio"))

@app.route("/midia/<nome>")
def midia(nome):
    return send_from_directory(UPLOAD_FOLDER, nome)

if __name__ == "__main__":
    app.run(debug=False)
