"""
Teste End-to-End: Simulação do Fluxo Front-end -> API Flask -> Cloud Firestore
"""
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from server import app, db

def testar_fluxo_frontend_para_firestore():
    print("=" * 70)
    print("[TESTE E2E] VALIDANDO GRAVAÇÃO DO FRONT-END NO CLOUD FIRESTORE")
    print("=" * 70)

    client = app.test_client()

    # 1. Simular Login do Front-end (definirUsuario())
    uid_usuario = "usr_frontend_produtor_888"
    payload_login_frontend = {
        "uid": uid_usuario,
        "nome": "Sebastião do Vale - Produtor de Morangos",
        "email": "sebastiao.morango@ceasavirtual.com",
        "tipo_perfil": "PRODUTOR"
    }

    print("\n1. Simulando requisição de Login do Front-end (POST /api/auth/login)...")
    res_login = client.post('/api/auth/login', json=payload_login_frontend)
    print(f"   Status HTTP: {res_login.status_code}")
    assert res_login.status_code == 200, "Erro ao registrar login do front-end"

    # Verificar no Firestore se o usuário foi gravado
    user_doc = db.collection('usuarios').document(uid_usuario).get()
    assert user_doc.exists, "Usuário não foi gravado no Firestore!"
    print(f"   [OK] Usuário confirmado no Firestore: {user_doc.to_dict().get('nome')}")

    # 2. Simular Envio do Formulário de Cadastro do Lote do Front-end (salvarLote())
    payload_produto_frontend = {
        "tool": "cadastrar_produto",
        "parameters": {
            "produtor_id": uid_usuario,
            "nome": "Morango Orgânico Padrão CEASA Caixa 1.2kg",
            "categoria": "fruta",
            "preco_kg": 18.50,
            "quantidade_kg": 300.0
        }
    }

    print("\n2. Simulando envio do Formulário 'Cadastrar Lote' (POST /mcp/v1/executar)...")
    print(f"   Dados enviados pelo Front-end: {payload_produto_frontend['parameters']}")
    
    res_produto = client.post('/mcp/v1/executar', json=payload_produto_frontend)
    print(f"   Status HTTP retornado: {res_produto.status_code}")
    data_produto = res_produto.get_json()
    print(f"   Resposta da API: {data_produto}")

    assert res_produto.status_code == 200, "Erro na resposta do cadastro"
    assert data_produto.get("success") == True, "Falha no status de sucesso"
    
    produto_id = data_produto["result"]["produto_id"]
    print(f"   [OK] Produto registrado pela API com ID: {produto_id}")

    # 3. Validar no Cloud Firestore se o documento existe e os campos estão corretos
    print(f"\n3. Consultando diretamente a coleção 'produtos' no Cloud Firestore (ID: {produto_id})...")
    doc_firestore = db.collection('produtos').document(produto_id).get()
    
    assert doc_firestore.exists, f"Documento {produto_id} não existe no Firestore!"
    dados_firestore = doc_firestore.to_dict()
    
    print("   [OK] Documento recuperado diretamente do Firebase:")
    for k, v in dados_firestore.items():
        print(f"        • {k}: {v}")

    # Asserts de conformidade dos dados
    assert dados_firestore["produtor_id"] == uid_usuario
    assert dados_firestore["nome"] == "Morango Orgânico Padrão CEASA Caixa 1.2kg"
    assert dados_firestore["categoria"] == "fruta"
    assert dados_firestore["preco_kg"] == 18.50
    assert dados_firestore["quantidade_kg"] == 300.0
    assert "criado_em" in dados_firestore

    # 4. Simular Consulta do Mural no Front-end (carregarOfertas())
    print("\n4. Simulando carregamento do Mural no Front-end com o novo lote...")
    res_mural = client.post('/mcp/v1/executar', json={
        "tool": "listar_ofertas",
        "parameters": {"categoria": "fruta"}
    })
    ofertas = res_mural.get_json().get("result", [])
    nomes_ofertas = [p["nome"] for p in ofertas]
    
    assert "Morango Orgânico Padrão CEASA Caixa 1.2kg" in nomes_ofertas, "O produto recém-cadastrado não apareceu na lista do mural!"
    print(f"   [OK] Produto apareceu com sucesso no Mural de Ofertas do Front-end!")

    print("\n" + "=" * 70)
    print("[SUCESSO TOTAL] AS INFORMAÇÕES DO FRONT-END ESTÃO SENDO GRAVADAS NO FIREBASE!")
    print("=" * 70)
    return True

if __name__ == "__main__":
    sucesso = testar_fluxo_frontend_para_firestore()
    sys.exit(0 if sucesso else 1)
