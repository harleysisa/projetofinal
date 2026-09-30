"""
Teste Automatizado de Autenticação com Firebase Admin SDK
"""
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import firebase_admin
from firebase_admin import credentials, auth

KEY_PATH = os.environ.get("FIREBASE_KEY_PATH", os.path.join(BASE_DIR, "firebase-key.json"))

if not firebase_admin._apps:
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred)

def testar_autenticacao():
    print("=" * 60)
    print("[TESTE] INICIANDO TESTE DE AUTENTICACAO COM FIREBASE ADMIN")
    print("=" * 60)

    uid_teste = "usr_produtor_ceasa_001"
    email_teste = "produtor.joao@ceasavirtual.com"
    nome_teste = "Joao Silva - Produtor Rural"

    try:
        # 1. Cria ou recupera usuário no Firebase Auth
        print("\n1. Verificando/Criando usuario de teste no Firebase Auth...")
        try:
            user = auth.get_user(uid_teste)
            print(f"[OK] Usuario existente encontrado: UID={user.uid}, Email={user.email}")
        except auth.UserNotFoundError:
            user = auth.create_user(
                uid=uid_teste,
                email=email_teste,
                display_name=nome_teste
            )
            print(f"[OK] Novo usuario criado com sucesso: UID={user.uid}, Email={user.email}")

        # 2. Gera um Custom Token para login autenticado
        print("\n2. Gerando Custom Token de autenticacao...")
        custom_token = auth.create_custom_token(uid_teste, {"perfil": "PRODUTOR", "nome": nome_teste})
        print(f"[OK] Token JWT seguro gerado: {custom_token[:35].decode('utf-8')}... (truncado)")

        # 3. Define Custom User Claims (Perfil de Produtor)
        print("\n3. Atribuindo claims de perfil (Role-Based Access)...")
        auth.set_custom_user_claims(uid_teste, {"role": "PRODUTOR", "ativo": True})
        
        user_atualizado = auth.get_user(uid_teste)
        print(f"[OK] Claims confirmadas no Firebase: {user_atualizado.custom_claims}")
        assert user_atualizado.custom_claims.get("role") == "PRODUTOR", "Claim de role invalida"

        print("\n" + "=" * 60)
        print("[SUCESSO] SISTEMA DE AUTENTICACAO VALIDADO COM EXITO!")
        print(f"   - Projeto: ceasavirtual")
        print(f"   - Usuario: {user_atualizado.display_name} ({user_atualizado.email})")
        print(f"   - Perfil: {user_atualizado.custom_claims.get('role')}")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n[ERRO] Falha no teste de autenticacao: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    sucesso = testar_autenticacao()
    sys.exit(0 if sucesso else 1)
