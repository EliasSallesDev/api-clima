from datetime import datetime, timezone
from unicodedata import combining, normalize

import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(
    title="API de Clima e Cidades",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BRASIL_API_BASE_URL = "https://brasilapi.com.br/api"
APP_VERSION = "1.0.0"


class ExternalServiceError(Exception):
    def __init__(self, servico: str):
        self.servico = servico


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def error_response(status_code: int, codigo: str, mensagem: str, **extra):
    body = {
        "erro": True,
        "codigo": codigo,
        "mensagem": mensagem,
    }
    body.update(extra)
    return JSONResponse(status_code=status_code, content=body)


def normalize_text(value: str):
    text = normalize("NFKD", value.strip().lower())
    return "".join(char for char in text if not combining(char))


def fetch_json(url: str, servico: str):
    try:
        response = requests.get(url, timeout=10)
    except requests.RequestException as exc:
        raise ExternalServiceError(servico) from exc

    if response.status_code >= 500:
        raise ExternalServiceError(servico)

    if response.status_code == 404:
        return None

    try:
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as exc:
        raise ExternalServiceError(servico) from exc


@app.get("/api/v1/health")
def health():
    return {
        "status": "healthy",
        "versao": APP_VERSION,
        "timestamp": utc_now()
    }


@app.get("/api/v1/clima/{nome_cidade}")
def clima_por_cidade(nome_cidade: str):
    nome_informado = nome_cidade.strip()
    if len(nome_informado) < 2:
        return error_response(
            400,
            "NOME_INVALIDO",
            "O nome da cidade deve conter pelo menos 2 caracteres",
            nome_informado=nome_cidade,
        )

    try:
        cidades = fetch_json(
            f"{BRASIL_API_BASE_URL}/cptec/v1/cidade/{nome_informado}",
            "CPTEC",
        )
    except ExternalServiceError as exc:
        return error_response(
            503,
            "SERVICO_EXTERNO_INDISPONIVEL",
            "Nao foi possivel obter dados do servico externo. Tente novamente em alguns instantes",
            servico=exc.servico,
        )

    if not cidades:
        return error_response(
            404,
            "CIDADE_NAO_ENCONTRADA",
            "Nenhuma cidade encontrada com o nome informado",
            nome_informado=nome_cidade,
        )

    nome_normalizado = normalize_text(nome_informado)
    cidade = next(
        (item for item in cidades if normalize_text(item.get("nome", "")) == nome_normalizado),
        cidades[0],
    )

    try:
        previsao = fetch_json(
            f"{BRASIL_API_BASE_URL}/cptec/v1/clima/previsao/{cidade['id']}",
            "CPTEC",
        )
    except ExternalServiceError as exc:
        return error_response(
            503,
            "SERVICO_EXTERNO_INDISPONIVEL",
            "Nao foi possivel obter dados do servico externo. Tente novamente em alguns instantes",
            servico=exc.servico,
        )

    dias = (previsao or {}).get("clima") or []
    if not dias:
        return error_response(
            503,
            "SERVICO_EXTERNO_INDISPONIVEL",
            "Nao foi possivel obter dados do servico externo. Tente novamente em alguns instantes",
            servico="CPTEC",
        )

    clima_hoje = dias[0]
    return {
        "nome": cidade.get("nome"),
        "estado": cidade.get("estado"),
        "clima": {
            "temperatura_min": clima_hoje.get("min"),
            "temperatura_max": clima_hoje.get("max"),
            "condicao": clima_hoje.get("condicao_desc") or clima_hoje.get("condicao"),
            "unidades": {
                "temperatura": "C"
            }
        },
        "consultado_em": utc_now()
    }


@app.get("/api/v1/cidades/{sigla_uf}")
def cidades_por_estado(sigla_uf: str, limite: int = Query(default=10, ge=1, le=100)):
    sigla_informada = sigla_uf.strip()
    if len(sigla_informada) != 2 or not sigla_informada.isalpha():
        return error_response(
            400,
            "SIGLA_UF_INVALIDA",
            "A sigla do estado deve conter exatamente 2 letras",
            sigla_uf_informada=sigla_uf,
        )

    uf = sigla_informada.upper()
    try:
        cidades = fetch_json(
            f"{BRASIL_API_BASE_URL}/ibge/municipios/v1/{uf}",
            "Brasil API - IBGE",
        )
    except ExternalServiceError as exc:
        return error_response(
            503,
            "SERVICO_EXTERNO_INDISPONIVEL",
            "Nao foi possivel obter dados do servico externo. Tente novamente em alguns instantes",
            servico=exc.servico,
        )

    if cidades is None:
        return error_response(
            404,
            "UF_NAO_ENCONTRADA",
            "Estado com a sigla informada nao foi encontrado",
            sigla_uf_informada=sigla_uf,
        )

    cidades_limitadas = [{"nome": cidade.get("nome")} for cidade in cidades[:limite]]
    return {
        "uf": uf,
        "quantidade_retornada": len(cidades_limitadas),
        "cidades": cidades_limitadas,
        "consultado_em": utc_now()
    }
