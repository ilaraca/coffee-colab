# Guia de Testes Funcionais - Coffee Co-lab MVP 🧪

Este documento descreve os passos para validar as principais funcionalidades da aplicação.

## 📋 Pré-requisitos
- Aplicação rodando (`uvicorn app.main:app --reload`)
- Banco de dados migrado e populado (`seed.py` executado)
- Navegador acessando [http://localhost:8000](http://localhost:8000)

---

## 🛑 Cenário 1: Autenticação
**Objetivo:** Verificar se os diferentes perfis (Cafe e Provider) conseguem logar e são redirecionados corretamente.

1. **Acessar Home:**
   - Vá para `http://localhost:8000/`.
   - Deve redirecionar para `/login`.

2. **Login Cafeteria (Admin):**
   - Email: `admin@modocafe.local`
   - Senha: `Admin123!`
   - **Resultado:** Redirecionamento para `/cafe` (Painel da Cafeteria).
   - Clique em "Sair" (Logout).

3. **Login Prestador (Provider):**
   - Email: `provider@modocafe.local`
   - Senha: `Provider123!`
   - **Resultado:** Redirecionamento para `/provider` (Painel do Prestador).
   - Clique em "Sair" (Logout).

---

## ☕ Cenário 2: Ciclo de Vida da Missão (Core Loop)
**Objetivo:** Criar, aceitar, finalizar e aprovar uma missão, verificando a troca de créditos.

### Parte A: Criação (Admin)
1. Logue com **Admin**.
2. No Dashboard `/cafe`, clique em "Nova Missão" (se o formulário estiver oculto, procure o botão ou verifique se já está visível).
3. Preencha:
   - Título: "Fotos para Instagram"
   - Descrição: "5 fotos editadas do novo Latte."
   - Valor: 50 Créditos
4. Clique em "Criar Missão".
5. **Verificação:** A missão deve aparecer na lista com status **OPEN**.
6. Faça Logout.

### Parte B: Execução (Provider)
1. Logue com **Provider**.
2. No Dashboard `/provider`, vá para a aba **"Missões Abertas"**.
3. Encontre "Fotos para Instagram" e clique em **"Aceitar Missão"**.
4. Vá para a aba **"Minhas Missões"**.
5. Verifique se o status é **ACCEPTED**.
6. Clique em **"Marcar Concluída"**.
7. O status deve mudar para **DONE** e aparecer a mensagem "Aguardando aprovação".
8. Faça Logout.

### Parte C: Aprovação e Pagamento (Admin)
1. Logue com **Admin**.
2. No Dashboard `/cafe`, encontre a missão (agora com status **DONE**).
3. Clique no botão **"Avaliar & Aprovar"**.
4. No modal/form que abrir:
   - Nota: 5 Estrelas
   - Recomendação: "Trabalho excelente!"
   - Checkbox "Permitir uso no portfólio": **MARCADO**.
5. Confirme.
6. **Verificação:** A missão deve aparecer como **APPROVED** (ou "Finalizada e paga").

---

## 💰 Cenário 3: Carteira e Resgate (Redeem)
**Objetivo:** Verificar se o prestador recebeu os créditos e consegue gastá-los.

1. Logue com **Provider**.
2. Vá para a aba **"Carteira"** (Wallet).
3. **Verificação de Saldo:** O saldo deve ser **50 Créditos** (ou mais, se já tiver saldo anterior).
4. No formulário "Gerar Token":
   - Valor: 15 Créditos.
   - Clique em "Gerar QR Code".
5. **Resultado:**
   - Um QR Code é exibido.
   - O saldo visual pode não atualizar imediatamente até recarregar, mas o token foi criado.
6. **Simulação de Uso:**
   - Clique no link "Link direto (Simulação)" que aparece abaixo do QR Code.
   - Isso abrirá uma nova aba em `/redeem/{token_hash}`.

---

## 📱 Cenário 4: Validação do Consumo (Caixa da Cafeteria)
**Objetivo:** O caixa (Admin) valida o token e desconta o saldo.

1. Na aba aberta do **Link direto** (`/redeem/...`):
   - Se não estiver logado como Admin nesta aba, faça o login.
2. Você verá os detalhes do Token:
   - Prestador: John Provider
   - Valor: 15 Créditos
   - Status: ISSUED
3. Clique em **"CONFIRMAR CONSUMO"**.
4. **Resultado:** Mensagem de sucesso "Consumo Confirmado!".

*Volta para o Provider (Opcional):*
- Volte para a aba do Provider e atualize a página da Carteira.
- O saldo deve ter reduzido (50 - 15 = 35).
- No Extrato, deve aparecer uma transação de **SPEND (-15)**.

---

## 🎨 Cenário 5: Portfólio Público
**Objetivo:** Verificar se a missão aprovada gerou um item de portfólio visível.

1. Logue com **Provider**.
2. Vá para a aba **"Portfólio"**.
3. Você deve ver o card "Fotos para Instagram" (gerado da missão).
4. **Teste de Privacidade:**
   - O status deve estar "Privado" (ou Público se a lógica setou default).
   - Clique em "Tornar Público".
   - O status muda para "Publicado".
5. Clique no botão **"Ver meu perfil público"**.
6. Uma nova aba abrirá em `/u/{id_do_provider}/portfolio`.
7. **Verificação:** A página deve ser pública (acessível sem login, se testar em janela anônima) e mostrar o card do projeto com a avaliação.

---

## 🐛 Bônus: Teste de Erro (Saldo Insuficiente)
1. Tente gerar um token com valor **1000** na Carteira do Provider.
2. **Resultado Esperado:** O sistema deve impedir (mensagem de erro ou validação HTML `max`).

---
*Fim dos Testes.*
