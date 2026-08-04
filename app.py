 # ==================================================
# © 2026 JBS TECNOLOGIA — INTELIGÊNCIA EXCLUSIVA JBS
# VERSÃO FINAL: FOTO + VOZ MASCULINA + SEM CONFLITOS
# ==================================================

from flask import Flask, request, render_template_string, jsonify
import os

app = Flask(__name__)
app.secret_key = os.environ.get("CHAVE_JBS", "JBS_INTELIGENCIA_SEGURA_2026")

# ==================== LÓGICA PRINCIPAL ====================
def processar_pergunta(texto_usuario: str) -> str:
    tx = texto_usuario.lower().strip()

    if any(p in tx for p in ["ola", "oi", "bom dia", "boa tarde", "boa noite"]):
        return "Olá! Eu sou a JBS, a inteligência exclusiva da JBS Tecnologia. Estou aqui para ajudar com códigos, projetos, cálculos e organização de documentos. Em que posso colaborar hoje?"

    elif any(p in tx for p in ["codigo", "programa", "python", "flask"]):
        return "Posso criar, corrigir, organizar e explicar códigos em Python, Flask e outras linguagens. Sempre seguindo os seus padrões, mantendo tudo funcional e seguro. Basta me dizer o que precisa."

    elif any(p in tx for p in ["projeto", "elétrico", "automação", "veicular", "engenharia"]):
        return "Posso ajudar a estruturar, detalhar e organizar projetos técnicos, elétricos, de automação, segurança veicular e viabilidade. Transformo a sua ideia em documento organizado e pronto para uso."

    elif any(p in tx for p in ["documento", "declaração", "contrato", "recibo"]):
        return "Posso auxiliar na elaboração, revisão e organização de documentos oficiais, mantendo a formalidade, clareza e os valores de mercado que definimos."

    elif any(p in tx for p in ["mudança", "cálculo", "valor", "metro cúbico", "quilômetro"]):
        return "Posso auxiliar nos cálculos de mudança, valores por região, volume e distância, seguindo a tabela que você definiu."

    elif any(p in tx for p in ["segurança", "dados", "perder", "apagar"]):
        return "Todos os dados ficam armazenados dentro da sua própria hospedagem, com a sua chave de segurança. Nada é enviado para fora, nada é apagado sem a sua ordem. Você tem o controle total."

    else:
        return "Ainda estou aprendendo com você, mas posso ajudar com códigos, projetos técnicos, documentos, cálculos e organização. Basta explicar o que precisa com detalhes que eu ajudo a estruturar."

# ==================== PÁGINA COM FOTO E VOZ AJUSTADA ====================
@app.route("/")
def inicio():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>JBS — INTELIGÊNCIA EXCLUSIVA</title>
        <style>
            *{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI',Arial,sans-serif;}
            body{min-height:100vh;background:linear-gradient(160deg,#020617 0%,#0f172a 40%,#1e293b 100%);color:#e2e8f0;}
            .caixa{max-width:850px;margin:0 auto;padding:40px 20px;text-align:center;}
            .foto-perfil{width:160px;height:160px;border-radius:50%;border:3px solid #84cc16;margin-bottom:15px;object-fit:cover;box-shadow:0 0 25px rgba(132,204,22,0.35);}
            .logo{font-size:48px;font-weight:900;color:#84cc16;margin-bottom:10px;text-shadow:0 0 20px rgba(132,204,22,0.3);}
            .subtitulo{color:#94a3b8;margin-bottom:35px;}
            .area-entrada{background:rgba(30,41,59,0.6);border:1px solid rgba(132,204,22,0.3);padding:25px;border-radius:12px;margin-bottom:25px;text-align:left;}
            textarea{width:100%;padding:14px;border-radius:8px;border:none;background:rgba(15,23,42,0.8);color:white;font-size:16px;min-height:120px;}
            .botoes{display:flex;gap:15px;margin-top:15px;flex-wrap:wrap;justify-content:center;}
            button{padding:12px 28px;border-radius:8px;font-weight:bold;border:none;cursor:pointer;transition:all 0.2s;}
            .btn-enviar{background:#84cc16;color:#020617;}
            .btn-enviar:hover{transform:translateY(-2px);box-shadow:0 0 15px rgba(132,204,22,0.4);}
            .btn-voz{background:rgba(30,41,59,0.8);color:#84cc16;border:1px solid #84cc16;}
            .resposta{margin-top:25px;padding:20px;background:rgba(0,0,0,0.25);border-radius:10px;border-left:3px solid #84cc16;text-align:left;}
        </style>
    </head>
    <body>
        <div class="caixa">
            <!-- FOTO DIRETO NA MESMA PASTA -->
            <img src="criador_jbs.jpg" alt="João Bento da Silva — Criador JBS" class="foto-perfil" onerror="this.style.display='none'">

            <div class="logo">JBS</div>
            <div class="subtitulo">Inteligência Exclusiva JBS Tecnologia</div>

            <div class="area-entrada">
                <p>Escreva o que precisa:</p>
                <textarea id="pergunta" placeholder="Exemplo: crie um código para... / ajude a montar um projeto de..."></textarea>
                <div class="botoes">
                    <button class="btn-enviar" onclick="enviar()">ENVIAR</button>
                    <button class="btn-voz" onclick="falarResposta()">OUVIR RESPOSTA</button>
                </div>
            </div>

            <div class="resposta" id="resposta"></div>
        </div>

        <script>
        let textoResposta = "";

        function enviar(){
            const texto = document.getElementById("pergunta").value.trim();
            if(!texto) return;

            fetch("/responder",{
                method:"POST",
                headers:{"Content-Type":"application/json"},
                body:JSON.stringify({dados:texto})
            })
            .then(res=>res.json())
            .then(retorno=>{
                textoResposta = retorno.resposta;
                document.getElementById("resposta").innerHTML = `<p>${textoResposta}</p>`;
            });
        }

        function falarResposta(){
            if(!textoResposta) return;
            const voz = new SpeechSynthesisUtterance(textoResposta);
            voz.lang = "pt-BR";
            voz.rate = 0.95;
            voz.pitch = 0.85; // TOM MAIS GRAVE E FIRME

            const vozes = window.speechSynthesis.getVoices();
            const vozMasculina = vozes.find(v => 
                v.lang === "pt-BR" && 
                (v.name.toLowerCase().includes("masculino") || 
                 v.name.toLowerCase().includes("homem") ||
                 v.name.toLowerCase().includes("male"))
            );
            if(vozMasculina) voz.voice = vozMasculina;

            speechSynthesis.speak(voz);
        }

        window.speechSynthesis.onvoiceschanged = () => {};
        </script>
    </body>
    </html>
    ''')

@app.route("/responder", methods=["POST"])
def responder():
    dados = request.get_json()
    pergunta = dados.get("dados", "")
    resposta_final = processar_pergunta(pergunta)
    return jsonify({"resposta": resposta_final})

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta, debug=False)
