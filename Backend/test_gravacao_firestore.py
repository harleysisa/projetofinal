"""
Script de Teste Automatizado: Validação da Gravação de Produtos no Cloud Firestore
"""
import os
import sys

# Garante suporte a UTF-8 no stdout do Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from server import tool_cadastrar_produto, db

def testar_gravacao_firestore():
    print("=" * 60)
    print("[TESTE] INICIANDO TESTE DE GRAVACAO DE PRODUTO NO CLOUD FIRESTORE")
    print("=" * 60)

    # Dados de teste
    dados_teste = {
        "produtor_id": "usr_teste_produtor_001",
        "nome": "Melancia Crimson Sweet Selecionada",
        "categoria": "fruta",
        "preco_kg": 2.85,
        "quantidade_kg": 1500.0
    }

    print("\n1. Enviando dados para gravacao via 'tool_cadastrar_produto'...")
    print(f"   Payload: {dados_teste}")

    try:
        # Executa a função MCP de cadastro
        resultado = tool_cadastrar_produto(**dados_teste)
        print(f"\n[OK] Retorno da funcao MCP: {resultado}")
        
        produto_id = resultado.get("produto_id")
        if not produto_id:
            raise AssertionError("[ERRO] 'produto_id' nao foi retornado.")

        print(f"\n2. Consultando documento gravado no Firestore (ID: {produto_id})...")
        doc_ref = db.collection('produtos').document(produto_id)
        doc = doc_ref.get()

        if not doc.exists:
            raise AssertionError(f"[ERRO] Documento '{produto_id}' nao foi encontrado no Firestore.")

        doc_dict = doc.to_dict()
        print(f"[OK] Documento recuperado com sucesso!")
        print(f"   Dados no Firestore: {doc_dict}")

        # Validações de integridade dos campos
        assert doc_dict.get("produtor_id") == dados_teste["produtor_id"], "produtor_id incorreto"
        assert doc_dict.get("nome") == dados_teste["nome"], "nome incorreto"
        assert doc_dict.get("categoria") == dados_teste["categoria"], "categoria incorreta"
        assert abs(doc_dict.get("preco_kg") - dados_teste["preco_kg"]) < 0.001, "preco_kg incorreto"
        assert abs(doc_dict.get("quantidade_kg") - dados_teste["quantidade_kg"]) < 0.001, "quantidade_kg incorreto"
        assert "criado_em" in doc_dict, "Timestamp criado_em ausente"

        print("\n" + "=" * 60)
        print("[SUCESSO] TESTE CONCLUIDO COM SUCESSO!")
        print(f"   - Colecao: 'produtos'")
        print(f"   - Documento ID: {produto_id}")
        print(f"   - Status: Gravado e verificado com integridade total no Firestore.")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n[ERRO] DURANTE O TESTE: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    sucesso = testar_gravacao_firestore()
    sys.exit(0 if sucesso else 1)
