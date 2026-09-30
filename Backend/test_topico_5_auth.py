"""
Teste de Validação: Tópico 5 do GEMINI.md (Autenticação e Guarda de Rotas)
"""
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from server import app, db

def testar_topico_5():
    print("=" * 65)
    print("[TESTE] VALIDACAO DO TOPICO 5: AUTENTICACAO OBRIGATORIA & PERFIS")
    print("=" * 65)

    client = app.test_client()

    # 1. Teste: Tentar cadastrar lote sem autenticação / sem produtor_id
    print("\n1. Testando bloqueio de cadastro para usuario deslogado...")
    res_bloqueio = client.post('/mcp/v1/executar', json={
        "tool": "cadastrar_produto",
        "parameters": {
            "nome": "Abacaxi Pérola",
            "categoria": "fruta",
            "preco_kg": 5.0,
            "quantidade_kg": 100
        }
    })
    print(f"   Status HTTP retornado: {res_bloqueio.status_code}")
    print(f"   Resposta: {res_bloqueio.get_json()}")
    assert res_bloqueio.status_code == 403, "Deveria bloquear usuario deslogado com status 403"
    print("[OK] Guarda de rota bloqueou usuario deslogado com sucesso.")

    # 2. Teste: Autenticar usuário no endpoint /api/auth/login
    print("\n2. Testando registro e login de usuario na colecao 'usuarios'...")
    res_login = client.post('/api/auth/login', json={
        "uid": "usr_google_produtor_777",
        "nome": "Marcos Produtor Google",
        "email": "marcos.produtor@gmail.com",
        "tipo_perfil": "PRODUTOR",
        "foto_url": "https://lh3.googleusercontent.com/photo_demo"
    })
    print(f"   Status HTTP retornado: {res_login.status_code}")
    assert res_login.status_code == 200, "Login deveria retornar status 200"
    print(f"[OK] Usuario autenticado e gravado no Firestore.")

    # 3. Teste: Cadastro autenticado como PRODUTOR
    print("\n3. Testando cadastro de lote com perfil de Produtor autenticado...")
    res_cadastro = client.post('/mcp/v1/executar', json={
        "tool": "cadastrar_produto",
        "parameters": {
            "produtor_id": "usr_google_produtor_777",
            "nome": "Abacaxi Pérola Extra",
            "categoria": "fruta",
            "preco_kg": 5.50,
            "quantidade_kg": 250
        }
    })
    print(f"   Status HTTP retornado: {res_cadastro.status_code}")
    dados_cadastro = res_cadastro.get_json()
    print(f"   Resposta: {dados_cadastro}")
    assert res_cadastro.status_code == 200 and dados_cadastro.get("success") == True, "Cadastro deveria ser autorizado"
    print(f"[OK] Lote cadastrado com sucesso. ID: {dados_cadastro['result']['produto_id']}")

    print("\n" + "=" * 65)
    print("[SUCESSO] TOPICO 5 DO GEMINI.MD VALIDADO COM EXITO TOTAL!")
    print("=" * 65)
    return True

if __name__ == '__main__':
    sucesso = testar_topico_5()
    sys.exit(0 if sucesso else 1)
