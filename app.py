 # ==================================================
# JNB — PLATAFORMA INTEGRADA DE SERVIÇOS & IA AUTOMÁTICA ✅
# ==================================================

from datetime import datetime
import hashlib
import os
import re
import sqlite3
import unicodedata
from flask import Flask, redirect, render_template_string, request, session, url_for

app = Flask(__name__)

# ==============================================
# CONFIGURAÇÕES E CHAVES
# ==============================================
app.secret_key = os.getenv("SECRET_KEY", "chave_secreta_padrao_jnb_2026")
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 31536000

CHAVE_MESTRA = "21054551774858609435694112838216077829"
PLANO_VALOR = 49.90
PLANO_VALOR_VITALICIO = 897.00
CHAVE_PIX = "769.534.677-20"
NOME_RECEBEDOR = "João Bento da Silva"
EMAIL_DONO = "joasilva19577@gmail.com"

# ==============================================
# LINGUAGEM E INTERPRETADOR JNB
# ==============================================
TABELA_NUMERICA_JNB = {
    "Y": "0", "Z": "1", "X": "2", "A": "3", "B": "4",
    "C": "5", "D": "6", "E": "7", "F": "8", "G": "9"
}

def converter_jnb_para_numero(texto_jnb):
    num_str = ""
    for char in str(texto_jnb).upper():
        if char in TABELA_NUMERICA_JNB:
            num_str += TABELA_NUMERICA_JNB[char]
        else:
            return None
    return int(num_str) if num_str else None

class InterpretadorJNB:
    def __init__(self):
        self.variaveis = {}
        self.saida = []

    def executar(self, codigo_jnb):
        linhas = codigo_jnb.strip().split("\n")
        self.saida = []

        for linha in linhas:
            linha = linha.strip()
            if not linha or linha.startswith("//"):
                continue

            match_def = re.match(r"^DEF\s+([a-zA-Z0-9_]+)\s*=\s*(.+)$", linha, re.IGNORECASE)
            if match_def:
                var_nome, var_valor = match_def.groups()
                self.variaveis[var_nome] = self._avaliar_expressao(var_valor.strip())
                continue

            match_mostre = re.match(r"^MOSTRE\s+(.+)$", linha, re.IGNORECASE)
            if match_mostre:
                exp = match_mostre.group(1).strip()
                res = self._avaliar_expressao(exp)
                self.saida.append(str(res))
                continue

        return "\n".join(self.saida) if self.saida else "Executado com sucesso."

    def _avaliar_expressao(self, exp):
        if (exp.startswith("'") and exp.endswith("'")) or (exp.startswith('"') and exp.endswith('"')):
            return exp[1:-1]

        for var, val in self.variaveis.items():
            exp = re.sub(rf"\b{var}\b", str(val), exp)

        tokens = exp.split()
        for idx, token in enumerate(tokens):
            num_jnb = converter_jnb_para_numero(token)
            if num_jnb is not None:
                tokens[idx] = str(num_jnb)

        exp_convertida = " ".join(tokens)
        try:
            return eval(exp_convertida, {"__builtins__": None}, {"abs": abs, "round": round})
        except Exception:
            return exp_convertida

# ==============================================
# BASE DE CONHECIMENTO INICIAL DA IA
# ==============================================
CONHECIMENTO_INICIAL_JNB = [
    (
        "oi ola bom dia boa tarde boa noite saudaçoes",
        "Atendimento & Início JNB",
        "Olá! Seja bem-vindo à plataforma JNB Tecnologia. Eu sou a Inteligência Artificial nativa do sistema. Como posso te ajudar hoje com nossos projetos de engenharia, fretes, mudanças, passagens aéreas e rodoviárias ou parcerias?",
        "JNB Atendimento"
    ),
    (
        "engenharia automaçao aeronaves veiculos aviao carro projeto eletrica controle embarcado industria fabrica",
        "Engenharia & Automação JNB",
        "A JNB Engenharia desenvolve projetos executivos de controle embarcado, automação industrial, painéis elétricos e sistemas para aeronaves (inclusive UAVs e Drones) e veículos terrestres.",
        "Engenharia JNB"
    ),
    (
        "mudanca frete transporte logistica cotacao peso entrega trajeto valor calculo caminhao ajudantes custo embalagem onibus excursao turismo passagem aviao aereo rodoviario bilhete",
        "Transportes & Passagens JNB",
        "A plataforma JNB facilita a gestão de fretes, mudanças e emissão de passagens aéreas e rodoviárias com tarifa com desconto em relação aos guichês, além de redução burocrática para operadoras.",
        "Logística & Bilhetagem JNB"
    ),
    (
        "socio sociedade investidor investir parceria parceiro cotas cotista franchising apoio apoiador",
        "Seja Sócio / Apoiador JNB",
        "Interessado em se associar à plataforma JNB? Oferecemos modalidade de sócio/investidor e parcerias regionais com direito a participação nas comissões de fretes e bilhetagem.",
        "Expansão JNB"
    ),
    (
        "empresa cadastrar prestador servico eletricista montador pintor guincho cadastro empresas profissional transportador motorista viaçao companhia aerea",
        "Cadastro de Empresas e Companhias",
        "Empresas de transportes, viações, companhias aéreas e profissionais autônomos podem se cadastrar na plataforma sem custos de captação de clientes.",
        "Comercial JNB"
    ),
    (
        "pix pagamento plano valor quanto custa assinatura vitalicio conta taxa comissao",
        "Planos e Taxas JNB",
        "Comissões por serviço: Fretes/Mudanças (12%), Passagens Ônibus/Fretamento (10%), Passagens Aéreas (5%). Plano Pró Mensal: R$ 49,90/mês. Plano Vitalício: R$ 897,00. Chave PIX Oficial: 769.534.677-20 (Favorecido: João Bento da Silva).",
        "Financeiro JNB"
    )
]

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
            print(f"Erro de conexão Postgres: {e}")

    conn = sqlite3.connect("jnb_ia_avancada.db")
    conn.row_factory = sqlite3.Row
    return conn, "sqlite"

def init_db():
    conn, db_type = get_db()
    c = conn.cursor()

    pk_auto = "SERIAL PRIMARY KEY" if db_type == "postgres" else "INTEGER PRIMARY KEY AUTOINCREMENT"

    c.execute(f"""CREATE TABLE IF NOT EXISTS usuarios
                 (id {pk_auto}, nome TEXT, email TEXT UNIQUE, 
                  senha_hash TEXT, data_cadastro TEXT,
                  pago INTEGER DEFAULT 0, data_pagamento TEXT, plano TEXT,
                  ativo INTEGER DEFAULT 1)""")

    c.execute(f"""CREATE TABLE IF NOT EXISTS configuracoes
                 (chave TEXT PRIMARY KEY, valor TEXT)""")

    c.execute(f"""CREATE TABLE IF NOT EXISTS empresas_parceiras
                 (id {pk_auto}, usuario_id INTEGER, razao_social TEXT,
                  cnpj_cpf TEXT, categoria TEXT, telefone TEXT,
                  cidade TEXT, status TEXT DEFAULT 'pendente', data_cadastro TEXT)""")

    c.execute(f"""CREATE TABLE IF NOT EXISTS socios_apoiadores
                 (id {pk_auto}, usuario_id INTEGER, nome_completo TEXT,
                  email TEXT, telefone TEXT, valor_investimento TEXT,
                  mensagem TEXT, status TEXT DEFAULT 'em_analise', data_registro TEXT)""")

    c.execute(f"""CREATE TABLE IF NOT EXISTS orcamentos_mudancas
                 (id {pk_auto}, usuario_id INTEGER, origem TEXT, destino TEXT,
                  distancia_km REAL, peso_kg REAL, ajudantes INTEGER,
                  embalagem TEXT, valor_total REAL, taxa_plataforma REAL, status TEXT DEFAULT 'solicitado', data_hora TEXT)""")

    c.execute(f"""CREATE TABLE IF NOT EXISTS passagens_emitidas
                 (id {pk_auto}, usuario_id INTEGER, modalidade TEXT, origem TEXT, destino TEXT,
                  passageiros INTEGER, data_viagem TEXT, classe TEXT, valor_balcao REAL, valor_jnb REAL,
                  taxa_plataforma REAL, status TEXT DEFAULT 'emitido', data_hora TEXT)""")

    c.execute(f"""CREATE TABLE IF NOT EXISTS pagamentos
                 (id {pk_auto}, usuario_id INTEGER, valor REAL, tipo_plano TEXT,
                  comprovante TEXT, status TEXT DEFAULT 'pendente', data_hora TEXT)""")

    c.execute(f"""CREATE TABLE IF NOT EXISTS documentos
                 (id {pk_auto}, titulo TEXT, conteudo TEXT, 
                  criptografado INTEGER, data_criacao TEXT, usuario_id INTEGER)""")

    c.execute(f"""CREATE TABLE IF NOT EXISTS projetos
                 (id {pk_auto}, nome TEXT, tipo TEXT, 
                  descricao TEXT, codigo_gerado TEXT, viabilidade TEXT, data_criacao TEXT, usuario_id INTEGER)""")

    c.execute(f"""CREATE TABLE IF NOT EXISTS base_conhecimento
                 (id {pk_auto}, palavra_chave TEXT, assunto TEXT, resposta TEXT, fonte TEXT)""")

    c.execute(f"""CREATE TABLE IF NOT EXISTS historico_conversas
                 (id {pk_auto}, usuario_id INTEGER, pergunta TEXT, resposta TEXT, data_hora TEXT)""")

    c.execute(f"""CREATE TABLE IF NOT EXISTS contratos_publicidade
                 (id {pk_auto}, usuario_id INTEGER, empresa_nome TEXT,
                  plano_anuncio TEXT, link_destino TEXT, conteudo_anuncio TEXT,
                  valor REAL, status TEXT DEFAULT 'pendente', data_inicio TEXT)""")

    # Taxas padrão das comissões
    taxas_iniciais = [
        ('TAXA_FRETE', '12.0'),
        ('TAXA_ONIBUS', '10.0'),
        ('TAXA_AEREO', '5.0')
    ]
    param = "%s" if db_type == "postgres" else "?"
    for key, val in taxas_iniciais:
        c.execute(f"SELECT COUNT(*) FROM configuracoes WHERE chave = {param}", (key,))
        res = c.fetchone()
        if res and res[0] == 0:
            c.execute(f"INSERT INTO configuracoes (chave, valor) VALUES ({param}, {param})", (key, val))

    c.execute("SELECT COUNT(*) FROM base_conhecimento")
    count_res = c.fetchone()
    total = count_res[0] if count_res else 0

    if total == 0:
        for item in CONHECIMENTO_INICIAL_JNB:
            c.execute(
                f"INSERT INTO base_conhecimento (palavra_chave, assunto, resposta, fonte) VALUES ({param}, {param}, {param}, {param})",
                item
            )
    
    conn.commit()
    conn.close()

