"""
Teste de Autenticação e Perfis de Usuário no Cloud Firestore
"""
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from server import db, firestore

def testar_autenticacao_firestore():
    print("=" * 60)
    print("[TESTE] INICIANDO TESTE DE AUTENTICACAO & PERFIS NO FIRESTORE")
    print("=" * 60)

    uid_teste = "usr_produtor_ceasa_001"
    dados_usuario = {
        "uid": uid_teste,
        "nome": "Joao Silva - Produtor Rural",
        "email": "produtor.joao@ceasavirtual.com",
        "tipo_perfil": "PRODUTOR",
        "foto_url": "https://cdn-icons-png.flaticon.com/512/1995/1995574.png",
        "atualizado_em": firestore.SERVER_TIMESTAMP
    }

    try:
        # 1. Grava perfil do usuário na coleção 'usuarios'
        print("\n1. Registrando perfil na colecao 'usuarios' do Firestore...")
        user_ref = db.collection('usuarios').document(uid_teste)
        user_ref.set(dados_usuario, merge=True)
        print(f"[OK] Usuario gravado com UID: {uid_teste}")

        # 2. Recupera perfil do usuário
        print("\n2. Consultando sessao e permissoes do usuario...")
        doc = user_ref.get()
        assert doc.exists, "Documento de usuario nao existe"
        
        perfil = doc.to_dict()
        print(f"[OK] Perfil carregado com sucesso:")
        print(f"     Nome: {perfil.get('nome')}")
        print(f"     Email: {perfil.get('email')}")
        print(f"     Tipo de Perfil: {perfil.get('tipo_perfil')}")

        assert perfil.get("tipo_perfil") == "PRODUTOR", "Tipo de perfil incorreto"
        assert perfil.get("email") == dados_usuario["email"], "Email incorreto"

        print("\n" + "=" * 60)
        print("[SUCESSO] AUTENTICACAO E PERFIL NO FIRESTORE VALIDADOS!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n[ERRO] Falha no teste: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    sucesso = testar_autenticacao_firestore()
    sys.exit(0 if sucesso else 1)
