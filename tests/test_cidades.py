from fastapi.testclient import TestClient

from src import main
from src.main import app


client = TestClient(app)


def test_cidades_por_estado_valido(monkeypatch):
    cidades = [
        {"nome": "Abaiara"},
        {"nome": "Acarape"},
        {"nome": "Acarau"},
    ]
    monkeypatch.setattr(main, "fetch_json", lambda url, servico: cidades)

    response = client.get("/api/v1/cidades/CE?limite=2")

    assert response.status_code == 200
    data = response.json()
    assert data["uf"] == "CE"
    assert data["quantidade_retornada"] == 2
    assert data["cidades"] == [{"nome": "Abaiara"}, {"nome": "Acarape"}]


def test_cidades_uf_nao_encontrada(monkeypatch):
    monkeypatch.setattr(main, "fetch_json", lambda url, servico: None)

    response = client.get("/api/v1/cidades/XX")

    assert response.status_code == 404
    assert response.json()["codigo"] == "UF_NAO_ENCONTRADA"


def test_cidades_uf_invalida():
    response = client.get("/api/v1/cidades/ceara")

    assert response.status_code == 400
    assert response.json()["codigo"] == "SIGLA_UF_INVALIDA"
