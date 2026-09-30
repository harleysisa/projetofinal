# 📋 Prompt de Especificação da Aplicação: CEASA Virtual

## 🎯 Objetivo
Desenvolver uma aplicação PWA full-stack para comercialização de hortifrúti diretamente entre produtores rurais, lojistas e clientes finais, integrando inteligência artificial (Gemini) através do protocolo MCP (*Model Context Protocol*) e RAG Híbrido no Cloud Firestore.

---

## 🏗️ Arquitetura do Sistema
┌─────────────────────────────────────────────────────────────┐
│                   FRONT-END (PWA Web)                       │
│    Vanilla JS + Tailwind CSS + Firebase Auth (Google)      │
│              Hospedado no Firebase Hosting                  │
└──────────────────────────────┬──────────────────────────────┘
│ Requisições HTTP / REST
┌──────────────────────────────▼──────────────────────────────┐
│                   BACK-END (API Python)                     │
│          Servidor Flask com MCP no PythonAnywhere           │
└──────────────────────────────┬──────────────────────────────┘
│
┌───────────────┴───────────────┐
▼                               ▼
┌───────────────────┐           ┌───────────────────┐
│  Cloud Firestore  │           │   Motor Gemini    │
│  (RAG Estruturado │           │ (Prompts Markdown │
│   & Vetorial)     │           │   + Ferramentas)  │
└───────────────────┘           └───────────────────┘
---

## 🎨 1. ESPECIFICAÇÃO DO FRONT-END (PWA)

### **Tecnologias**
*   **Interface:** HTML5 semântico estilizado com **Tailwind CSS** (via CDN).
*   **Lógica:** **Vanilla JavaScript** (ES6+) modular e leve (sem frameworks como React/Vue).
*   **Autenticação:** **Firebase Auth** (Provedor Google Sign-In).
*   **Distribuição:** **PWA** (*Manifest.json* + *Service Worker*) hospedado no **Firebase Hosting**.

### **Telas e Funcionalidades**
1.  **Tela de Boas-Vindas & Login (Bloqueio de Acesso):**
    *   Exibir resumo da plataforma e botão "Entrar com Google".
    *   Restringir funcionalidades de cadastro e pedidos a usuários autenticados.
2.  **Painel do Produtor Rural (Requer Perfil Produtor):**
    *   Formulário para cadastro de lotes: `Nome do Produto`, `Categoria` (Frutas, Legumes, Hortaliças), `Preço por Kg` e `Quantidade Total (Kg)`.
3.  **Mural do Mercado (Lojistas e Clientes):**
    *   Listagem dinâmica de produtos disponíveis via requisição `POST` ao Back-end.
    *   Filtros por categoria e botão para realização de pedidos.
4.  **Interface de Chat com IA (Assistente Comercial):**
    *   Caixa de diálogo interativa para cotar preços, consultar padrões de qualidade e fazer pedidos via linguagem natural.

---

## ⚙️ 2. ESPECIFICAÇÃO DO BACK-END (API Python + MCP)

### **Tecnologias**
*   **Lógica de Negócio:** **Python** com micro-framework **Flask** (ou FastAPI) e `flask-cors`.
*   **Banco de Dados:** **Firebase Admin SDK** (`firebase-admin`, `google-cloud-firestore`).
*   **Protocolo de IA:** Servidor **MCP** (*Model Context Protocol*) expondo ferramentas para o Gemini.

### **Rotas da API**
*   `POST /mcp/v1/executar`: Endpoint central do MCP responsável por receber o nome da ferramenta e seus parâmetros em JSON, executar a instrução e retornar a resposta.

### **Ferramentas MCP a Implementar**
1.  `cadastrar_produto(produtor_id, nome, categoria, preco_kg, quantidade_kg)`:
    *   **Ação:** Grava um novo documento na coleção `produtos` do Cloud Firestore.
2.  `listar_ofertas(categoria=None)`:
    *   **Ação:** Realiza RAG Estruturado buscando os lotes ativos na coleção `produtos`.
