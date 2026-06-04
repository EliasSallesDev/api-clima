from fastapi.testclient import TestClient

from src import main
from src.main import app


client = TestClient(app)


def test_clima_por_cidade_valida(monkeypatch):
    def fake_fetch_json(url, servico):
        if "/cptec/v1/cidade/" in url:
            return [{"id": 123, "nome": "Fortaleza", "estado": "CE"}]
        return {
            "clima": [
                {
                    "min": 24,
                    "max": 32,
                    "condicao_desc": "Parcialmente Nublado",
                }
            ]
        }

    monkeypatch.setattr(main, "fetch_json", fake_fetch_json)

    response = client.get("/api/v1/clima/Fortaleza")

    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Fortaleza"
    assert data["estado"] == "CE"
    assert data["clima"]["temperatura_min"] == 24
    assert data["clima"]["temperatura_max"] == 32
    assert data["clima"]["condicao"] == "Parcialmente Nublado"


def test_clima_cidade_nao_encontrada(monkeypatch):
    monkeypatch.setattr(main, "fetch_json", lambda url, servico: [])

    response = client.get("/api/v1/clima/CidadeInexistente")

    assert response.status_code == 404
    data = response.json()
    assert data["erro"] is True
    assert data["codigo"] == "CIDADE_NAO_ENCONTRADA"
    assert data["nome_informado"] == "CidadeInexistente"


def test_clima_nome_invalido():
    response = client.get("/api/v1/clima/X")

    assert response.status_code == 400
    assert response.json()["codigo"] == "NOME_INVALIDO"
