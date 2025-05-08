# realmate-challenge

## Introdução

O objetivo deste desafio é avaliar os conhecimentos em **APIs** e **Webhooks**, além da capacidade de aprender rapidamente e implementar soluções eficientes, usando frameworks renomados como **Django** e **Django Rest Framework (DRF)**.

Deverá desenvolver uma web API que sincroniza eventos de um sistema de atendimentos no WhatsApp, processando webhooks e registrando as alterações no banco de dados.

## 🎯 O Desafio

Desenvolver uma web API utilizando **Django Rest Framework** para receber webhooks de um sistema de atendimento. Esses webhooks contêm eventos relacionados a conversas e mensagens, e devem ser registrados no banco de dados corretamente.

## 📌 Requisitos

1.	Criar dois modelos principais:
	- `Conversation`
	- `Message` (relacionado a uma `Conversation`)
2.	A API deve:
	- Receber eventos via POST no endpoint `localhost/webhook/`
	- Criar instâncias dos modelos correspondentes
3.	Criar um endpoint GET em `localhost/conversations/{id}` para expor a conversa, incluindo:
	- Seu estado (`OPEN` ou `CLOSED`)
	- Suas mensagens
4.	Lidar com erros de maneira graceful (evitar retornos de erro 500).
5.	Restrições:
	- Uma `Conversation` deve ter um estado. Os estados possíveis são: `OPEN` e `CLOSED`
	- Uma `CLOSED` `Conversation` não pode receber novas mensagens
	- Uma `Message` deve ter dois tipos: `SENT` e `RECEIVED`
6.	O banco de dados utilizado deve ser SQLite.

## 📦 Formato dos Webhooks

Os eventos virão no seguinte formato:

### Novo evento de conversa iniciada

```json
{
    "type": "NEW_CONVERSATION",
    "timestamp": "2025-02-21T10:20:41.349308",
    "data": {
        "id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
    }
}
```

### Novo evento de mensagem recebida

```json
{
    "type": "NEW_MESSAGE",
    "timestamp": "2025-02-21T10:20:42.349308",
    "data": {
        "id": "49108c71-4dca-4af3-9f32-61bc745926e2",
        "direction": "RECEIVED",
        "content": "Olá, tudo bem?",
        "conversation_id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
    }
}
```

### Novo evento de mensagem enviada

```json
{
    "type": "NEW_MESSAGE",
    "timestamp": "2025-02-21T10:20:44.349308",
    "data": {
        "id": "16b63b04-60de-4257-b1a1-20a5154abc6d",
        "direction": "SENT",
        "content": "Tudo ótimo e você?",
        "conversation_id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
    }
}
```

### Novo evento de conversa encerrada

```json
{
    "type": "CLOSE_CONVERSATION",
    "timestamp": "2025-02-21T10:20:45.349308",
    "data": {
        "id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
    }
}
```

## 📌 Regras de Negócio

- Toda conversa começa no estado “OPEN”
- Uma conversa no estado “CLOSED” não pode receber novas mensagens
- As mensagens devem estar associadas a uma conversa existente
- O ID da mensagem e o ID da conversa devem ser únicos
- O sistema deve lidar com erros sem retornar HTTP 500

## 🚀 Tecnologias e Ferramentas

- Django
- Django Rest Framework
- Poetry
- SQLite
- GitHub

## 💡 Como o Desafio Foi Resolvido

Para atender aos requisitos do desafio, a seguinte abordagem foi adotada:

1.  **Configuração Inicial do Projeto:**
    *   O projeto Django foi iniciado e configurado para utilizar o Django Rest Framework (DRF).
    *   As dependências foram gerenciadas com o Poetry, conforme especificado.

2.  **Criação dos Modelos:**
    *   Foram definidos dois modelos principais no `models.py` do app correspondente:
        *   `Conversation`: Com campos para `id` (UUID, único) e `state` (CharField com escolhas `OPEN` e `CLOSED`, default `OPEN`).
        *   `Message`: Com campos para `id` (UUID, único), `conversation` (ForeignKey para `Conversation`), `timestamp` (DateTimeField), `direction` (CharField com escolhas `SENT` e `RECEIVED`), e `content` (TextField).
    *   As migrações foram criadas e aplicadas para refletir esses modelos no banco de dados SQLite.

3.  **Desenvolvimento da API de Webhook (`/webhook/`):**
    *   Foi criada uma `APIView` no DRF para o endpoint `POST /webhook/`.
    *   A view é responsável por:
        *   Receber o payload JSON do webhook.
        *   Identificar o `type` do evento (`NEW_CONVERSATION`, `NEW_MESSAGE`, `CLOSE_CONVERSATION`).
        *   Para `NEW_CONVERSATION`: Criar uma nova instância de `Conversation` com o `id` fornecido e estado `OPEN`.
        *   Para `NEW_MESSAGE`:
            *   Verificar se a `conversation_id` existe e se a conversa está `OPEN`.
            *   Criar uma nova instância de `Message` associada à conversa, com os dados fornecidos (`id`, `timestamp`, `direction`, `content`).
        *   Para `CLOSE_CONVERSATION`: Encontrar a conversa pelo `id` e atualizar seu estado para `CLOSED`.
    *   Validadores e serializers do DRF foram utilizados para garantir a integridade dos dados recebidos e para criar/atualizar os modelos.
    *   A regra de negócio que impede novas mensagens em conversas `CLOSED` foi implementada na lógica de criação de mensagens.
    *   A unicidade dos IDs de `Conversation` e `Message` é garantida pela definição dos campos `id` como `primary_key=True` ou `unique=True` nos modelos, e tratada adequadamente para evitar erros 500 (ex: retornando um erro 409 Conflict se tentar criar uma conversa/mensagem com ID já existente).

4.  **Desenvolvimento do Endpoint de Consulta (`/conversations/{id}`):**
    *   Foi criada uma `RetrieveAPIView` no DRF para o endpoint `GET /conversations/{id}`.
    *   Serializers aninhados foram utilizados para incluir o estado da conversa e a lista de suas mensagens na resposta. O serializer de `Conversation` incluiu um serializer de `Message` com `many=True`.

5.  **Tratamento de Erros:**
    *   Foram implementados manipuladores de exceção customizados no DRF ou try-except blocks nas views para capturar exceções específicas (ex: `ObjectDoesNotExist`, `ValidationError`) e retornar respostas de erro apropriadas (ex: 400, 404, 409) em vez de erros 500.

## 📌 Instruções de Instalação

### Pré-requisitos

- Instalar o Poetry para gerenciamento de dependências:

```bash
pip install poetry
```

### Instalação do Projeto

> Opcionalmente, crie um ambiente virtual python.

1.	Instale as dependências do projeto utilizando o Poetry:

```bash
cd realmate-challenge-felipe
poetry install
```

2.	Aplique as migrações no banco de dados SQLite:

```bash
python manage.py makemigrations
python manage.py migrate
```

3.	Execute o servidor de desenvolvimento:

```bash
python manage.py runserver
```

## 📚 Referências

- [Django Rest Framework](https://www.django-rest-framework.org/)
- [Django](https://www.djangoproject.com/)
- [Poetry](https://python-poetry.org/)
