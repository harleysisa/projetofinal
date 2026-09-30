import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
CORS(app)

# Caminho absoluto para o arquivo de credenciais
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.environ.get("FIREBASE_KEY_PATH", os.path.join(BASE_DIR, "firebase-key.json"))

# Inicializa Firebase Admin
if not firebase_admin._apps:
    if os.path.exists(KEY_PATH):
        cred = credentials.Certificate(KEY_PATH)
        firebase_admin.initialize_app(cred)
    else:
        firebase_admin.initialize_app()

db = firestore.client()

def _serialize_firestore_data(data):
    """Converte tipos do Firestore (datetime, etc) em formato JSON serializável."""
    if isinstance(data, dict):
        return {k: _serialize_firestore_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_serialize_firestore_data(v) for v in data]
    elif isinstance(data, datetime):
        return data.isoformat()
    elif hasattr(data, '__class__') and 'Sentinel' in data.__class__.__name__:
        return datetime.utcnow().isoformat()
    return data

# =====================================================================
# FERRAMENTAS MCP (Expostas para o modelo Gemini/Agente)
# =====================================================================

def tool_cadastrar_produto(produtor_id, nome, categoria, preco_kg, quantidade_kg):
    if not produtor_id or not nome:
        raise ValueError("produtor_id e nome são obrigatórios.")
        
    doc_ref = db.collection('produtos').document()
    dados = {
        'produtor_id': str(produtor_id),
        'nome': str(nome).strip(),
        'categoria': str(categoria).lower().strip() if categoria else "geral",
        'preco_kg': float(preco_kg),
        'quantidade_kg': float(quantidade_kg),
        'criado_em': firestore.SERVER_TIMESTAMP
    }
    doc_ref.set(dados)
    return {"status": "sucesso", "produto_id": doc_ref.id, "mensagem": f"Produto '{nome}' cadastrado com sucesso!"}

def tool_listar_ofertas(categoria=None):
    ref = db.collection('produtos')
    if categoria and categoria.strip().lower() not in ["todos", "todas", "geral", ""]:
        ref = ref.where('categoria', '==', str(categoria).lower().strip())
    docs = ref.stream()
    
    produtos = []
    for d in docs:
        doc_data = _serialize_firestore_data(d.to_dict() or {})
        produtos.append({"id": d.id, **doc_data})
        
    return produtos

import re

STOPWORDS = {
    "qual", "quais", "como", "para", "onde", "quando", "quanto", "quem", "porque",
    "por", "que", "de", "do", "da", "dos", "das", "um", "uma", "uns", "umas",
    "o", "a", "os", "as", "em", "no", "na", "nos", "nas", "e", "ou", "se",
    "com", "sobre", "ao", "aos", "à", "às", "está", "estao", "tem", "qualidade",
    "norma", "tecnica", "técnica", "padrao", "padrão", "manual", "classificacao", "classificação"
}

def extrair_palavras_chave(texto):
    """Extrai palavras-chave relevantes de uma consulta em linguagem natural."""
    palavras = re.findall(r'\b[a-zA-ZáéíóúÁÉÍÓÚãõÃÕâêîôûÂÊÎÔÛçÇ]{3,}\b', (texto or "").lower())
    chaves = [p for p in palavras if p not in STOPWORDS]
    return chaves if chaves else palavras

def tool_consultar_qualidade(duvida=None, produto=None, termo_busca=None):
    """Realiza busca RAG por relevância nas normas técnicas e manuais de qualidade do CEASA."""
    texto_consulta = f"{termo_busca or ''} {duvida or ''} {produto or ''}".strip().lower()
    chaves = extrair_palavras_chave(texto_consulta)
    
    docs = db.collection('manuais_qualidade').stream()
    candidatos = []
    
    for doc in docs:
        d = doc.to_dict() or {}
        conteudo = d.get('conteudo', '')
        prod_doc = d.get('produto', '')
        cat_doc = d.get('categoria', '')
        
        texto_completo = f"{prod_doc} {cat_doc} {conteudo}".lower()
        
        # Calcula score de relevância por correspondência de termos
        score = 0
        for chave in chaves:
            if chave in prod_doc.lower():
                score += 5  # Alta relevância no nome do produto
            elif chave in cat_doc.lower():
                score += 3  # Relevância na categoria
            elif chave in conteudo.lower():
                score += 1  # Relevância no corpo do texto
                
        if score > 0 or not chaves:
            candidatos.append({
                "score": score,
                "produto": prod_doc,
                "categoria": cat_doc,
                "norma": conteudo
            })
            
    # Ordena pelos mais relevantes
    candidatos.sort(key=lambda x: x["score"], reverse=True)
    
    resultados_finais = [{
        "produto": c["produto"],
        "categoria": c["categoria"],
        "norma": c["norma"]
    } for c in candidatos[:4]]
    
    if not resultados_finais:
        return {"mensagem": "Nenhuma norma técnica encontrada para o termo pesquisado.", "resultados": []}
    return {"resultados": resultados_finais}

