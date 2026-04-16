# Coffee Co-lab ☕️

**Coffee Co-lab** é uma plataforma de "banco de escambo moderno" que conecta cafeterias artesanais a pessoas em busca de experiências reais para fortalecer seus portfólios (designers, fotógrafos, social media, devs).

A premissa é simples: em vez de dinheiro, a moeda de troca é a experiência e o produto.\
- **A Cafeteria** recebe serviços digitais de alta qualidade (fotos do menu, artes para Instagram) pagando com o custo marginal do café e seu espaço.\
- **O Talento Local (Prestador)** recebe uma oportunidade de trabalhar com clientes reais, ganha um case para o portfólio oficial, e ainda consome na cafeteria através de um sistema de "créditos" e "tokens".

---

## 🚀 Funcionalidades Principais

### Autenticação & Segurança
- **Cadastro de Usuários:** Perfis separados para `CAFE_ADMIN` (Cafeterias) e `PROVIDER` (Talentos Locais).
- **Verificação de E-mail:** Ao se cadastrar, o usuário recebe um e-mail com link verificado por token assinado (válido por 24h). Conta só é ativada após confirmação.
- **Reenvio de Verificação:** Usuários que não receberam o e-mail podem solicitar novo envio.
- **Esqueceu a Senha / Redefinição:** Fluxo completo de "Forgot Password" com token seguro (válido por 2h), e-mail HTML estilizado e redefinição via formulário.
- **Sessões Seguras:** Gerenciamento de sessão via middleware (Starlette `SessionMiddleware`), proteção por role-based access (`CAFE_ADMIN` vs `PROVIDER`).
- **Flash Messages:** Feedback via mensagens flash nas sessões (erro de login, sucesso ao redefinir senha, etc.).
- **Hashing de Senha:** bcrypt via Passlib.

### Onboarding de Cafeterias
- **Cadastro de Perfil:** As cafeterias informam nome, site e Instagram. O perfil recebe um slug único.
- **Status de Verificação:** O perfil passa por um status `is_verified` até ser aprovado, garantindo um ambiente seguro.
- **Vínculo Usuário-Café:** O admin é vinculado à cafeteria via `cafe_id` ao registrar o perfil.

### Mural de Missões (Core Loop)
- **Criar Missão:** A cafeteria publica demandas reais com título, descrição e valor em créditos.
- **Aceitar Missão:** Prestadores visualizam missões abertas (`OPEN`) e escolhem aceitar.
- **Marcar Concluída:** O prestador marca como `DONE` quando finaliza o serviço (com campo opcional de prova de entrega).
- **Avaliar & Aprovar:** O admin da cafeteria avalia (nota 1–5 + texto de recomendação), define se permite uso no portfólio público, e aprova (`APPROVED`).
- **Ciclo Completo:** Ao aprovar, o sistema automaticamente: atualiza o status, cria a avaliação (`Rating`), credita os créditos (`Transaction EARN`) e gera o item de portfólio.

### Carteira & Sistema de Créditos (Ledger)
- **Saldo:** Calculado como `SUM(EARN) - SUM(SPEND)` a partir do histórico de transações.
- **Extrato:** Visualização completa das transações do prestador.
- **Geração de Token (QR Code):** O prestador gera um token seguro (SHA-256 hash + `secrets.token_urlsafe`) com validade de 5 minutos, convertido em QR Code para apresentar no balcão.

### Resgate de Créditos (Redeem)
- **Link de Resgate:** Cada QR Code gera um link `/redeem/{token}` com detalhes do token (prestador, valor, status).
- **Confirmação pelo Caixa:** O admin da cafeteria (logado) visualiza o token e confirma o consumo, gerando uma transação `SPEND`.
- **Validação de Segurança:** Tokens expirados ou já usados são bloqueados automaticamente.
- **Verificação de Saldo:** O sistema impede a geração de tokens com valor acima do saldo disponível.

### Portfólio Público
- **Geração Automática:** Itens de portfólio são criados automaticamente ao aprovar uma missão.
- **Visibilidade Controlada:** O prestador pode alternar entre público e privado para cada item.
- **Página Pública:** URL pública `/u/{id}/portfolio` acessível sem login, exibindo projetos e nota média.
- **Nota Média:** Calculada dinamicamente a partir das avaliações recebidas.

### Landing Page
- **Missões em Destaque:** A homepage exibe até 6 missões abertas de cafeterias verificadas, ordenadas por data.
- **Detecção de Sessão:** Usuários logados veem conteúdo contextualizado.

### E-mails Transacionais
- **Templates HTML Estilizados:** E-mails de verificação e redefinição de senha com design profissional (gradientes, tipografia, dark mode).
- **Modo Dev:** Quando SMTP não está configurado, links são impressos no console para facilitar o desenvolvimento local.
- **Integração SMTP:** Suporte a Mailtrap (dev) e qualquer servidor SMTP via configuração em `.env`.

---

## 🛠 Tech Stack

A arquitetura foi projetada para ser leve, rápida e amigável:

