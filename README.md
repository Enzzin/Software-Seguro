# BrazucaPhish - Plataforma de Conscientização sobre Phishing

BrazucaPhish é uma plataforma de código aberto projetada para ajudar empresas e equipes de segurança a conduzir campanhas de simulação de phishing. Com ela, é possível gerar links de phishing rastreáveis, enviá-los para alvos específicos e monitorar os cliques em um dashboard intuitivo.

A plataforma também inclui um chatbot integrado com o Ollama para responder a perguntas gerais.

## ✨ Funcionalidades

* **Autenticação Segura:** Sistema de registro e login de usuários utilizando AWS Cognito.
* **Criação de Campanhas:** Crie campanhas de phishing com nomes, descrições e URLs de destino personalizadas.
* **Geração de Links:** Gere links de phishing únicos para cada e-mail alvo.
* **Envio de E-mails:** Envio automático dos links de phishing para os alvos.
* **Dashboard Interativo:** Visualize estatísticas agregadas e por campanha, incluindo número de cliques e vítimas únicas.
* **Rastreamento Detalhado:** Colete informações sobre cada clique, como endereço IP, User-Agent, geolocalização e referer.
* **Exportação de Dados:** Exporte os resultados de uma campanha para um arquivo CSV.
* **Chatbot Inteligente:** Um assistente de IA (Ollama 3.2) para responder a dúvidas.

## 🛠️ Arquitetura e Tecnologias

O projeto é conteinerizado com Docker e utiliza as seguintes tecnologias:

* **Backend:** Flask (Python)
* **Frontend:** HTML, CSS, JavaScript, Bootstrap
* **Banco de Dados:** PostgreSQL
* **ORM:** SQLAlchemy com Flask-SQLAlchemy
* **Migrações de Banco:** Alembic com Flask-Migrate
* **Autenticação:** AWS Cognito
* **Servidor de E-mail:** Qualquer servidor SMTP (configurável via variáveis de ambiente).
* **IA (Chatbot):** Ollama
* **Servidor Web:** Nginx (como proxy reverso)

## 🚀 Instalação e Execução (com Docker)

### Pré-requisitos

* Docker e Docker Compose instalados.
* Uma conta na AWS com um User Pool no Cognito configurado.
* Um servidor SMTP para o envio de e-mails.
* Ollama rodando, se desejar usar o chatbot.

### Passos para Instalação

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/Enzzin/Software-Seguro.git](https://github.com/Enzzin/Software-Seguro.git)
    cd Software-Seguro
    ```

2.  **Configure as variáveis de ambiente:**
    Copie o arquivo `.env.example` para `.env` e preencha com suas credenciais.
    ```bash
    cp .env.example .env
    ```
    Edite o arquivo `.env` com suas informações.

3.  **Construa e execute os containers:**
    ```bash
    docker-compose up --build -d
    ```

4.  **Acesse a aplicação:**
    A aplicação estará disponível em `http://localhost:8000`

## 🔒 Considerações de Segurança

Este projeto foi desenvolvido com foco em práticas de desenvolvimento seguro, prevenindo as principais vulnerabilidades da web.

* [cite_start]**CWE-522 (Credenciais Insuficientemente Protegidas):** A aplicação utiliza o **Amazon Cognito** para todo o gerenciamento de contas, delegando o armazenamento seguro de senhas e o fluxo de autenticação para um serviço especializado da AWS. 
* [cite_start]**CWE-798 (Uso de Credenciais "Hard-coded"):** Todas as credenciais e segredos da aplicação são gerenciados através de um arquivo **`.env`**, que é carregado no ambiente de execução e mantido fora do controle de versão do Git. 
* [cite_start]**CWE-89 (SQL Injection):** O uso do **SQLAlchemy ORM** em todas as interações com o banco de dados impossibilita a ocorrência de injeção de SQL, pois todas as entradas são devidamente parametrizadas. 
* [cite_start]**CWE-223 (Omissão de Informação de Segurança Relevante):** O sistema de **logs** está configurado para registrar eventos importantes da aplicação sem revelar informações sensíveis do usuário ou da sessão, garantindo a rastreabilidade sem comprometer a privacidade. 
* **CWE-284 (Controle de Acesso Inadequado):** A rota `/api/phish/stats` garante que um usuário só possa acessar os dados de suas próprias campanhas. [cite_start]Isso é feito verificando a sessão do usuário e filtrando as consultas ao banco de dados com base no e-mail do proprietário, impedindo o acesso a dados de outros usuários. 

---
_© 2025 BrazucaPhish_
