# ======================================
# DNA DIGITAL B.N.J. — VERSÃO FINAL 🔐
# 🏆 PRÊMIO: R$ 1.000.000,00
# REGRAS SECRETAS — NÃO APARECEM NA TELA
# 64 BITS → 18.446.744.073.709.551.616 COMBINAÇÕES
# ======================================

@app.route("/bnj", methods=["GET", "POST"])
def bnj():
    if not usuario_logado():
        return redirect(url_for("entrar"))

    # GERA CÓDIGO NOVO A CADA ACESSO
    if request.method != "POST" or "reiniciar" in request.form:
        import random
        CODIGO_ORIGINAL = ''.join(random.choice(['0','1']) for _ in range(64))
        session["codigo_original"] = CODIGO_ORIGINAL
    else:
        CODIGO_ORIGINAL = session.get("codigo_original", "")

    mensagem = ""
    analise = None

    # CALCULA A CHAVE CORRETA — LER DE TRÁS PRA FRENTE + TROCAR 0↔1
    def gerar_par(cod):
        invertido = cod[::-1]
        par_final = ""
        for b in invertido:
            par_final += "1" if b == "0" else "0"
        return par_final

    CHAVE_CORRETA = gerar_par(CODIGO_ORIGINAL)

    if request.method == "POST" and "sequencia" in request.form:
        resposta = request.form.get("sequencia", "").strip()

        # CONVERSÕES TÉCNICAS
        def converter(bin_str):
            decimal = int(bin_str, 2)
            hex_str = format(decimal, 'X')
            return decimal, hex_str, len(bin_str), len(bin_str)//8

        dec_ori, hex_ori, bits_ori, bytes_ori = converter(CODIGO_ORIGINAL)
        dec_par, hex_par, bits_par, bytes_par = converter(CHAVE_CORRETA)

        if resposta == CHAVE_CORRETA:
            mensagem = "🎉 PARABÉNS! CHAVE DESCOBERTA!\n\n✅ SISTEMA ÍNTEGRO — INTEGRIDADE 100%\n🏆 VOCÊ ACERTOU! PRÊMIO: R$ 1.000.000,00"
            status = "🔒 SEGURO"
            cor_status = "#84cc16"
        else:
            mensagem = "❌ CHAVE INCORRETA\nNão perde nada! Tente de novo."
            status = "⚠️ INVÁLIDA"
            cor_status = "#f87171"

        analise = {
            "status": status,
            "cor_status": cor_status,
            "bits": bits_ori,
            "bytes": bytes_ori,
            "combinacoes": "18.446.744.073.709.551.616",
            "dec_ori": f"{dec_ori:,}",
            "hex_ori": hex_ori,
            "dec_par": f"{dec_par:,}",
            "hex_par": hex_par,
            "megabits": round((bits_ori + bits_par) / 1_000_000, 2)
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
            .painel{{background:#1e293b;border-radius:20px;padding:30px;max-width:850px;margin:0 auto;border:3px solid #22d3ee;box-shadow:0 0 40px #22d3ee30}}
            h1{{text-align:center;color:#ffd700;margin-bottom:5px;font-size:28px}}
            .premio{{text-align:center;color:#ffd700;font-size:22px;font-weight:bold;margin-bottom:15px;
                padding:10px;background:#ffd70015;border-radius:10px;border:2px solid #ffd70040}}
            .sub{{text-align:center;color:#f87171;font-size:13px;margin-bottom:20px}}
            .codigo{{background:#0f172a;padding:18px;border-radius:12px;border:2px solid #475569;
                font-family:monospace;font-size:14px;letter-spacing:2px;color:#84cc16;
                text-align:center;word-break:break-all;line-height:1.8;margin:15px 0}}
            .dica{{background:#334155;padding:12px;border-radius:8px;color:#e2e8f0;text-align:center;margin-bottom:15px}}
            .msg{{padding:18px;border-radius:10px;margin:20px 0;text-align:center;font-weight:bold;white-space:pre-line;font-size:16px;
                background:{'#84cc1620' if '🎉' in mensagem else '#f8717120'};
                color:{'#84cc16' if '🎉' in mensagem else '#f87171'}}}
            input{{width:100%;padding:16px;font-size:14px;font-family:monospace;letter-spacing:1px;
                border-radius:10px;border:2px solid #ffd700;background:#0f172a;color:#f1f5f9;outline:none;text-align:center}}
            button{{padding:14px 24px;font-size:16px;font-weight:bold;border:none;border-radius:10px;cursor:pointer;transition:0.2s}}
            .btn-verificar{{background:linear-gradient(90deg,#ffd700,#f59e0b);color:#000;width:100%;margin-top:12px}}
            .btn-novo{{background:#475569;color:#fff;margin-right:10px}}
            button:hover{{transform:scale(1.02)}}
            .titulo{{color:#22d3ee;font-size:15px;margin:25px 0 10px 0;padding-bottom:8px;border-bottom:1px solid #475569}}
            .linha{{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #334155;font-size:14px}}
            .esq{{color:#94a3b8}}
            .dir{{color:#e2e8f0;font-family:monospace}}
        </style>
    </head>
    <body>
        <div class="painel">
            <h1>🧬 DNA DIGITAL — B.N.J.</h1>

            <div class="premio">🏆 PRÊMIO: R$ 1.000.000,00</div>
            <p class="sub">🔐 64 BITS · 18.446.744.073.709.551.616 COMBINAÇÕES POSSÍVEIS</p>

            <div class="dica">
                Descubra a chave correta e ganhe o prêmio!
                <br>Se errar, não perde nada! Tente de novo!
            </div>

            <div class="codigo">{CODIGO_ORIGINAL}</div>

            <form method="POST">
                <input type="text" name="sequencia" placeholder="Digite a CHAVE CORRETA" required autocomplete="off">
                <button class="btn-verificar" type="submit">🔐 VERIFICAR CHAVE</button>
            </form>

            <form method="POST" style="margin-top:10px;">
                <button class="btn-novo" name="reiniciar" value="1">🔄 Gerar Novo Código</button>
            </form>

            {f'<div class="msg">{mensagem}</div>' if mensagem else ''}

            {f'''
            <div class="titulo">📊 RELATÓRIO TÉCNICO</div>
            <div class="linha"><span class="esq">Status</span><span class="dir" style="color:{analise['cor_status']}">{analise['status']}</span></div>
            <div class="linha"><span class="esq">Tamanho</span><span class="dir">{analise['bits']} bits</span></div>
            <div class="linha"><span class="esq">Combinações</span><span class="dir">{analise['combinacoes']}</span></div>
            ''' if analise else ''}
        </div>
        <div style="text-align:center;margin-top:20px;"><a href="/painel" style="color:#22d3ee;">← Voltar ao Painel</a></div>
    </body>
    </html>
    """
    return render_template_string(html)
 
