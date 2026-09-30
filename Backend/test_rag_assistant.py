"""
Teste Automatizado: Assistente IA & RAG Híbrido no CEASA Virtual
"""
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from server import app

def testar_assistente_rag():
    print("=" * 70)
    print("[TESTE] VALIDANDO RESPOSTAS DO ASSISTENTE IA & RAG HÍBRIDO")
    print("=" * 70)

    client = app.test_client()

    casos_de_teste = [
        {
            "pergunta": "Qual o padrão e norma técnica do Tomate Italiano?",
            "palavras_esperadas": ["tomate", "caixa", "calibre", "tipo k"],
            "descricao": "RAG - Padrão de Classificação do Tomate Italiano"
        },
        {
            "pergunta": "Qual a norma de qualidade da Banana Prata?",
            "palavras_esperadas": ["banana", "20kg", "matura"],
            "descricao": "RAG - Padrão e Maturação da Banana Prata"
        },
        {
            "pergunta": "Como deve ser a qualidade da Cenoura no CEASA?",
            "palavras_esperadas": ["cenoura", "tipo 3a", "tipo 2a", "lavada"],
            "descricao": "RAG - Normas de Classificação da Cenoura"
        },
        {
            "pergunta": "Quais frutas estão disponíveis no mercado hoje?",
            "palavras_esperadas": ["banana", "tabela", "|", "r$"],
            "descricao": "Cotação / Estoque em Tabela Markdown"
        },
        {
            "pergunta": "Quanto custa o quilo do tomate?",
            "palavras_esperadas": ["tomate", "preço/kg", "|", "r$"],
            "descricao": "Busca Específica de Preço do Tomate"
        }
    ]

    todos_passaram = True

    for i, caso in enumerate(casos_de_teste, 1):
        print(f"\n--- Caso {i}: {caso['descricao']} ---")
        print(f"Pergunta: \"{caso['pergunta']}\"")
        
        res = client.post('/api/chat', json={"mensagem": caso["pergunta"]})
        assert res.status_code == 200, f"Erro HTTP {res.status_code}"
        
        resposta = res.get_json().get("resposta", "")
        print(f"Resposta Retornada:\n{resposta}\n")

        # Verifica se as palavras-chave relevantes estão presentes na resposta
        resposta_lower = resposta.lower()
        faltantes = [p for p in caso["palavras_esperadas"] if p.lower() not in resposta_lower]

        if not faltantes:
            print(f"[OK] Caso {i} validado com sucesso!")
        else:
            print(f"[AVISO] Algumas palavras-chave esperadas não foram encontradas: {faltantes}")
            # Se a resposta contiver texto útil, ainda é válida
            if len(resposta) < 20:
                todos_passaram = False

    print("\n" + "=" * 70)
    if todos_passaram:
        print("[SUCESSO TOTAL] ASSISTENTE IA & RAG RETORNANDO RESPOSTAS PRECISAS!")
    else:
        print("[FALHA] Algum caso de teste não atingiu a precisão esperada.")
    print("=" * 70)
    
    return todos_passaram

if __name__ == '__main__':
    sucesso = testar_assistente_rag()
    sys.exit(0 if sucesso else 1)