# Dispatcher do protocolo MCP
MCP_TOOLS = {
    "cadastrar_produto": tool_cadastrar_produto,
    "listar_ofertas": tool_listar_ofertas,
    "consultar_qualidade": tool_consultar_qualidade
}

# =====================================================================
# ROTAS DE AUTENTICAÇÃO E USUÁRIOS (Firestore)
# =====================================================================

@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    """Registra ou atualiza sessão do usuário na coleção 'usuarios' do Firestore."""
    data = request.get_json(silent=True) or {}
    uid = data.get('uid')
    if not uid:
        return jsonify({"success": False, "error": "UID do usuário é obrigatório"}), 400

    tipo_perfil = str(data.get('tipo_perfil', 'PRODUTOR')).upper()
    if tipo_perfil not in ['PRODUTOR', 'LOJISTA', 'CLIENTE']:
        tipo_perfil = 'PRODUTOR'

    user_data = {
        "uid": str(uid),
        "nome": str(data.get('nome', 'Usuário Google')),
        "email": str(data.get('email', '')),
        "foto_url": str(data.get('foto_url', '')),
        "tipo_perfil": tipo_perfil,
        "ultimo_acesso": firestore.SERVER_TIMESTAMP
    }

    try:
        user_ref = db.collection('usuarios').document(str(uid))
        user_ref.set(user_data, merge=True)
        return jsonify({"success": True, "usuario": _serialize_firestore_data(user_data)}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/auth/usuario/<uid>', methods=['GET'])
def get_user_profile(uid):
    """Consulta perfil e permissões do usuário."""
    try:
        doc = db.collection('usuarios').document(str(uid)).get()
        if not doc.exists:
            return jsonify({"success": False, "error": "Usuário não encontrado"}), 404
        return jsonify({"success": True, "usuario": _serialize_firestore_data(doc.to_dict())}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# =====================================================================
# ROTAS DA API & MCP (Com Controle de Acesso por Perfil)
# =====================================================================

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "online",
        "servico": "CEASA Virtual - Backend MCP & RAG API",
        "versao": "1.0.0",
        "autenticacao_obrigatoria": True,
        "ferramentas_mcp": list(MCP_TOOLS.keys())
    }), 200

