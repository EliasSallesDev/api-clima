# API de Agregacao de Dados Climaticos e Geograficos

Este projeto foi desenvolvido para a disciplina **Tecnicas de Integracao de Sistemas**.

A ideia da API e facilitar a consulta de informacoes sobre cidades brasileiras em um unico lugar. A partir do nome de uma cidade ou da sigla de um estado, a aplicacao consulta servicos publicos externos, organiza os dados recebidos e devolve uma resposta em JSON de forma simples e padronizada.

## O que a API faz

- Verifica se o servico esta funcionando pelo endpoint de health check.
- Busca dados climaticos de uma cidade informada pelo usuario.
- Lista cidades de um estado brasileiro a partir da sigla da UF.
- Trata entradas invalidas e casos em que cidade ou estado nao sao encontrados.
- Consome APIs publicas externas para montar as respostas.

## Tecnologias utilizadas

- Python
- FastAPI
- Uvicorn
- Requests
- Pytest

## APIs externas

O projeto utiliza endpoints publicos da Brasil API:

- **CPTEC**: usado para buscar cidades e previsao do tempo.
- **IBGE**: usado para listar municipios de uma UF.

Como a aplicacao depende desses servicos externos, pode haver erro temporario caso alguma API publica esteja indisponivel no momento da consulta.

## Como executar o projeto

Antes de iniciar, tenha o Python instalado na maquina.

1. Instale as dependencias:

```bash
pip install -r requirements.txt
```

2. Inicie a API na porta 3000:

```bash
uvicorn src.main:app --reload --port 3000
```

3. Acesse a documentacao interativa no navegador:

```text
http://localhost:3000/docs
```

## Endpoints disponiveis

### Health check

Verifica se a API esta ativa.

```http
GET /api/v1/health
```

Exemplo de resposta:

```json
{
  "status": "healthy",
  "versao": "1.0.0",
  "timestamp": "2026-06-04T06:16:19Z"
}
```

### Clima por cidade

Retorna dados climaticos a partir do nome da cidade.

```http
GET /api/v1/clima/Fortaleza
```

Exemplo de resposta:

```json
{
  "nome": "Fortaleza",
  "estado": "CE",
  "clima": {
    "temperatura_min": 24,
    "temperatura_max": 32,
    "condicao": "Parcialmente Nublado",
    "unidades": {
      "temperatura": "C"
    }
  },
  "consultado_em": "2026-06-04T06:16:19Z"
}
```

### Cidades por estado

Lista cidades de uma UF. O parametro `limite` define a quantidade maxima de cidades retornadas.

```http
GET /api/v1/cidades/CE?limite=5
```

Exemplo de resposta:

```json
{
  "uf": "CE",
  "quantidade_retornada": 5,
  "cidades": [
    { "nome": "Abaiara" },
    { "nome": "Acarape" },
    { "nome": "Acarau" }
  ],
  "consultado_em": "2026-06-04T06:16:19Z"
}
```

## Tratamento de erros

A API retorna respostas padronizadas para os principais cenarios de erro:

- `400`: nome da cidade ou sigla da UF em formato invalido.
- `404`: cidade ou UF nao encontrada.
- `503`: falha ou indisponibilidade de algum servico externo.

## Testes automatizados

Para executar os testes:

```bash
pytest
```

Os testes simulam as respostas das APIs externas. Isso ajuda a validar o comportamento da aplicacao sem depender da internet ou da disponibilidade dos servicos publicos no momento da execucao.

## Colecao Postman

A colecao para testes manuais esta disponivel em:

```text
docs/postman_collection.json
```
