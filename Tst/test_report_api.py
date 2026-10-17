import pytest

import main
from Src.Models.response_format_enum import response_format_enum


@pytest.fixture
def client():
    return main.app.test_client()


@pytest.mark.parametrize("response_format", list(response_format_enum))
def test_report_api_returns_requested_format_for_entity(client, response_format):
    recipe = main.storage.data[main.storage_manager.recipe_key()][0]
    response = client.get(
        f"/api/report/format/{response_format.value}/recipe/{recipe.unique_code}"
    )

    assert response.status_code == 200
    assert "Борщ столичный" in response.get_data(as_text=True)
    if response_format in (response_format_enum.CSV, response_format_enum.MARKDOWN):
        assert response.headers["Content-Disposition"].startswith("attachment;")
    else:
        assert "Content-Disposition" not in response.headers


def test_report_api_default_uses_settings_factory_method(client, monkeypatch):
    recipe = main.storage.data[main.storage_manager.recipe_key()][0]
    monkeypatch.setattr(main.factory.settings, "response_format", response_format_enum.XML)

    response = client.get(f"/api/report/recipe/{recipe.unique_code}")

    assert response.status_code == 200
    assert response.mimetype == "application/xml"
    assert "<report>" in response.get_data(as_text=True)


@pytest.mark.parametrize(
    ("entity_type", "entity_collection"),
    [
        ("nomenclature", main.storage_manager.nomenclature_key()),
        ("range", main.storage_manager.range_key()),
    ],
)
def test_report_api_supports_nomenclature_and_unit_entities(
        client, entity_type, entity_collection):
    entity = main.storage.data[entity_collection][0]

    response = client.get(f"/api/report/format/TXT/{entity_type}/{entity.unique_code}")

    assert response.status_code == 200
    assert entity.name in response.get_data(as_text=True)


def test_report_api_rejects_unknown_format_and_entity(client):
    recipe = main.storage.data[main.storage_manager.recipe_key()][0]

    unknown_format = client.get(
        f"/api/report/format/PDF/recipe/{recipe.unique_code}")
    unknown_entity = client.get("/api/report/format/TXT/unknown/code")

    assert unknown_format.status_code == 400
    assert unknown_entity.status_code == 404
