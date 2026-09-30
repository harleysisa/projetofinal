"""
Script para popular o Cloud Firestore com dados iniciais do CEASA Virtual.
Cria produtos de exemplo e manuais de qualidade (RAG).
"""
import os
import sys

# Garante suporte a UTF-8 no stdout do Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.environ.get("FIREBASE_KEY_PATH", os.path.join(BASE_DIR, "firebase-key.json"))

if not firebase_admin._apps:
    if os.path.exists(KEY_PATH):
        cred = credentials.Certificate(KEY_PATH)
        firebase_admin.initialize_app(cred)
    else:
        firebase_admin.initialize_app()

db = firestore.client()

MANUAIS_QUALIDADE = [
    {
        "categoria": "fruta",
        "produto": "Banana Prata",
        "conteudo": "Norma Tecnica CEASA para Banana Prata: Comercializacao em caixas plasticas de 20kg higienizadas. Grau de maturacao ideal para atacado: Grau 2 a 4. Ausencia de danos mecanicos graves."
    },
    {
        "categoria": "legume",
        "produto": "Tomate Italiano",
        "conteudo": "Classificacao do Tomate Italiano: Caixa padrao tipo K (20kg a 22kg). Calibres aceitos: Extra A (> 60mm) e Extra AA (> 70mm). Coloracao padrao 'de vez' (amarelado a rosado)."
    },
    {
        "categoria": "hortaliça",
        "produto": "Alface Americana",
        "conteudo": "Padrao de Qualidade Alface Americana: Caixas contendo 12 a 18 cabecas compactas (6kg a 8kg por caixa). Folhas limpas sem queima de borda e sem sinais de mildio."
    },
    {
        "categoria": "legume",
        "produto": "Cenoura",
        "conteudo": "Normas da Cenoura CEASA: Raizes lavadas, sem ramagens, sem bifurcacoes. Classificacao: Tipo 3A (18 a 22 cm) e Tipo 2A (14 a 18 cm). Embalagem em sacos de 20kg."
    }
]

PRODUTOS_INICIAIS = [
    {
        "produtor_id": "produtor_sitio_esperanca",
        "nome": "Banana Prata Climatizada",
        "categoria": "fruta",
        "preco_kg": 4.80,
        "quantidade_kg": 450.0,
        "criado_em": firestore.SERVER_TIMESTAMP
    },
    {
        "produtor_id": "produtor_fazenda_boa_vista",
        "nome": "Tomate Italiano Extra AA",
        "categoria": "legume",
        "preco_kg": 5.20,
        "quantidade_kg": 800.0,
        "criado_em": firestore.SERVER_TIMESTAMP
    },
    {
        "produtor_id": "produtor_hidroponia_verde",
        "nome": "Alface Americana Hidroponica",
        "categoria": "hortaliça",
        "preco_kg": 6.50,
        "quantidade_kg": 180.0,
        "criado_em": firestore.SERVER_TIMESTAMP
    },
    {
        "produtor_id": "produtor_sitio_esperanca",
        "nome": "Cenoura Lavada Selecionada 3A",
        "categoria": "legume",
        "preco_kg": 3.90,
        "quantidade_kg": 600.0,
        "criado_em": firestore.SERVER_TIMESTAMP
    }
]

def popular_banco():
    print("Iniciando povoamento do Firestore...")
    
    # 1. Inserir Manuais de Qualidade
    manuais_ref = db.collection('manuais_qualidade')
    for m in MANUAIS_QUALIDADE:
        manuais_ref.add(m)
    print(f"[OK] {len(MANUAIS_QUALIDADE)} normas tecnicas inseridas em 'manuais_qualidade'.")

    # 2. Inserir Produtos Iniciais
    produtos_ref = db.collection('produtos')
    for p in PRODUTOS_INICIAIS:
        produtos_ref.add(p)
    print(f"[OK] {len(PRODUTOS_INICIAIS)} lotes iniciais inseridos em 'produtos'.")
    
    print("[SUCESSO] Cloud Firestore inicializado com sucesso!")

if __name__ == '__main__':
    popular_banco()