3.  `consultar_qualidade(duvida, produto=None)`:
    *   **Ação:** Realiza RAG Clássico (busca por similaridade vetorial via `find_nearest` com `text-embedding-004`) na coleção `manuais_qualidade` do Firestore.

---

## 🗄️ 3. ESTRUTURA DO BANCO DE DADOS (Cloud Firestore)

*   **Coleção `produtos` (RAG Estruturado):**
    ```json
    {
      "produtor_id": "string",
      "nome": "string",
      "categoria": "string",
      "preco_kg": 0.00,
      "quantidade_kg": 0.0,
      "criado_em": "TIMESTAMP"
    }
    ```
*   **Coleção `manuais_qualidade` (RAG Vetorial Clássico):**
    ```json
    {
      "categoria": "string",
      "produto": "string",
      "conteudo": "string",
      "embedding": "VECTOR(768)"
    }
    ```

---

## ✅ 4. CHECKLIST DE VALIDAÇÃO: PRONTO PARA PYTHONANYWHERE

Antes de realizar o deploy do Back-end no **PythonAnywhere**, verifique se todos os itens abaixo estão atendidos:

- [ ] **Variáveis e Credenciais:** O arquivo `firebase-key.json` está na pasta do projeto e incluído no `.gitignore`.
- [ ] **Arquivo `requirements.txt` criado com as dependências exatas:**
  ```text
  Flask
  Flask-Cors
  firebase-admin
  google-cloud-firestore
  google-generativeai

## 🔒5. Autenticação obrigatoria via Conta Google (Firebase Auth)

Para garantir a segurança das transações, a integridade dos dados e a identificação dos perfis de uso no **CEASA Virtual**, o acesso à aplicação é estritamente controlado via **Firebase Authentication** com o provedor de login do Google.

### 1. Regras de Controle de Acesso (Guardas de Rota)
- **Estado Não Autenticado (Visitante/Deslogado):**
  - O usuário visualiza apenas a tela inicial de boas-vindas (*Landing Page*) informando a necessidade de login.
  - Todas as funcionalidades do sistema (Mural de Ofertas, Cadastro de Produtos e Chat com IA) permanecem **bloqueadas**.
  - É exibido o botão proeminente **"Entrar com Google"**.
- **Estado Autenticado (Usuário Logado):**
  - O sistema lê os dados do perfil fornecidos pelo Google (`displayName`, `email`, `photoURL` e `uid`).
  - O token JWT gerado pelo Firebase deve ser enviado no cabeçalho das requisições para validar as chamadas na API Python no backend.

### 2. Mapeamento de Permissões por Perfil
Após o login com a Conta Google, as permissões no sistema são distribuídas da seguinte forma:

| Ação no Sistema | Exige Autenticação Google? | Perfil Exigido |
| :--- | :---: | :---: |
| **Visualizar Ofertas Ativas** |  Sim | Qualquer usuário logado |
| **Consultar Manual de Qualidade (RAG)** |  Sim | Qualquer usuário logado |
| **Realizar Pedido de Compra** |  Sim | Lojista / Cliente Final |
| **Cadastrar / Ofertar Lotes** |  Sim | Produtor Rural |

### 3. Exemplo de Implementação no Front-end (Vanilla JS)
```javascript
// Monitor de estado de autenticação do Firebase
firebase.auth().onAuthStateChanged((user) => {
  if (user) {
    // Usuário autenticado com conta Google
    console.log("Usuário logado:", user.displayName, user.email);
    liberarAcessoAplicacao(user);
  } else {
    // Usuário não autenticado -> Bloqueia a interface
    bloquearInterfaceEExibirLogin();
  }
});

// Função acionada pelo botão "Entrar com Google"
function autenticarComGoogle() {
  const provider = new firebase.auth.GoogleAuthProvider();
  firebase.auth().signInWithPopup(provider)
    .then((result) => {
      console.log("Login realizado com sucesso!");
    })
    .catch((error) => {
      console.error("Erro na autenticação:", error);
    });
}