init_db()

# ==============================================
# AUXILIARES E DADOS DINÂMICOS
# ==============================================
def usuario_logado():
    return "usuario_id" in session

def eh_dono():
    if not usuario_logado():
        return False
    conn, db_type = get_db()
    c = conn.cursor()
    param = "%s" if db_type == "postgres" else "?"
    c.execute(f"SELECT email FROM usuarios WHERE id = {param} AND ativo = 1", (session["usuario_id"],))
    res = c.fetchone()
    conn.close()
    return res and res["email"].strip().lower() == EMAIL_DONO.strip().lower()

def obter_taxa_comissao(chave="TAXA_FRETE"):
    conn, db_type = get_db()
    c = conn.cursor()
    param = "%s" if db_type == "postgres" else "?"
    c.execute(f"SELECT valor FROM configuracoes WHERE chave = {param}", (chave,))
    res = c.fetchone()
    conn.close()
    return float(res["valor"]) if res else 10.0

def verificar_transportadoras_disponiveis(categoria="Mudanças"):
    conn, db_type = get_db()
    c = conn.cursor()
    param = "%s" if db_type == "postgres" else "?"
    c.execute(f"SELECT COUNT(*) FROM empresas_parceiras WHERE categoria LIKE {param} AND status = 'aprovada'", (f"%{categoria}%",))
    res = c.fetchone()
    conn.close()
    qtd = res[0] if res else 0
    return qtd > 0

def normalizar_texto(texto):
    texto = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
    texto = re.sub(r'[^\w\s]', '', texto.lower())
    return texto.strip()

# ==============================================
# MOTOR DE IA COM PROCESSAMENTO INTELIGENTE
# ==============================================
def ia_responder_gratuita(pergunta, usuario_id=None):
    texto = pergunta.strip()
    texto_upper = texto.upper()

    if re.search(r'\b(DEF|MOSTRE)\b', texto_upper):
        try:
            interpretador = InterpretadorJNB()
            resultado = interpretador.executar(texto)

            resposta_final = (
                f"💻 **TERMINAL E COMPILADOR JNB**\n\n"
                f"```jnb\n{texto}\n```\n\n"
                f"**Saída / Resultado da Execução:**\n"
                f"```text\n{resultado}\n```"
            )
            return registrar_e_retornar(usuario_id, pergunta, resposta_final)
        except Exception as e:
            resposta_final = f"❌ **[ERRO DE COMPILAÇÃO JNB]**\nFalha ao processar instrução: `{str(e)}`"
            return registrar_e_retornar(usuario_id, pergunta, resposta_final)

    conn, db_type = get_db()
    c = conn.cursor()
    
    pergunta_norm = normalizar_texto(pergunta)
    tokens_usuario = set(pergunta_norm.split())

    c.execute("SELECT assunto, resposta, fonte, palavra_chave FROM base_conhecimento")
    registros = c.fetchall()
    conn.close()

    melhor_resposta = None
    max_pontuacao = 0

    for reg in registros:
        chaves_norm = normalizar_texto(reg["palavra_chave"])
        tokens_chave = set(chaves_norm.split())
        coincidencias = len(tokens_usuario.intersection(tokens_chave))
        
        if coincidencias > max_pontuacao:
            max_pontuacao = coincidencias
            melhor_resposta = reg

    if melhor_resposta and max_pontuacao > 0:
        resposta_final = f"**[{melhor_resposta['assunto']}]**\n{melhor_resposta['resposta']}\n\n_Fonte: {melhor_resposta['fonte']}_"
    else:
        resposta_final = (
            f"**Atendimento Inteligente JNB:**\n"
            f"Entendi sua dúvida sobre '{pergunta}'. Nossos módulos cobrem Engenharia, Fretes, Mudanças, Bilhetagem de Passagens (Aéreas e Ônibus) e Turismo.\n\n"
            f"💡 **Como posso te ajudar melhor?**\n"
            f"• **Solicitar Frete/Mudança:** Acesse 'Mudanças & Fretes'.\n"
            f"• **Comprar Passagens (Aérea/Ônibus):** Acesse 'Passagens & Fretamento'.\n"
            f"• **Seja Sócio/Parceiro:** Acesse 'Seja Sócio / Apoiador'."
        )

    return registrar_e_retornar(usuario_id, pergunta, resposta_final)

