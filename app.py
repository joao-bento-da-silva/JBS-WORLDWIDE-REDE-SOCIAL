 # ==================================================
# © 2026 JBS TECNOLOGIA — INTELIGÊNCIA EXCLUSIVA JBS
# VERSÃO PRONTA: FALA E ESCREVE | RESPOSTA POR VOZ
# ==================================================

from flask import Flask, request, render_template_string, jsonify
import os

app = Flask(__name__)
app.secret_key = os.environ.get("CHAVE_JBS", "JBS_INTELIGENCIA_SEGURA_2026")

# ==================== LÓGICA PRINCIPAL ====================
def processar_pergunta(texto_usuario: str) -> str:
    tx = texto_usuario.lower().strip()

    if any(p in tx for p in ["ola", "oi", "bom dia", "boa tarde", "boa noite"]):
        return "Olá! Eu sou a JBS, a inteligência exclusiva da JBS Tecnologia. Estou aqui para ajudar com códigos, projetos, cálculos e documentos. Em que posso colaborar hoje?"
    elif any(p in tx for p in ["codigo", "programa", "python", "flask"]):
        return "Posso criar, corrigir e organizar códigos seguindo os seus padrões, mantendo tudo funcional e seguro."
    elif any(p in tx for p in ["projeto", "elétrico", "automação", "veicular", "engenharia"]):
        return "Posso estruturar e detalhar projetos técnicos, transformando a sua ideia em documento organizado e pronto para uso."
    elif any(p in tx for p in ["documento", "declaração", "contrato", "recibo"]):
        return "Posso auxiliar na elaboração e revisão de documentos oficiais, com clareza e formalidade."
    else:
        return "Ainda estou aprendendo com você, mas posso ajudar com códigos, projetos, cálculos e organização. Basta explicar o que precisa."

# ==================== PÁGINA COMPLETA ====================
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
            *{margin:0;padding:0;box-sizing:border-box;font-family:Arial,sans-serif;}
            body{background:linear-gradient(160deg,#020617 0%,#0f172a 40%,#1e293b 100%);color:#e2e8f0;min-height:100vh;}
            .caixa{max-width:800px;margin:0 auto;padding:40px 20px;text-align:center;}
            .nome{font-size:52px;color:#84cc16;font-weight:900;margin-bottom:5px;text-shadow:0 0 20px rgba(132,204,22,0.3);}
            .sub{color:#94a3b8;margin-bottom:35px;}
            textarea{width:100%;padding:14px;border-radius:8px;border:none;background:rgba(15,23,42,0.8);color:white;min-height:120px;margin-bottom:15px;font-size:16px;}
            .botoes{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;}
            button{padding:12px 25px;border-radius:8px;border:none;font-weight:bold;cursor:pointer;transition:all 0.2s;}
            .btn-falar{background:rgba(220,38,38,0.9);color:white;}
            .btn-enviar{background:#84cc16;color:#020617;}
            .btn-ouvir{background:rgba(30,41,59,0.9);color:#84cc16;border:1px solid #84cc16;}
            .resposta{margin-top:25px;padding:20px;background:rgba(0,0,0,0.25);border-left:3px solid #84cc16;text-align:left;border-radius:8px;}
            .gravando{color:#ef4444;font-weight:bold;margin-top:8px;display:none;}
        </style>
    </head>
    <body>
        <div class="caixa">
            <div class="nome">JBS</div>
            <div class="sub">Inteligência Exclusiva JBS Tecnologia</div>

            <textarea id="campo_texto" placeholder="Escreva ou aperte o botão e fale..."></textarea>
            <div class="gravando" id="aviso_gravando">GRAVANDO... FALE AGORA</div>

            <div class="botoes">
                <button class="btn-falar" id="btn_fala" onclick="iniciarFala()">FALAR COM A JBS</button>
                <button class="btn-enviar" onclick="enviar()">ENVIAR</button>
                <button class="btn-ouvir" onclick="ouvirResposta()">OUVIR RESPOSTA</button>
            </div>

            <div class="resposta" id="resposta"></div>
        </div>

        <script>
        let textoResposta = "";
        let reconhecimento = null;

        if('webkitSpeechRecognition' in window || 'SpeechRecognition' in window){
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            reconhecimento = new SpeechRecognition();
            reconhecimento.continuous = false;
            reconhecimento.lang = "pt-BR";
            reconhecimento.onresult = function(event){
                const falado = event.results[0][0].transcript;
                document.getElementById("campo_texto").value = falado;
            };
            reconhecimento.onstart = function(){
                document.getElementById("aviso_gravando").style.display = "block";
                document.getElementById("btn_fala").disabled = true;
            };
            reconhecimento.onend = function(){
                document.getElementById("aviso_gravando").style.display = "none";
                document.getElementById("btn_fala").disabled = false;
            };
        }

        function iniciarFala(){
            if(!reconhecimento){
                alert("Use o navegador Google Chrome para usar a função de voz.");
                return;
            }
            reconhecimento.start();
        }

        function enviar(){
            const texto = document.getElementById("campo_texto").value.trim();
            if(!texto) return;
            fetch("/resp",{
                method:"POST",
                headers:{"Content-Type":"application/json"},
                body:JSON.stringify({dados:texto})
            })
            .then(r=>r.json())
            .then(dados=>{
                textoResposta = dados.resp;
                document.getElementById("resposta").innerHTML = "<p>"+textoResposta+"</p>";
            });
        }

        function ouvirResposta(){
            if(!textoResposta) return;
            const voz = new SpeechSynthesisUtterance(textoResposta);
            voz.lang = "pt-BR";
            voz.rate = 0.9;
            voz.pitch = 0.8;
            speechSynthesis.speak(voz);
        }
        </script>
    </body>
    </html>
    ''')

@app.route("/resp", methods=["POST"])
def resp():
    dados = request.get_json()
    resposta = processar_pergunta(dados.get("dados", ""))
    return jsonify({"resp": resposta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