| Camada | Tecnologia |
|---|---|
| **Backend** | Python + FastAPI (tipagem estática, async) |
| **Banco de Dados** | PostgreSQL (Docker Compose) + SQLAlchemy ORM |
| **Frontend / UI** | HTMX + Jinja2 Templates + Vanilla CSS |
| **Migrations** | Alembic |
| **Autenticação** | Sessions (Starlette) + bcrypt + itsdangerous |
| **E-mails** | fastapi-mail (Mailtrap / SMTP) |
| **QR Code** | qrcode + Pillow |
| **Monitoramento** | Sentry SDK (opcional) |
| **Testes** | pytest + pytest-asyncio + httpx + aiosmtpd |
| **Linting** | Ruff |
| **Deploy** | Docker |

### Arquitetura de Camadas

```
app/
├── core/         # Config, DB, segurança, tokens
├── models/       # SQLAlchemy models (User, Cafe, Mission, Rating, Transaction, Redeem, Portfolio)
├── repos/        # Camada de repositório (acesso a dados)
├── services/     # Lógica de negócio (AuthService, MissionService, RedeemService, EmailService)
├── web/          # Rotas FastAPI + dependências de autenticação
├── templates/    # Jinja2 HTML templates (17 páginas)
└── static/       # CSS, imagens, assets
```

---

## 💻 Como Rodar o Projeto Localmente

Nós criamos um script facilitador (`run_local.sh`) que cuida de praticamente tudo para você (gerencia o banco pelo Docker, cria o ambiente virtual, instala dependências e roda as migrações).

### Pré-requisitos
- **Docker e Docker Compose** instalados e rodando (Ex: Docker Desktop aberto).
- **Python 3.9+** instalado no sistema.
- **Git** (opcional para clonar o projeto).

### Passo a Passo

1. **Clone o repositório e acesse a pasta:**
   ```bash
   git clone https://github.com/ilaraca/coffee-colab.git
   cd coffee-colab
   ```

2. **Configure as variáveis de ambiente:**
   ```bash
   cp .env.example .env
   # Edite o .env com suas credenciais (SMTP, SECRET_KEY, etc.)
   ```

3. **Dê permissão de execução ao script (Linux/Mac):**
   ```bash
   chmod +x run_local.sh
   ```

4. **Inicie o servidor localmente:**
   Pela primeira vez (ou sempre que quiser reinstalar as dependências e popular o banco de dados inicial), use a flag `--setup`:
   ```bash
   ./run_local.sh --setup
   ```
   *O script vai cuidar do Docker do Postgres, criar o `venv`, rodar o Alembic e alimentar o banco (Seed).*
   
   Para as vezes seguintes (onde o banco já está pronto), basta rodar sem a flag:
   ```bash
   ./run_local.sh
   ```

5. **Acesse a Plataforma:**
   Abra seu navegador em: **[http://localhost:8000](http://localhost:8000)**

---

## 🧪 Testes Automatizados

O projeto inclui uma suíte de testes automatizados com **pytest**:

```bash
# Rodar todos os testes
python -m pytest -v

# Ou usar o script de guardrails (lint + testes)
./verify.sh
```

### Cobertura de Testes

| Arquivo | O que testa |
|---|---|
| `test_smoke.py` | Healthcheck básico da aplicação |
| `test_auth_flows.py` | Registro, login (verificado/não verificado), verificação de e-mail, forgot/reset password (7 testes) |
| `test_email_integration.py` | Construção de mensagens de e-mail, integração SMTP (4 testes, 2 skip sem SMTP) |
| `test_onboarding_flows.py` | Rotas protegidas, registro de admin/café, verificação, perfil do café (4 testes) |

### Guardrails (verify.sh)

Antes de cada push, execute:
```bash
./verify.sh
```
Isso roda o **Ruff** (linting) e o **pytest** automaticamente.

---

## 🔑 Credenciais de Teste (Seed)

Após rodar o comando com `--setup`, um banco de dados modelo será populado. Você pode entrar usando a opção "Já tem uma conta? Entrar" na página inicial:

| Perfil | Email de Login | Senha |
|---|---|---|
| **Cafeteria (Admin Verificado)** | `admin@modocafe.local` | `Admin123!` |
| **Talento Local (Prestador)** | `provider@modocafe.local` | `Provider123!` |

*(Ou sinta-se à vontade para clicar em "Começar Agora" e testar todo o fluxo de cadastro real do zero!)*

---

## 📧 Configuração de E-mail

| Variável | Descrição | Valor padrão |
|---|---|---|
| `MAIL_USERNAME` | Usuário SMTP | *(vazio — modo dev)* |
| `MAIL_PASSWORD` | Senha SMTP | *(vazio — modo dev)* |
| `MAIL_SERVER` | Servidor SMTP | `sandbox.smtp.mailtrap.io` |
| `MAIL_PORT` | Porta SMTP | `587` |
| `MAIL_STARTTLS` | STARTTLS habilitado | `True` |
| `MAIL_FROM` | Remetente | `noreply@coffeecolab.com` |

> **Modo Dev:** Quando `MAIL_USERNAME` e `MAIL_PASSWORD` não estão configurados, os links de verificação e redefinição de senha são impressos diretamente no console do servidor.

---

## 📊 Monitoramento (Opcional)

Configure a variável `SENTRY_DSN` no `.env` para ativar o rastreamento de erros via [Sentry](https://sentry.io):

```env
SENTRY_DSN=https://your-dsn@sentry.io/project-id
```