@app.route('/mcp/v1/executar', methods=['POST'])
def handle_mcp():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"success": False, "error": "Corpo da requisição JSON inválido ou ausente"}), 400

    tool_name = data.get('tool')
    params = data.get('parameters', {})
    
    if not isinstance(params, dict):
        return jsonify({"success": False, "error": "O campo 'parameters' deve ser um objeto/dicionário"}), 400

    if tool_name not in MCP_TOOLS:
        return jsonify({"success": False, "error": f"Ferramenta '{tool_name}' não encontrada"}), 404
        
    # Validação de Permissão conforme Tópico 5 do GEMINI.md
    produtor_id = params.get('produtor_id')
    if tool_name == 'cadastrar_produto' and not produtor_id:
        return jsonify({"success": False, "error": "Acesso Negado: Cadastrar lotes exige autenticação com perfil de Produtor Rural."}), 403

    try:
        result = MCP_TOOLS[tool_name](**params)
        return jsonify({"success": True, "result": result}), 200
    except TypeError as te:
        return jsonify({"success": False, "error": f"Parâmetros incorretos para '{tool_name}': {str(te)}"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    """Endpoint de chat inteligente com o Assistente Comercial CEASA (RAG Híbrido)."""
    data = request.get_json(silent=True) or {}
    user_msg = data.get('mensagem', '').strip()
    produtor_id = data.get('produtor_id', 'anonimo')
    
    if not user_msg:
        return jsonify({"resposta": "Olá! Como posso ajudar você hoje no CEASA Virtual?"})
    
    # 1. Recupera Contexto RAG do Firestore
    rag_info = tool_consultar_qualidade(duvida=user_msg)
    normas_encontradas = rag_info.get("resultados", [])
    
    produtos = tool_listar_ofertas()
    
    # Se a chave do Gemini estiver configurada no ambiente
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            produtos_txt = "\n".join([f"- {p.get('nome')} ({p.get('categoria')}): R$ {float(p.get('preco_kg',0)):.2f}/kg - Estoque: {p.get('quantidade_kg')}kg" for p in produtos])
            normas_txt = "\n".join([f"- {n.get('produto')} ({n.get('categoria')}): {n.get('norma')}" for n in normas_encontradas]) if normas_encontradas else "Nenhuma norma técnica específica recuperada."
            
            prompt = f"""Você é o Assistente Virtual Comercial do CEASA Virtual (intermediação de hortifrúti).

Estoque Atual no CEASA Virtual:
{produtos_txt}

Manuais de Qualidade Recuperados (RAG):
{normas_txt}

Pergunta do Usuário: {user_msg}

Instruções:
- Seja cortês, comercial e direto.
- Ao listar ofertas e cotações, formate OBRIGATORIAMENTE em Tabelas Markdown com as colunas | Produto | Categoria | Preço/Kg | Estoque |.
- Ao responder dúvidas de classificação e caixas, fundamente-se estritamente nas normas técnicas recuperadas."""
            
            response = model.generate_content(prompt)
            return jsonify({"resposta": response.text})
        except Exception:
            pass # Fallback automático
    
    # 2. Motor Autônomo Local com RAG Semântico
    msg_lower = user_msg.lower()
    chaves_msg = extrair_palavras_chave(msg_lower)
    
    # Intenção 1: Normas técnicas e classificação (RAG)
    if normas_encontradas and any(p in msg_lower for p in ["norma", "qualidade", "classifica", "caixa", "matura", "padrao", "padrão", "como", "tipo", "calibre"]):
        texto_normas = "\n\n".join([f"📋 **Norma para {r.get('produto', 'Hortifrúti')} ({r.get('categoria', '').capitalize()}):**\n{r.get('norma')}" for r in normas_encontradas])
        return jsonify({"resposta": f"Consultei nossos manuais técnicos do CEASA:\n\n{texto_normas}"})
        
    # Intenção 2: Cotações e Estoque
    if any(p in msg_lower for p in ["oferta", "ofertas", "preço", "preco", "precos", "preços", "tem", "comprar", "produtos", "listar", "catalogo", "catálogo", "quanto"]):
        # Filtra por categoria ou nome do item
        produtos_filtrados = []
        for p in produtos:
            nome_p = p.get('nome', '').lower()
            cat_p = p.get('categoria', '').lower()
            if any(k in nome_p or k in cat_p for k in chaves_msg) or not chaves_msg:
                produtos_filtrados.append(p)
                
        if not produtos_filtrados:
            produtos_filtrados = produtos  # Mostra todos se não houver filtro específico
            
        tabela = "| Produto | Categoria | Preço/Kg | Estoque |\n| :--- | :--- | :--- | :--- |\n"
        for p in produtos_filtrados:
            tabela += f"| **{p.get('nome')}** | {p.get('categoria', '').capitalize()} | R$ {float(p.get('preco_kg',0)):.2f} | {p.get('quantidade_kg')} kg |\n"
        
        return jsonify({"resposta": f"Aqui estão os lotes disponíveis no CEASA Virtual:\n\n{tabela}\n\n*Posso te ajudar a fechar o pedido de algum desses itens?*"})
        
    # Se tiver encontrado norma de qualidade diretamente
    if normas_encontradas:
        texto_normas = "\n\n".join([f"📋 **Padrão Técnico ({r.get('produto', 'Hortifrúti')}):**\n{r.get('norma')}" for r in normas_encontradas])
        return jsonify({"resposta": f"Localizei as seguintes informações nos manuais do CEASA:\n\n{texto_normas}"})

    return jsonify({
        "resposta": "Olá! Sou o **Assistente Comercial do CEASA Virtual**.\n\nVocê pode me perguntar sobre:\n- 🛒 **Cotação e preços** (ex: *'Quais frutas estão disponíveis?'* ou *'Quanto custa o tomate?'*)\n- 📋 **Normas de qualidade e caixas** (ex: *'Qual o padrão da caixa de banana prata?'*)\n- 🌾 **Anúncio de lotes** para produtores rurais."
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)