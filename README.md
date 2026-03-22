# Coffee Co-lab ☕️

**Coffee Co-lab** é uma plataforma de "banco de escambo moderno" que conecta cafeterias artesanais a pessoas em busca de experiências reais para fortalecer seus portfólios (designers, fotógrafos, social media, devs).

A premissa é simples: em vez de dinheiro, a moeda de troca é a experiência e o produto.\n
- **A Cafeteria** recebe serviços digitais de alta qualidade (fotos do menu, artes para Instagram) pagando com o custo marginal do café e seu espaço.\n
- **O Talento Local (Prestador)** recebe uma oportunidade de trabalhar com clientes reais, ganha um case para o portfólio oficial, e ainda consome na cafeteria através de um sistema de "créditos" e "tokens".

---

## 🚀 Funcionalidades Principais

- **Cadastro de Usuários:** Perfis separados para `CAFE_ADMIN` (Cafeterias) e `PROVIDER` (Talentos Locais).
- **Onboarding & Verificação de Cafeterias:** As cafeterias informam seus sites e links de Instagram. O perfil passa por um status de "Em análise" até ser verificado, garantindo um ambiente seguro livre de impostores.
- **Mural de Missões:** As cafeterias publicam demandas reais com valores em Créditos. Os prestadores escolhem, executam e entregam os serviços.
- **Portfólio Público:** Todo prestador que conclui uma missão com sucesso ganha permissão para expor aquele trabalho no portfólio público na plataforma, anexado à marca da cafeteria real.
- **Sistema de Ledgers & Resgate (Redeem):** Cada crédito ganho pelo prestador fica salvo em uma "carteira". O prestador pode gerar um Token (QR Code) para descontar R$ 15, R$ 30, etc., direto no balcão da cafeteria.
- **Flash Messages e Segurança:** Fluxos robustos contra e-mails duplicados e proteção nas sessões dos usuários.

---

## 🛠 Tech Stack

A arquitetura foi projetada para ser leve, rápida e amigável:
- **Backend:** Python + FastAPI (Tipagem estática, performance e assincronismo).
- **Banco de Dados:** PostgreSQL (via Docker Compose) integrado via SQLAlchemy ORM.
- **Frontend / UI:** HTMX + Jinja2 Templates + Vanilla CSS (Aplicações "Single Page Application" sem escrever JavaScript pesado).
- **Migrations:** Alembic.
- **Deploy:** Docker.

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

2. **Dê permissão de execução ao script (Linux/Mac):**
   ```bash
   chmod +x run_local.sh
   ```

3. **Inicie o servidor localmente:**
   Pela primeira vez (ou sempre que quiser reinstalar as dependências e popular o banco de dados inicial), use a flag `--setup`:
   ```bash
   ./run_local.sh --setup
   ```
   *O script vai cuidar do Docker do Postgres, criar o `venv`, rodar o Alembic e alimentar o banco (Seed).*
   
   Para as vezes seguintes (onde o banco já está pronto), basta rodar sem a flag:
   ```bash
   ./run_local.sh
   ```

4. **Acesse a Plataforma:**
   Abra seu navegador em: **[http://localhost:8000](http://localhost:8000)**

---

## 🔑 Credenciais de Teste (Seed)

Após rodar o comando com `--setup`, um banco de dados modelo será populado. Você pode entrar usando a opção "Já tem uma conta? Entrar" na página inicial:

| Perfil | Email de Login | Senha |
|---|---|---|
| **Cafeteria (Admin Verificado)** | `admin@modocafe.local` | `Admin123!` |
| **Talento Local (Prestador)** | `provider@modocafe.local` | `Provider123!` |

*(Ou sinta-se à vontade para clicar em "Começar Agora" e testar todo o fluxo de cadastro real do zero!)*
