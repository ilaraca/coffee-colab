# Coffee Co-lab MVP ☕️

Plataforma Web2 de "permuta" para cafeterias e prestadores de serviço.
MVP funcional rodando local via Docker + FastAPI + HTMX.

## Pré-requisitos
- Docker & Docker Compose
- Python 3.9+ (Recomendado usar `venv`)

## Como Rodar

1. **Clone e Setup Inicial:**
   ```bash
   # Crie e ative o ambiente virtual
   python3 -m venv venv
   source venv/bin/activate
   
   # Instale dependências
   pip install -r requirements.txt
   ```

2. **Subir Banco de Dados (Postgres):**
   ```bash
   docker-compose up -d
   ```

3. **Migrações e Seeds:**
   ```bash
   # Criar tabelas
   alembic upgrade head
   
   # Popular dados iniciais (Cafe, Admin, Provider)
   python scripts/seed.py
   ```

4. **Rodar Aplicação:**
   ```bash
   uvicorn app.main:app --reload
   ```
   Acesse: [http://localhost:8000](http://localhost:8000)

## Credenciais Demo

| Role | Email | Senha |
|------|-------|-------|
| **Cafeteria (Admin)** | `admin@modocafe.local` | `Admin123!` |
| **Prestador** | `provider@modocafe.local` | `Provider123!` |

## Fluxo de Teste Manual (Passo a Passo)

1. **Login Cafeteria:**
   - Acesse `/login`. Entre com as credenciais de Admin.
   - Vá para o Dashboard (`/cafe`).
   - Crie uma **Nova Missão** (ex: "Fotos do Menu", 50 Créditos).
   - Logout.

2. **Login Prestador:**
   - Entre com credenciais de Provider.
   - Vá para Dashboard (`/provider`).
   - Em "Missões Abertas", clique em **Aceitar Missão**.
   - Vá para aba "Minhas Missões", clique em **Marcar Concluída**.
   - Logout.

3. **Aprovação (Cafeteria):**
   - Login como Admin de novo.
   - No Dashboard, veja a missão como DONE.
   - Clique em **Avaliar & Aprovar**.
   - Preencha nota (5), recomendação ("Ótimas fotos!") e marque "Permitir uso no portfólio".
   - Confirmar.
   - Logout.

4. **Carteira e Resgate (Prestador):**
   - Login como Provider.
   - Vá para aba "Carteira" (`/provider?tab=wallet` ou navbar/link).
   - Veja o saldo (50 Créditos).
   - Gere um Token de consumo (ex: 15 Créditos).
   - Você verá um QR Code e um link de teste simulado.
   - Copie/Abra o "Link direto".

5. **Confimar Resgate (Cafeteria):**
   - O link abrirá `/redeem/{token}`.
   - (Se não estiver logado como admin, faça login).
   - Veja os detalhes do token.
   - Clique em **CONFIRMAR CONSUMO**.
   - O saldo do prestador será debitado.

6. **Portfólio Público:**
   - Como Provider, vá para aba "Portfólio".
   - Clique em "Tornar Público" se necessário (embora na aprovação já tenhamos marcado).
   - Clique em "Ver meu perfil público".
   - Veja a página `/u/{provider_id}/portfolio`.

## Stack Tecnológica
- **Backend:** Python 3.12 (FastAPI), SQLAlchemy 2.0 (Sync), Pydantic v2
- **DB:** Postgres 15 (Docker)
- **Frontend:** Jinja2, HTMX, CSS (Vanilla Variables)
- **Auth:** Session Cookies (Signed)
- **Segurança:** Passlib (Bcrypt), ItsDangerous (Tokens)

## Notas de Implementação
- **Ledger:** Saldo calculado via soma de transações (EARN - SPEND).
- **Segurança:** Tokens de resgate armazenados apenas como hash SHA256. Expiração de 5 minutos.
- **Privacidade:** Opção de esconder nome da cafeteria no portfólio implementada.

---
*Criado por Antigravity Agent*