def registrar_e_retornar(usuario_id, pergunta, resposta):
    if usuario_id:
        try:
            conn, db_type = get_db()
            c = conn.cursor()
            param = "%s" if db_type == "postgres" else "?"
            c.execute(
                f"INSERT INTO historico_conversas (usuario_id, pergunta, resposta, data_hora) VALUES ({param}, {param}, {param}, {param})",
                (usuario_id, pergunta, resposta, datetime.now().strftime("%d/%m/%Y %H:%M"))
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")
            
    return resposta

def gerar_projeto_engenharia(nome, tipo, descricao):
    codigo_soft = (
        f"// CÓDIGO FONTE AUTOGERADO — JNB TECNOLOGIA\n"
        f"// PROJETO: {nome}\n"
        f"// CATEGORIA: {tipo}\n\n"
        f"DEF status = Z\n"
        f"DEF potencia = CXX\n"
        f"MOSTRE status\n"
        f"MOSTRE potencia"
    )
    viabilidade = (
        f"Análise de Viabilidade Técnica para {nome}:\n"
        f"- Compatibilidade Térmica e Elétrica: OK\n"
        f"- Protocolos de Segurança embarcados: Norma IEC/ISO equivalente\n"
        f"- Custo Estimado de Execução: R$ 4.500,00"
    )
    return codigo_soft, viabilidade

# ==============================================
# LAYOUT MODERNIZADO E ULTRA-PROFISSIONAL
# ==============================================
LAYOUT = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JNB — Tecnologia, Logística & Passagens</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
    
    <style>
        :root {
            --bg-color: #030712;
            --accent-green: #10b981;
            --accent-glow: rgba(16, 185, 129, 0.15);
            --card-bg: rgba(17, 24, 39, 0.6);
            --card-border: rgba(255, 255, 255, 0.08);
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --input-bg: rgba(31, 41, 55, 0.5);
        }

        * { margin:0; padding:0; box-sizing:border-box; font-family: 'Plus Jakarta Sans', sans-serif; }
        body { background: var(--bg-color); color: var(--text-main); min-height: 100vh; overflow-x: hidden; background-image: radial-gradient(circle at 50% 0%, rgba(16, 185, 129, 0.08) 0%, transparent 50%); }

        /* HEADER */
        .cabecalho { text-align:center; padding: 45px 20px 25px; }
        .cabecalho h1 { font-size: 32px; font-weight: 800; letter-spacing: -0.5px; background: linear-gradient(135deg, #ffffff 0%, #a7f3d0 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px; }
        .cabecalho p { color: var(--text-muted); font-size: 15px; font-weight: 400; }

        /* NAVBAR SLIM */
        .nav-container { display:flex; justify-content:center; padding: 0 15px; margin-bottom: 35px; }
        .menu { display:inline-flex; flex-wrap:wrap; gap:6px; padding: 6px; background: rgba(17, 24, 39, 0.8); backdrop-filter: blur(16px); border: 1px solid var(--card-border); border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
        .menu a { color: var(--text-muted); padding: 10px 18px; border-radius: 10px; text-decoration:none; font-size: 14px; font-weight: 600; transition: all 0.2s ease; display:flex; align-items:center; gap:8px; }
        .menu a:hover, .menu a.ativo { background: rgba(255,255,255,0.06); color: #ffffff; }

        /* BADGES */
        .badge-gratis { background: rgba(16, 185, 129, 0.2); color: #34d399; padding: 3px 8px; border-radius: 20px; font-size: 10px; font-weight: 700; text-transform: uppercase; }
        .badge-pago { background: rgba(245, 158, 11, 0.2); color: #fbbf24; padding: 3px 8px; border-radius: 20px; font-size: 10px; font-weight: 700; text-transform: uppercase; }
        .badge-admin { background: rgba(239, 68, 68, 0.2); color: #f87171; padding: 3px 8px; border-radius: 20px; font-size: 10px; font-weight: 700; text-transform: uppercase; }
        .badge-socio { background: rgba(168, 85, 247, 0.2); color: #c084fc; padding: 3px 8px; border-radius: 20px; font-size: 10px; font-weight: 700; text-transform: uppercase; }
        .badge-bus { background: rgba(56, 189, 248, 0.2); color: #38bdf8; padding: 3px 8px; border-radius: 20px; font-size: 10px; font-weight: 700; text-transform: uppercase; }

        /* CONTAINER & BLOCKS */
        .conteudo { max-width: 980px; margin: 0 auto; padding: 0 20px 60px; }
        .bloco { background: var(--card-bg); backdrop-filter: blur(12px); padding: 35px; border-radius: 24px; border: 1px solid var(--card-border); box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4); margin-bottom: 25px; transition: transform 0.2s ease; }
        .bloco h2 { color: #ffffff; font-size: 22px; font-weight: 700; margin-bottom: 12px; letter-spacing: -0.3px; display:flex; align-items:center; gap:10px; }
        .bloco p { color: var(--text-muted); font-size: 15px; margin-bottom: 20px; }

        /* TABELAS MODERNAS */
        table { width:100%; border-collapse:collapse; margin-top:15px; }
        th, td { padding:12px 16px; text-align:left; border-bottom:1px solid var(--card-border); font-size:14px; }
        th { background:rgba(255,255,255,0.03); color:var(--accent-green); font-weight:700; }
        tr:hover { background:rgba(255,255,255,0.02); }

        /* FORMS & INPUTS */
        input, textarea, select { width: 100%; padding: 14px 18px; margin: 8px 0 16px 0; background: var(--input-bg); border: 1px solid var(--card-border); border-radius: 12px; color: #ffffff; font-size: 14px; outline: none; transition: all 0.2s ease; }
        input:focus, textarea:focus, select:focus { border-color: var(--accent-green); box-shadow: 0 0 0 4px var(--accent-glow); background: rgba(31, 41, 55, 0.8); }
        button { width: 100%; padding: 15px; margin-top: 10px; background: linear-gradient(135deg, #10b981, #059669); color: #ffffff; font-weight: 700; font-size: 15px; border: none; border-radius: 12px; cursor: pointer; transition: all 0.2s ease; box-shadow: 0 8px 20px rgba(16, 185, 129, 0.25); }
        button:hover { transform: translateY(-2px); box-shadow: 0 12px 25px rgba(16, 185, 129, 0.35); }

        /* CHAT & RESPONSE */
        .resposta { background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(10px); padding: 25px; border-radius: 16px; margin-top: 25px; border: 1px solid rgba(16, 185, 129, 0.3); box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        .resposta strong { color: var(--accent-green); font-size: 16px; display: block; margin-bottom: 12px; }
        
        pre { background: rgba(3, 7, 18, 0.8) !important; padding: 16px !important; border-radius: 12px !important; border: 1px solid var(--card-border) !important; overflow-x: auto; margin-top: 10px; }
        code { font-family: 'Fira Code', 'Courier New', monospace !important; font-size: 13px; }
    </style>
</head>
<body>
    <div class="cabecalho">
        <h1>JNB Tecnologia, Logística & Passagens</h1>
        <p>Fretes, Mudanças, Passagens Aéreas, Passagens Rodoviárias & Automação</p>
    </div>
    
    <div class="nav-container">
        <div class="menu">
            <a href="/">Início</a>
            <a href="/ia">IA Assistente <span class="badge-gratis">Grátis</span></a>
            <a href="/frete">Mudanças & Fretes</a>
            <a href="/passagens">Passagens & Fretamento <span class="badge-bus">Novos Serviços</span></a>
            <a href="/servicos">Profissionais</a>
            <a href="/anuncie">Anuncie</a>
            <a href="/seja-socio">Seja Sócio <span class="badge-socio">Oportunidade</span></a>
            <a href="/gerar-projeto">Projetos <span class="badge-pago">Pró</span></a>
            <a href="/executar-jnb">Terminal</a>
            {% if session.usuario_id %}
                {% if eh_dono() %}
                    <a href="/admin" style="color:#f87171;">Painel Dono <span class="badge-admin">Admin</span></a>
                {% endif %}
                <a href="/sair" style="color:#ef4444;">Sair</a>
            {% else %}
                <a href="/cadastro">Cadastro</a>
                <a href="/entrar">Entrar</a>
            {% endif %}
        </div>
    </div>

    <div class="conteudo">
        {{ conteudo | safe }}
    </div>

    <script>
      Prism.languages.jnb = {
        'keyword-jnb': /\\b(DEF|MOSTRE)\\b/i,
        'number-jnb': /\\b([0-9]+|[A-Z]{1,2})\\b/,
        'operator-jnb': /[\\+\\-\\*\\/=]/
      };

      document.addEventListener("DOMContentLoaded", function() {
        const resp = document.getElementById('res-area');
        if(resp) {
            resp.innerHTML = marked.parse(resp.getAttribute('data-raw'));
            Prism.highlightAllAllUnder(resp);
        }
      });
    </script>
</body>
</html>
"""

# ==============================================
# ROTAS E APLICAÇÃO
# ==============================================
@app.context_processor
def inject_user_status():
    return dict(eh_dono=eh_dono)

@app.route("/")
def inicio():
    conn, db_type = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM contratos_publicidade WHERE status = 'ativo' ORDER BY id DESC")
    anuncios_vitrine = c.fetchall()
    conn.close()

    anuncios_html = ""
    if anuncios_vitrine:
        anuncios_html = '<div style="margin-top:30px;"><h3 style="color:#38bdf8; font-size:18px; margin-bottom:15px;">📢 Marcas e Ofertas em Destaque</h3><div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap:15px;">'
        for a in anuncios_vitrine:
            anuncios_html += f'''
            <div style="background:rgba(31, 41, 55, 0.4); border:1px solid var(--card-border); padding:20px; border-radius:16px;">
                <span class="badge-pago" style="margin-bottom:8px; display:inline-block;">{a['plano_anuncio']}</span>
                <h4 style="color:#ffffff; font-size:16px; margin-bottom:5px;">{a['empresa_nome']}</h4>
                <p style="color:var(--text-muted); font-size:13px; margin-bottom:12px;">{a['conteudo_anuncio']}</p>
                <a href="{a['link_destino']}" target="_blank" style="color:#10b981; font-weight:700; font-size:13px; text-decoration:none;">Acessar Oferta &rarr;</a>
            </div>
            '''
        anuncios_html += '</div></div>'

    return render_template_string(LAYOUT, conteudo=f"""
    <div class="bloco" style="text-align:center; padding: 50px 30px;">
        <span class="badge-gratis" style="font-size:12px; padding: 6px 16px; margin-bottom: 15px; display:inline-block;">Ecossistema Integrado JNB</span>
        <h2 style="justify-content:center; font-size:32px; margin-bottom: 15px;">Logística, Fretes & Emissão de Passagens Inteligentes</h2>
        <p style="max-width: 750px; margin: 0 auto 30px; line-height: 1.7;">Conectamos mudanças residenciais, fretes comerciais e bilhetagem de passagens aéreas e rodoviárias com descontos diretos no balcão e zero burocracia para operadoras.</p>
        
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px; margin-bottom:30px; text-align:left;">
            <div style="background:rgba(15, 23, 42, 0.6); padding:20px; border-radius:16px; border:1px solid rgba(16, 185, 129, 0.2);">
                <h4 style="color:#10b981; font-size:16px; margin-bottom:8px;">✈️ 🚌 Para Empresas & Operadoras</h4>
                <p style="color:var(--text-muted); font-size:13px; margin:0;">Ocupação de assentos vagos e frota ociosa. Custo zero de marketing e captação; recebimento em custódia garantido.</p>
            </div>
            <div style="background:rgba(15, 23, 42, 0.6); padding:20px; border-radius:16px; border:1px solid rgba(56, 189, 248, 0.2);">
                <h4 style="color:#38bdf8; font-size:16px; margin-bottom:8px;">🎟️ Para Passageiros & Clientes</h4>
                <p style="color:var(--text-muted); font-size:13px; margin:0;">Tarifas de passagens aéreas e de ônibus mais baratas que na bilhetaria oficial, com emissão do e-ticket digital direto no celular.</p>
            </div>
        </div>

        <div style="display:flex; justify-content:center; gap:15px; flex-wrap:wrap;">
            <a href="/frete" style="background:linear-gradient(135deg, #10b981, #059669); color:white; padding: 14px 28px; border-radius:12px; text-decoration:none; font-weight:700; box-shadow:0 10px 20px rgba(16,185,129,0.3);">Cotar Frete ou Mudança</a>
            <a href="/passagens" style="background:linear-gradient(135deg, #0284c7, #0369a1); color:white; padding: 14px 28px; border-radius:12px; text-decoration:none; font-weight:700;">Comprar Passagem Aérea / Ônibus</a>
            <a href="/seja-socio" style="background:rgba(168, 85, 247, 0.2); border:1px solid rgba(168, 85, 247, 0.4); color:#c084fc; padding: 14px 28px; border-radius:12px; text-decoration:none; font-weight:600;">Seja Sócio / Investidor</a>
        </div>
    </div>
    {anuncios_html}
    """)

@app.route("/ia", methods=["GET", "POST"])
def pagina_ia():
    if not usuario_logado():
        return redirect(url_for("entrar"))

    resposta = ""
    if request.method == "POST":
        pergunta = request.form.get("pergunta", "").strip()
        if pergunta:
            resposta = ia_responder_gratuita(pergunta, session.get("usuario_id"))

    return render_template_string(LAYOUT, conteudo=f"""
    <div class="bloco">
        <h2>🤖 Assistente Virtual JNB</h2>
        <p>Pergunte sobre fretes, passagens aéreas/rodoviárias, projetos ou envie comandos na linguagem JNB.</p>
        <form method="POST">
            <textarea name="pergunta" rows="3" placeholder="Digite sua dúvida ou comando..." required></textarea>
            <button type="submit">Enviar Mensagem</button>
        </form>
        {f'<div class="resposta"><strong>Resposta do Assistente:</strong><div id="res-area" data-raw="{resposta}"></div></div>' if resposta else ''}
    </div>
    """)

# ==============================================
# PAINEL DE CONTROLE DO DONO (ADMIN)
# ==============================================
@app.route("/admin", methods=["GET", "POST"])
def painel_admin():
    if not usuario_logado() or not eh_dono():
        return redirect(url_for("inicio"))

    mensagem = ""
    conn, db_type = get_db()
    c = conn.cursor()
    param = "%s" if db_type == "postgres" else "?"

    if request.method == "POST":
        acao = request.form.get("acao")
        if acao == "salvar_taxas":
            taxa_frete = request.form.get("taxa_frete")
            taxa_onibus = request.form.get("taxa_onibus")
            taxa_aereo = request.form.get("taxa_aereo")

            c.execute(f"UPDATE configuracoes SET valor = {param} WHERE chave = 'TAXA_FRETE'", (taxa_frete,))
            c.execute(f"UPDATE configuracoes SET valor = {param} WHERE chave = 'TAXA_ONIBUS'", (taxa_onibus,))
            c.execute(f"UPDATE configuracoes SET valor = {param} WHERE chave = 'TAXA_AEREO'", (taxa_aereo,))
            conn.commit()
            mensagem = "Tabela de comissões atualizada com sucesso!"
        elif acao == "aprovar_empresa":
            empresa_id = request.form.get("empresa_id")
            c.execute(f"UPDATE empresas_parceiras SET status = 'aprovada' WHERE id = {param}", (empresa_id,))
            conn.commit()
            mensagem = "Empresa parceira aprovada!"
        elif acao == "aprovar_anuncio":
            anuncio_id = request.form.get("anuncio_id")
            c.execute(f"UPDATE contratos_publicidade SET status = 'ativo' WHERE id = {param}", (anuncio_id,))
            conn.commit()
            mensagem = "Anúncio aprovado e publicado na vitrine!"

    t_frete = obter_taxa_comissao("TAXA_FRETE")
    t_onibus = obter_taxa_comissao("TAXA_ONIBUS")
    t_aereo = obter_taxa_comissao("TAXA_AEREO")

    c.execute("SELECT * FROM empresas_parceiras ORDER BY id DESC")
    empresas = c.fetchall()

    c.execute("SELECT * FROM contratos_publicidade ORDER BY id DESC")
    anuncios = c.fetchall()

    c.execute("SELECT * FROM socios_apoiadores ORDER BY id DESC")
    socios = c.fetchall()

    conn.close()

    return render_template_string(LAYOUT, conteudo=f"""
    <div class="bloco">
        <h2>⚙️ Painel de Gestão e Controle (Dono da Plataforma)</h2>
        <p>Ajuste percentuais de comissão e aprove parceiros, viações e patrocinadores.</p>
        {f'<p style="background:rgba(16, 185, 129, 0.15); color:#34d399; padding:12px; border-radius:10px; margin-bottom:15px; border:1px solid rgba(16, 185, 129, 0.3);">{mensagem}</p>' if mensagem else ''}

        <div style="background:rgba(15, 23, 42, 0.6); padding:20px; border-radius:16px; margin-bottom:25px; border:1px solid var(--card-border);">
            <h3 style="color:#38bdf8; font-size:18px; margin-bottom:15px;">Tabela de Comissões por Categoria (%)</h3>
            <form method="POST">
                <input type="hidden" name="acao" value="salvar_taxas">
                <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:15px;">
                    <div>
                        <label style="color:var(--text-muted); font-size:12px;">Fretes & Mudanças (%)</label>
                        <input type="number" step="0.5" name="taxa_frete" value="{t_frete}" required>
                    </div>
                    <div>
                        <label style="color:var(--text-muted); font-size:12px;">Passagens Ônibus / Fretamento (%)</label>
                        <input type="number" step="0.5" name="taxa_onibus" value="{t_onibus}" required>
                    </div>
                    <div>
                        <label style="color:var(--text-muted); font-size:12px;">Passagens Aéreas (%)</label>
                        <input type="number" step="0.5" name="taxa_aereo" value="{t_aereo}" required>
                    </div>
                </div>
                <button type="submit" style="margin-top:10px;">Atualizar Tabela de Taxas</button>
            </form>
        </div>

        <h3 style="color:#ffffff; margin:25px 0 10px 0;">Empresas / Viações Cadastradas</h3>
        <table>
            <tr>
                <th>Razão Social / Nome</th>
                <th>CNPJ/CPF</th>
                <th>Categoria</th>
                <th>Telefone</th>
                <th>Status</th>
                <th>Ação</th>
            </tr>
            {''.join([f'''
            <tr>
                <td>{e['razao_social']}</td>
                <td>{e['cnpj_cpf']}</td>
                <td>{e['categoria']}</td>
                <td>{e['telefone']}</td>
                <td><span class="badge-{"gratis" if e['status']=="aprovada" else "pago"}">{e['status']}</span></td>
                <td>
                    {"-" if e['status']=="aprovada" else f'''
                    <form method="POST" style="margin:0;">
                        <input type="hidden" name="acao" value="aprovar_empresa">
                        <input type="hidden" name="empresa_id" value="{e['id']}">
                        <button type="submit" style="padding:6px 12px; font-size:12px; margin:0; background:#10b981;">Aprovar</button>
                    </form>
                    '''}
                </td>
            </tr>
            ''' for e in empresas]) if empresas else '<tr><td colspan="6">Nenhuma empresa parceira cadastrada ainda.</td></tr>'}
        </table>

        <h3 style="color:#ffffff; margin:35px 0 10px 0;">Anúncios Pendentes</h3>
        <table>
            <tr>
                <th>Empresa</th>
                <th>Plano</th>
                <th>Valor</th>
                <th>Status</th>
                <th>Ação</th>
            </tr>
            {''.join([f'''
            <tr>
                <td>{a['empresa_nome']}</td>
                <td>{a['plano_anuncio']}</td>
                <td>R$ {a['valor']:.2f}</td>
                <td><span class="badge-{"gratis" if a['status']=="ativo" else "pago"}">{a['status']}</span></td>
                <td>
                    {"-" if a['status']=="ativo" else f'''
                    <form method="POST" style="margin:0;">
                        <input type="hidden" name="acao" value="aprovar_anuncio">
                        <input type="hidden" name="anuncio_id" value="{a['id']}">
                        <button type="submit" style="padding:6px 12px; font-size:12px; margin:0; background:#10b981;">Aprovar & Publicar</button>
                    </form>
                    '''}
                </td>
            </tr>
            ''' for a in anuncios]) if anuncios else '<tr><td colspan="5">Nenhum anúncio em fila.</td></tr>'}
        </table>

        <h3 style="color:#ffffff; margin:35px 0 10px 0;">Investidores / Sócios Inscritos</h3>
        <table>
            <tr>
                <th>Nome</th>
                <th>Contato</th>
                <th>Investimento</th>
                <th>Mensagem</th>
                <th>Data</th>
            </tr>
            {''.join([f'''
            <tr>
                <td>{s['nome_completo']}</td>
                <td>{s['email']}<br><small>{s['telefone']}</small></td>
                <td><strong style="color:#10b981;">{s['valor_investimento']}</strong></td>
                <td>{s['mensagem']}</td>
                <td>{s['data_registro']}</td>
            </tr>
            ''' for s in socios]) if socios else '<tr><td colspan="5">Nenhuma intenção de sociedade registrada.</td></tr>'}
        </table>

        <div style="margin-top:20px; text-align:right;">
            <a href="/admin/conhecimento" style="color:#38bdf8; font-weight:600; text-decoration:none;">🧠 Gerenciar Conhecimento da IA &rarr;</a>
        </div>
    </div>
    """)

# ==============================================
# MÓDULO DE MUDANÇAS E FRETES
# ==============================================
@app.route("/frete", methods=["GET", "POST"])
def pagina_frete():
    if not usuario_logado():
        return redirect(url_for("entrar"))

    taxa_comissao = obter_taxa_comissao("TAXA_FRETE")
    disponivel = verificar_transportadoras_disponiveis("Mudanças")
    resultado = None
    mensagem_pre = ""

    if request.method == "POST":
        origem = request.form.get("origem")
        destino = request.form.get("destino")
        distancia = float(request.form.get("distancia", 10))
        peso = float(request.form.get("peso", 100))
        ajudantes = int(request.form.get("ajudantes", 1))
        embalagem = request.form.get("embalagem", "Sem Embalagem")

        custo_km = distancia * 3.50
        custo_mao_obra = ajudantes * 120.00
        taxa_partida = 200.00
        custo_peso = (peso / 100) * 15.00
        custo_embalagem = 180.00 if embalagem == "Com Embalagem Completa" else 0.0

        valor_bruto = taxa_partida + custo_km + custo_mao_obra + custo_peso + custo_embalagem
        valor_comissao = valor_bruto * (taxa_comissao / 100.0)

        conn, db_type = get_db()
        c = conn.cursor()
        param = "%s" if db_type == "postgres" else "?"
        c.execute(f"""INSERT INTO orcamentos_mudancas 
                     (usuario_id, origem, destino, distancia_km, peso_kg, ajudantes, embalagem, valor_total, taxa_plataforma, data_hora)
                     VALUES ({param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param})""",
                  (session["usuario_id"], origem, destino, distancia, peso, ajudantes, embalagem, valor_bruto, valor_comissao, datetime.now().strftime("%d/%m/%Y %H:%M")))
        conn.commit()
        conn.close()

        if disponivel:
            resultado = {
                "origem": origem,
                "destino": destino,
                "distancia": distancia,
                "ajudantes": ajudantes,
                "embalagem": embalagem,
                "valor_total": valor_bruto
            }
        else:
            mensagem_pre = "Sua solicitação de frete foi recebida! Nossas transportadoras parceiras homologadas entrarão em contato em breve para confirmar a alocação do caminhão."

    return render_template_string(LAYOUT, conteudo=f"""
    <div class="bloco">
        <h2>🚚 Cotação Inteligente de Mudanças & Fretes</h2>
        <p>Serviço sem burocracia comercial para o motorista e pagamento em custódia segura para o contratante.</p>

        {f'<p style="background:rgba(16, 185, 129, 0.15); color:#34d399; padding:12px; border-radius:10px; margin-bottom:15px; border:1px solid rgba(16, 185, 129, 0.3);">{mensagem_pre}</p>' if mensagem_pre else ''}

        <form method="POST">
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                <div>
                    <label style="color:var(--text-muted); font-size:12px;">Origem</label>
                    <input type="text" name="origem" placeholder="Cidade / Bairro de Origem" required>
                </div>
                <div>
                    <label style="color:var(--text-muted); font-size:12px;">Destino</label>
                    <input type="text" name="destino" placeholder="Cidade / Bairro de Destino" required>
                </div>
            </div>
            
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                <div>
                    <label style="color:var(--text-muted); font-size:12px;">Distância Aprox. (km)</label>
                    <input type="number" name="distancia" value="25" required>
                </div>
                <div>
                    <label style="color:var(--text-muted); font-size:12px;">Peso Aprox. (kg)</label>
                    <input type="number" name="peso" value="150" required>
                </div>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                <div>
                    <label style="color:var(--text-muted); font-size:12px;">Ajudantes</label>
                    <select name="ajudantes">
                        <option value="1">1 Ajudante</option>
                        <option value="2" selected>2 Ajudantes</option>
                        <option value="3">3 Ajudantes</option>
                    </select>
                </div>
                <div>
                    <label style="color:var(--text-muted); font-size:12px;">Embalagem</label>
                    <select name="embalagem">
                        <option value="Sem Embalagem">Sem Embalagem</option>
                        <option value="Com Embalagem Completa">Com Embalagem Completa</option>
                    </select>
                </div>
            </div>

            <button type="submit">Calcular e Solicitarem Frete</button>
        </form>

        {f'''
        <div class="resposta">
            <strong>Cotação Gerada com Sucesso:</strong>
            <p style="color:#ffffff; font-size:15px; margin-bottom:6px;">• Trajeto: <strong>{resultado['origem']}</strong> &rarr; <strong>{resultado['destino']}</strong> ({resultado['distancia']} km)</p>
            <p style="color:#ffffff; font-size:15px; margin-bottom:6px;">• Ajudantes: <strong>{resultado['ajudantes']}</strong> | Embalagem: <strong>{resultado['embalagem']}</strong></p>
            <div style="background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.3); padding:20px; border-radius:12px; margin-top:15px; text-align:center;">
                <span style="color:#9ca3af; font-size:13px; text-transform:uppercase;">Valor Final do Frete</span>
                <div style="font-size:32px; font-weight:800; color:#10b981;">R$ {resultado['valor_total']:.2f}</div>
                <p style="color:#9ca3af; font-size:12px; margin-top:5px;">Pagamento protegido em custódia até a conclusão da entrega.</p>
                <a href="/pagamento" style="display:inline-block; margin-top:15px; background:#10b981; color:white; padding:12px 24px; border-radius:10px; font-weight:700; text-decoration:none;">Confirmar e Contratar Frete</a>
            </div>
        </div>
        ''' if resultado else ''}
    </div>
    """)

# ==============================================
# MÓDULO DE PASSAGENS AÉREAS E RODOVIÁRIAS
# ==============================================
@app.route("/passagens", methods=["GET", "POST"])
def pagina_passagens():
    if not usuario_logado():
        return redirect(url_for("entrar"))

    resultado = None
    mensagem_pre = ""

    if request.method == "POST":
        modalidade = request.form.get("modalidade")
        origem = request.form.get("origem")
        destino = request.form.get("destino")
        passageiros = int(request.form.get("passageiros", 1))
        data_viagem = request.form.get("data_viagem")
        classe = request.form.get("classe", "Econômica / Convencional")

        # Regra do cálculo e comissão
        if "Aérea" in modalidade:
            taxa_comissao = obter_taxa_comissao("TAXA_AEREO")
            base_balcao_unidade = 650.00
            desc_unidade = 590.00  # Vantagem para o consumidor
        else:
            taxa_comissao = obter_taxa_comissao("TAXA_ONIBUS")
            base_balcao_unidade = 180.00
            desc_unidade = 162.00  # Vantagem para o consumidor

        valor_balcao = base_balcao_unidade * passageiros
        valor_jnb = desc_unidade * passageiros
        taxa_plataforma = valor_jnb * (taxa_comissao / 100.0)

        conn, db_type = get_db()
        c = conn.cursor()
        param = "%s" if db_type == "postgres" else "?"
        c.execute(f"""INSERT INTO passagens_emitidas 
                     (usuario_id, modalidade, origem, destino, passageiros, data_viagem, classe, valor_balcao, valor_jnb, taxa_plataforma, data_hora)
                     VALUES ({param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param}, {param})""",
                  (session["usuario_id"], modalidade, origem, destino, passageiros, data_viagem, classe, valor_balcao, valor_jnb, taxa_plataforma, datetime.now().strftime("%d/%m/%Y %H:%M")))
        conn.commit()
        conn.close()

        resultado = {
            "modalidade": modalidade,
            "origem": origem,
            "destino": destino,
            "passageiros": passageiros,
            "data": data_viagem,
            "classe": classe,
            "valor_balcao": valor_balcao,
            "valor_jnb": valor_jnb,
            "economia": valor_balcao - valor_jnb
        }

    return render_template_string(LAYOUT, conteudo=f"""
    <div class="bloco">
        <h2>✈️ 🚌 Emissão de Passagens Aéreas & Rodoviárias</h2>
        <p>Bilhetes diretos com desconto sobre a tarifa de guichê tradicional e repasse automático às viações/companhias.</p>

        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px; margin-bottom:20px;">
            <div style="background:rgba(15, 23, 42, 0.5); padding:15px; border-radius:12px; border:1px solid rgba(16, 185, 129, 0.2);">
                <strong style="color:#10b981; font-size:13px;">✅ Vantagem para a Empresa de Transporte:</strong>
                <p style="color:var(--text-muted); font-size:12px; margin:4px 0 0 0;">Preenchimento de assentos ociosos sem custos operacionais de balcão, marketing ou equipe de vendas.</p>
            </div>
            <div style="background:rgba(15, 23, 42, 0.5); padding:15px; border-radius:12px; border:1px solid rgba(56, 189, 248, 0.2);">
                <strong style="color:#38bdf8; font-size:13px;">✅ Vantagem para o Consumidor:</strong>
                <p style="color:var(--text-muted); font-size:12px; margin:4px 0 0 0;">Economia de 8% a 15% em relação ao preço cobrado no guichê, com emissão do e-ticket direto no celular.</p>
            </div>
        </div>

        <form method="POST">
            <label style="color:var(--text-muted); font-size:12px;">Modalidade de Transporte</label>
            <select name="modalidade">
                <option value="Passagem Rodoviária (Ônibus Leito / Executivo)">Passagem Rodoviária (Ônibus Executivo / Leito)</option>
                <option value="Passagem Aérea (Voo Nacional / Regional)">Passagem Aérea (Voo Nacional / Regional)</option>
                <option value="Fretamento Corporativo de Ônibus">Fretamento Corporativo / Excursão Turismo</option>
            </select>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                <input type="text" name="origem" placeholder="Cidade / Aeroporto de Origem" required>
                <input type="text" name="destino" placeholder="Cidade / Aeroporto de Destino" required>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:15px;">
                <div>
                    <label style="color:var(--text-muted); font-size:12px;">Qtd. Passageiros</label>
                    <input type="number" name="passageiros" value="1" min="1" required>
                </div>
                <div>
                    <label style="color:var(--text-muted); font-size:12px;">Data da Viagem</label>
                    <input type="date" name="data_viagem" required>
                </div>
                <div>
                    <label style="color:var(--text-muted); font-size:12px;">Categoria / Classe</label>
                    <select name="classe">
                        <option value="Econômica / Convencional">Econômica / Convencional</option>
                        <option value="Executivo / Leito">Executivo / Leito</option>
                        <option value="Primeira Classe">Primeira Classe</option>
                    </select>
                </div>
            </div>

            <button type="submit" style="background:linear-gradient(135deg, #0284c7, #0369a1);">Pesquisar e Emitir Passagem com Desconto JNB</button>
        </form>

        {f'''
        <div class="resposta">
            <strong>Bilhete / Passagem Disponível:</strong>
            <p style="color:#ffffff; font-size:15px; margin-bottom:6px;">• Modalidade: <strong>{resultado['modalidade']}</strong> ({resultado['classe']})</p>
            <p style="color:#ffffff; font-size:15px; margin-bottom:6px;">• Trajeto: <strong>{resultado['origem']}</strong> &rarr; <strong>{resultado['destino']}</strong></p>
            <p style="color:#ffffff; font-size:15px; margin-bottom:12px;">• Data: <strong>{resultado['data']}</strong> | Total de Passageiros: <strong>{resultado['passageiros']}</strong></p>
            
            <div style="background:rgba(15, 23, 42, 0.8); border:1px solid rgba(56, 189, 248, 0.3); padding:20px; border-radius:12px; margin-top:15px; text-align:center;">
                <span style="color:#9ca3af; font-size:13px; text-transform:uppercase;">Valor de Balcão / Guichê: <s style="color:#f87171;">R$ {resultado['valor_balcao']:.2f}</s></span>
                <div style="font-size:32px; font-weight:800; color:#38bdf8; margin:8px 0;">Valor Exclusivo JNB: R$ {resultado['valor_jnb']:.2f}</div>
                <span class="badge-gratis" style="font-size:12px;">Sua Economia Direta: R$ {resultado['economia']:.2f}</span>
                <p style="color:#9ca3af; font-size:12px; margin-top:12px;">Passagem com assento garantido e emissão de bilhete digital instantânea.</p>
                <a href="/pagamento" style="display:inline-block; margin-top:15px; background:#0284c7; color:white; padding:12px 24px; border-radius:10px; font-weight:700; text-decoration:none;">Confirmar Reserva e Comprar</a>
            </div>
        </div>
        ''' if resultado else ''}
    </div>
    """)

# ==============================================
# MÓDULO SEJA SÓCIO / APOIADOR
# ==============================================
@app.route("/seja-socio", methods=["GET", "POST"])
def seja_socio():
    mensagem = ""
    if request.method == "POST":
        if not usuario_logado():
            return redirect(url_for("entrar"))

        nome = request.form.get("nome")
        email = request.form.get("email")
        telefone = request.form.get("telefone")
        investimento = request.form.get("investimento")
        mensagem_txt = request.form.get("mensagem")

        conn, db_type = get_db()
        c = conn.cursor()
        param = "%s" if db_type == "postgres" else "?"
        c.execute(f"""INSERT INTO socios_apoiadores 
                     (usuario_id, nome_completo, email, telefone, valor_investimento, mensagem, data_registro)
                     VALUES ({param}, {param}, {param}, {param}, {param}, {param}, {param})""",
                  (session["usuario_id"], nome, email, telefone, investimento, mensagem_txt, datetime.now().strftime("%d/%m/%Y")))
        conn.commit()
        conn.close()

        mensagem = "Proposta enviada com sucesso! O fundador analisará seu cadastro."

    return render_template_string(LAYOUT, conteudo=f"""
    <div class="bloco">
        <h2>🤝 Seja Sócio / Apoiador da Plataforma JNB</h2>
        <p>Receba divisão de lucros e participação das taxas de intermediação de fretes e emissão de passagens.</p>

        {f'<p style="background:rgba(168, 85, 247, 0.2); color:#c084fc; padding:12px; border-radius:10px; margin-bottom:15px; border:1px solid rgba(168, 85, 247, 0.4);">{mensagem}</p>' if mensagem else ''}

        <div style="background:rgba(15, 23, 42, 0.6); padding:20px; border-radius:16px; margin-bottom:20px; border:1px solid var(--card-border);">
            <h3 style="color:#c084fc; font-size:18px; margin-bottom:8px;">Fontes de Lucro do Sistema:</h3>
            <ul style="color:var(--text-muted); font-size:14px; margin-left:20px; line-height:1.7;">
                <li>Retenção de <strong>12%</strong> sobre Fretes e Mudanças.</li>
                <li>Retenção de <strong>10%</strong> sobre Passagens Rodoviárias e Fretamentos.</li>
                <li>Retenção de <strong>5%</strong> sobre Passagens Aéreas.</li>
                <li>Mensalidades de planos corporativos e venda de anúncios na vitrine.</li>
            </ul>
        </div>

        <form method="POST">
            <input type="text" name="nome" placeholder="Seu Nome Completo" required>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                <input type="email" name="email" placeholder="E-mail de Contato" required>
                <input type="text" name="telefone" placeholder="Telefone / WhatsApp" required>
            </div>
            <select name="investimento">
                <option value="Sócio Operacional / Regional">Sócio Operacional (Expansão Regional)</option>
                <option value="Aporte R$ 5.000 a R$ 20.000">Investidor Anjo (R$ 5.000 a R$ 20.000)</option>
                <option value="Aporte Acima de R$ 20.000">Investidor Estratégico (Acima de R$ 20.000)</option>
            </select>
            <textarea name="mensagem" rows="3" placeholder="Mensagem / Proposta de Sociedade..." required></textarea>
            <button type="submit" style="background:linear-gradient(135deg, #a855f7, #7e22ce);">Enviar Proposta de Sociedade</button>
        </form>
    </div>
    """)

# ==============================================
# MÓDULO PROFISSIONAIS E SERVIÇOS
# ==============================================
@app.route("/servicos", methods=["GET", "POST"])
def profissionais_servicos():
    mensagem = ""
    if request.method == "POST":
        if not usuario_logado():
            return redirect(url_for("entrar"))

        razao = request.form.get("razao")
        cnpj = request.form.get("cnpj")
        categoria = request.form.get("categoria")
        telefone = request.form.get("telefone")
        cidade = request.form.get("cidade")

        conn, db_type = get_db()
        c = conn.cursor()
        param = "%s" if db_type == "postgres" else "?"
        c.execute(f"""INSERT INTO empresas_parceiras 
                     (usuario_id, razao_social, cnpj_cpf, categoria, telefone, cidade, data_cadastro)
                     VALUES ({param}, {param}, {param}, {param}, {param}, {param}, {param})""",
                  (session["usuario_id"], razao, cnpj, categoria, telefone, cidade, datetime.now().strftime("%d/%m/%Y")))
        conn.commit()
        conn.close()

        mensagem = "Cadastro enviado com sucesso! Aguarde a liberação do administrador."

    conn, db_type = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM empresas_parceiras WHERE status = 'aprovada' ORDER BY id DESC")
    empresas_aprovadas = c.fetchall()
    conn.close()

    return render_template_string(LAYOUT, conteudo=f"""
    <div class="bloco">
        <h2>🛠️ Rede de Empresas, Viações & Prestadores</h2>
        <p>Cadastre sua empresa de frete, viação ou serviços para receber pedidos sem custo de anúncio.</p>

        {f'<p style="background:rgba(16, 185, 129, 0.15); color:#34d399; padding:12px; border-radius:10px; margin-bottom:15px; border:1px solid rgba(16, 185, 129, 0.3);">{mensagem}</p>' if mensagem else ''}

        <h3 style="color:#38bdf8; margin-bottom:15px;">Parceiros Homologados</h3>
        <table>
            <tr>
                <th>Empresa / Prestador</th>
                <th>Categoria</th>
                <th>Cidade</th>
                <th>Contato</th>
            </tr>
            {''.join([f'''
            <tr>
                <td><strong>{e['razao_social']}</strong></td>
                <td>{e['categoria']}</td>
                <td>{e['cidade']}</td>
                <td><span style="color:#10b981; font-weight:700;">{e['telefone']}</span></td>
            </tr>
            ''' for e in empresas_aprovadas]) if empresas_aprovadas else '<tr><td colspan="4">Nenhum parceiro cadastrado ainda.</td></tr>'}
        </table>

        <div style="margin-top:35px; border-top:1px solid var(--card-border); padding-top:25px;">
            <h3 style="color:#ffffff; margin-bottom:10px;">Cadastrar Minha Empresa / Agência</h3>
            <form method="POST">
                <input type="text" name="razao" placeholder="Razão Social ou Nome Fantasia" required>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                    <input type="text" name="cnpj" placeholder="CNPJ ou CPF" required>
                    <input type="text" name="telefone" placeholder="WhatsApp Comercial" required>
                </div>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                    <select name="categoria">
                        <option value="Transportadora / Empresa de Mudanças">Transportadora / Empresa de Mudanças</option>
                        <option value="Viação / Empresa de Ônibus / Fretamento">Viação / Empresa de Ônibus / Fretamento</option>
                        <option value="Companhia Aérea / Agência Consolidadora">Companhia Aérea / Agência Consolidadora</option>
                        <option value="Montador de Móveis / Serviços">Montador de Móveis / Serviços</option>
                    </select>
                    <input type="text" name="cidade" placeholder="Cidade / Estado" required>
                </div>
                <button type="submit">Cadastrar Empresa na Plataforma</button>
            </form>
        </div>
    </div>
    """)

# ==============================================
# MÓDULO DE PUBLICIDADE
# ==============================================
@app.route("/anuncie", methods=["GET", "POST"])
def pagina_anuncie():
    if not usuario_logado():
        return redirect(url_for("entrar"))

    mensagem = ""
    if request.method == "POST":
        empresa = request.form.get("empresa")
        plano = request.form.get("plano")
        link = request.form.get("link")
        conteudo = request.form.get("conteudo")

        val_map = {
            "Banner Topo (Mensal)": 199.00,
            "Destaque Lateral (Mensal)": 99.00,
            "Anúncio no Chat IA (Mensal)": 149.00
        }
        valor = val_map.get(plano, 99.00)

        conn, db_type = get_db()
        c = conn.cursor()
        param = "%s" if db_type == "postgres" else "?"
        c.execute(f"""INSERT INTO contratos_publicidade 
                     (usuario_id, empresa_nome, plano_anuncio, link_destino, conteudo_anuncio, valor, data_inicio)
                     VALUES ({param}, {param}, {param}, {param}, {param}, {param}, {param})""",
                  (session["usuario_id"], empresa, plano, link, conteudo, valor, datetime.now().strftime("%d/%m/%Y")))
        conn.commit()
        conn.close()

        mensagem = "Contrato de Anúncio criado! Faça o pagamento via PIX para liberação na vitrine."

    conn, db_type = get_db()
    c = conn.cursor()
    param = "%s" if db_type == "postgres" else "?"
    c.execute(f"SELECT * FROM contratos_publicidade WHERE usuario_id = {param} ORDER BY id DESC", (session["usuario_id"],))
    meus_anuncios = c.fetchall()
    conn.close()

    return render_template_string(LAYOUT, conteudo=f"""
    <div class="bloco">
        <h2>📢 Contratos de Anúncios & Vitrine</h2>
        <p>Divulgue sua marca para milhares de usuários ativos buscando transporte e passagens.</p>

        {f'<p style="background:rgba(16, 185, 129, 0.15); color:#34d399; padding:12px; border-radius:10px; margin-bottom:15px; border:1px solid rgba(16, 185, 129, 0.3);">{mensagem}</p>' if mensagem else ''}

        <form method="POST">
            <input type="text" name="empresa" placeholder="Nome da Sua Marca / Empresa" required>
            
            <label style="color:var(--text-muted); font-size:12px;">Selecione o Plano de Anúncio</label>
            <select name="plano">
                <option value="Banner Topo (Mensal)">Banner Topo do Site — R$ 199,00 / mês</option>
                <option value="Destaque Lateral (Mensal)">Destaque Vitrine — R$ 99,00 / mês</option>
                <option value="Anúncio no Chat IA (Mensal)">Patrocínio IA — R$ 149,00 / mês</option>
            </select>

            <input type="url" name="link" placeholder="Link do seu Site ou WhatsApp" required>
            <textarea name="conteudo" rows="3" placeholder="Descrição do anúncio ou promoção..." required></textarea>
            
            <button type="submit">Contratar Anúncio & Criar PIX</button>
        </form>

        <h3 style="color:#ffffff; margin:30px 0 15px 0;">Seus Anúncios Registrados</h3>
        <table>
            <tr>
                <th>Empresa</th>
                <th>Plano</th>
                <th>Valor</th>
                <th>Status</th>
                <th>Data</th>
            </tr>
            {''.join([f'''
            <tr>
                <td><strong>{a['empresa_nome']}</strong></td>
                <td>{a['plano_anuncio']}</td>
                <td>R$ {a['valor']:.2f}</td>
                <td><span class="badge-{"gratis" if a['status']=="ativo" else "pago"}">{a['status']}</span></td>
                <td>{a['data_inicio']}</td>
            </tr>
            ''' for a in meus_anuncios]) if meus_anuncios else '<tr><td colspan="5">Você não possui anúncios cadastrados.</td></tr>'}
        </table>
    </div>
    """)

# ==============================================
# OUTRAS ROTAS DO SISTEMA
# ==============================================
@app.route("/admin/conhecimento", methods=["GET", "POST"])
def admin_conhecimento():
    if not usuario_logado() or not eh_dono():
        return redirect(url_for("inicio"))

    mensagem = ""
    if request.method == "POST":
        palavra_chave = request.form.get("palavra_chave", "").strip()
        assunto = request.form.get("assunto", "").strip()
        resposta = request.form.get("resposta", "").strip()
        fonte = request.form.get("fonte", "Administração JNB").strip()

        if palavra_chave and assunto and resposta:
            conn, db_type = get_db()
            c = conn.cursor()
            param = "%s" if db_type == "postgres" else "?"
            c.execute(
                f"INSERT INTO base_conhecimento (palavra_chave, assunto, resposta, fonte) VALUES ({param}, {param}, {param}, {param})",
                (palavra_chave, assunto, resposta, fonte)
            )
            conn.commit()
            conn.close()
            mensagem = "Conhecimento cadastrado no cérebro da IA!"

    return render_template_string(LAYOUT, conteudo=f"""
    <div class="bloco">
        <h2>🎓 Treinar Inteligência Artificial JNB</h2>
        <p>Alimente a base de conhecimento com regras de passagens, fretes e normas.</p>
        {f'<p style="background:rgba(16, 185, 129, 0.15); color:#34d399; padding:12px; border-radius:10px; margin-bottom:15px; border:1px solid rgba(16, 185, 129, 0.3);">{mensagem}</p>' if mensagem else ''}
        <form method="POST">
            <input type="text" name="palavra_chave" placeholder="Palavras-chave separadas por espaço" required>
            <input type="text" name="assunto" placeholder="Assunto Principal" required>
            <textarea name="resposta" rows="4" placeholder="Resposta detalhada que a IA deve dar..." required></textarea>
            <input type="text" name="fonte" placeholder="Fonte da Informação (ex: Manual Comercial JNB)">
            <button type="submit">🧠 Gravar Conhecimento</button>
        </form>
    </div>
    """)

@app.route("/gerar-projeto", methods=["GET", "POST"])
def pagina_gerar_projeto():
    if not usuario_logado():
        return redirect(url_for("entrar"))

    resultado = ""
    if request.method == "POST":
        nome = request.form.get("nome")
        tipo = request.form.get("tipo")
        desc = request.form.get("descricao")
        
        codigo, viabilidade = gerar_projeto_engenharia(nome, tipo, desc)
        
        conn, db_type = get_db()
        c = conn.cursor()
        param = "%s" if db_type == "postgres" else "?"
        c.execute(f"INSERT INTO projetos (nome, tipo, descricao, codigo_gerado, viabilidade, data_criacao, usuario_id) VALUES ({param}, {param}, {param}, {param}, {param}, {param}, {param})",
                  (nome, tipo, desc, codigo, viabilidade, datetime.now().strftime("%d/%m/%Y"), session["usuario_id"]))
        conn.commit()
        conn.close()

        resultado = f"PROJETO GERADO COM SUCESSO!\n\n--- SOFTWARE / CÓDIGO EMBARCADO ---\n{codigo}\n\n--- RELATÓRIO DE VIABILIDADE ---\n{viabilidade}"

    return render_template_string(LAYOUT, conteudo=f"""
    <div class="bloco">
        <h2>🛠️ Gerador de Projetos Executivos & Engenharia</h2>
        <form method="POST">
            <input type="text" name="nome" placeholder="Nome do Projeto / Cliente" required>
            <select name="tipo">
                <option value="Automação Veicular">Automação Veicular</option>
                <option value="Automação de Aeronaves">Automação de Aeronaves</option>
                <option value="Automação Industrial">Automação Industrial</option>
                <option value="Engenharia Elétrica">Engenharia Elétrica</option>
            </select>
            <textarea name="descricao" rows="4" placeholder="Requisitos do projeto..." required></textarea>
            <button type="submit">Gerar Projeto Executivo</button>
        </form>
        {f'<div class="resposta"><pre>{resultado}</pre></div>' if resultado else ''}
    </div>
    """)

@app.route("/executar-jnb", methods=["GET", "POST"])
def pagina_executar_jnb():
    if not usuario_logado():
        return redirect(url_for("entrar"))

    codigo = request.form.get("codigo", "")
    resultado = ""

    if request.method == "POST" and codigo:
        interpretador = InterpretadorJNB()
        try:
            resultado = interpretador.executar(codigo)
        except Exception as e:
            resultado = f"Erro de execução: {str(e)}"

    return render_template_string(LAYOUT, conteudo=f"""
    <div class="bloco">
        <h2>💻 Terminal Compilador JNB</h2>
        <form method="POST">
            <textarea name="codigo" rows="6" placeholder="DEF valor1 = ZX\nDEF valor2 = A\nMOSTRE valor1 + valor2" style="font-family:monospace;">{codigo}</textarea>
            <button type="submit">Compilar e Executar Script</button>
        </form>
        {f'<div class="resposta"><pre>{resultado}</pre></div>' if resultado else ''}
    </div>
    """)

@app.route("/pagamento", methods=["GET", "POST"])
def pagamento():
    if not usuario_logado():
        return redirect(url_for("entrar"))

    if request.method == "POST":
        conn, db_type = get_db()
        c = conn.cursor()
        param = "%s" if db_type == "postgres" else "?"
        c.execute(f"UPDATE usuarios SET pago = 1, data_pagamento = {param} WHERE id = {param}",
                  (datetime.now().strftime("%d/%m/%Y"), session["usuario_id"]))
        conn.commit()
        conn.close()
        return redirect(url_for("inicio"))

    return render_template_string(LAYOUT, conteudo=f"""
    <div class="bloco" style="text-align:center;">
        <h2>💳 Pagamento Seguro em Custódia</h2>
        <p>Realize o PIX para garantir sua contratação ou passagem. O valor fica retido até a prestação do serviço.</p>
        
        <div style="background:rgba(15, 23, 42, 0.6); border:1px solid var(--card-border); padding:25px; border-radius:16px; margin:20px 0; text-align:left;">
            <p style="color:var(--text-muted); font-size:13px; margin-bottom:5px;">Chave PIX Oficial:</p>
            <code style="background:rgba(255,255,255,0.06); color:#38bdf8; padding:8px 14px; border-radius:8px; font-weight:700; display:inline-block; margin-bottom:15px; font-size:16px;">{CHAVE_PIX}</code>
            <p style="color:var(--text-muted); font-size:13px; margin-bottom:5px;">Favorecido:</p>
            <p style="color:#ffffff; font-weight:600;">{NOME_RECEBEDOR}</p>
        </div>

        <form method="POST">
            <button type="submit">Já Realizei o Pagamento / Liberar E-ticket ou Serviço</button>
        </form>
    </div>
    """)

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        conn, db_type = get_db()
        c = conn.cursor()
        param = "%s" if db_type == "postgres" else "?"
        try:
            c.execute(f"INSERT INTO usuarios (nome, email, senha_hash, data_cadastro) VALUES ({param}, {param}, {param}, {param})",
                      (nome, email, hashlib.sha256(senha.encode()).hexdigest(), datetime.now().strftime("%d/%m/%Y")))
            conn.commit()
            
            c.execute(f"SELECT id FROM usuarios WHERE email = {param}", (email,))
            novo_usuario = c.fetchone()
            
            session["usuario_id"] = novo_usuario["id"]
            session["nome"] = nome
            return redirect(url_for("inicio"))
        except Exception as e:
            return f"Erro ao cadastrar. ({str(e)})"
        finally:
            conn.close()

    return render_template_string(LAYOUT, conteudo="""
    <div class="bloco" style="max-width: 450px; margin: 20px auto;">
        <h2>Criar Conta</h2>
        <form method="POST">
            <input type="text" name="nome" placeholder="Seu Nome Completo" required>
            <input type="email" name="email" placeholder="Seu E-mail" required>
            <input type="password" name="senha" placeholder="Sua Senha" required>
            <button type="submit">Criar Minha Conta</button>
        </form>
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
        c.execute(f"SELECT id, nome, senha_hash, ativo FROM usuarios WHERE email = {param}", (email,))
        user = c.fetchone()
        conn.close()
        if user and user["ativo"] == 1 and user["senha_hash"] == hashlib.sha256(senha.encode()).hexdigest():
            session["usuario_id"] = user["id"]
            session["nome"] = user["nome"]
            return redirect(url_for("inicio"))
        return "E-mail ou senha incorretos."

    return render_template_string(LAYOUT, conteudo="""
    <div class="bloco" style="max-width: 450px; margin: 20px auto;">
        <h2>Entrar no Sistema</h2>
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
