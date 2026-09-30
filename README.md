# 🌱 CEASA Virtual - Full-Stack PWA com IA & MCP

Plataforma PWA para comercialização de hortifrúti diretamente entre produtores rurais, lojistas e clientes finais, integrando inteligência artificial (Gemini) através do protocolo MCP (*Model Context Protocol*) e RAG no Cloud Firestore.

---

## 📁 Estrutura do Projeto

```text
ProjetoFinal/
├── Backend/
│   ├── server.py              # API Flask com Servidor MCP & Chat RAG
│   ├── seed_data.py           # Script para popular Firestore com dados iniciais
│   └── firebase-key.json      # Chave de serviço do Firebase Admin SDK
├── Frontend/
│   ├── index.html             # Interface PWA com Tailwind CSS, Google Auth e Chat
│   ├── manifest.json          # Manifesto para instalação PWA
│   └── sw.js                  # Service Worker (Cache offline)
├── GEMINI.md                  # Especificação e arquitetura do projeto
├── agente.md                  # Instrução de Sistema do Assistente Comercial
├── requirements.txt           # Dependências Python do projeto
├── testes.http                # Testes de integração REST Client
└── .gitignore                 # Proteção de credenciais e venv
```

---

## 🚀 Como Executar Localmente

### 1. Instalar as dependências Python
```bash
pip install -r requirements.txt
```

### 2. (Opcional) Popular o banco com dados de exemplo
```bash
python Backend/seed_data.py
```

### 3. Iniciar o Servidor Backend (Flask + MCP)
```bash
python Backend/server.py
```
*O servidor iniciará em `http://127.0.0.1:5000`.*

### 4. Abrir o Frontend (PWA)
Basta abrir o arquivo `Frontend/index.html` em qualquer navegador ou utilizar uma extensão como *Live Server*.

---

## 🛠️ Ferramentas MCP Disponíveis

| Ferramenta | Parâmetros | Descrição |
| :--- | :--- | :--- |
| `cadastrar_produto` | `produtor_id`, `nome`, `categoria`, `preco_kg`, `quantidade_kg` | Grava um novo lote na coleção `produtos`. |
| `listar_ofertas` | `categoria` *(opcional)* | Consulta lotes disponíveis no mercado. |
| `consultar_qualidade` | `duvida` ou `produto` | Realiza busca RAG nas normas técnicas e manuais de classificação. |

---

## 🌐 Deploy no PythonAnywhere & Firebase

1. **Backend no PythonAnywhere:**
   - Suba o conteúdo da pasta `Backend/` e o `requirements.txt`.
   - Configure o arquivo WSGI do PythonAnywhere apontando para `app` em `server.py`.
   - Adicione `firebase-key.json` no diretório do app.
2. **Frontend no Firebase Hosting:**
   - Execute `firebase init hosting` e selecione a pasta `Frontend/` como diretório público.
   - Execute `firebase deploy --only hosting`.
