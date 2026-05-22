from mini_search_engine.config import AppConfig
from mini_search_engine.web.app_factory import create_app


def test_search_api_response_shape(monkeypatch):
    monkeypatch.setenv("MSE_INPUT_DIR", "input_pages")
    monkeypatch.setenv("MSE_INDEX_PATH", "index_data/test-index.json")
    app = create_app(AppConfig())
    client = app.test_client()

    response = client.get("/api/v1/search?q=search")
    assert response.status_code == 200
    payload = response.get_json()
    assert "results" in payload
    assert "total" in payload
