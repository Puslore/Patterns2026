import pytest
import main
from Src.Models.settings_model import settings_model


@pytest.fixture
def client():
    """Фикстура для создания тестового HTTP-клиента приложения."""
    main.app_settings_manager.settings.first_start = True
    main.app_storage_manager.build()
    return main.api.test_client()


"""
Проверить успешную фильтрацию номенклатуры по полному совпадению (EQUALS)
"""
def test_api_filter_nomenclature_equals(client):
    payload = {"name": "Свёкла", "filter_type": "EQUALS"}
    response = client.post("/api/nomenclature_model/filter", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Свёкла"


"""
Проверить фильтрацию номенклатуры по подстроке (LIKE)
"""
def test_api_filter_nomenclature_like(client):
    payload = {"name": "мука", "filter_type": "LIKE"}
    response = client.post("/api/nomenclature_model/filter", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Пшеничная мука"


"""
Проверить фильтрацию группы по уникальному коду через маршрут /api/group_model/filter
"""
def test_api_filter_group_by_code(client):
    groups = client.get("/api/entity/group_model").json()
    assert len(groups) > 0
    target_code = groups[0]["unique_code"]
    target_name = groups[0]["name"]

    payload = {"unique_code": target_code}
    response = client.post("/api/group_model/filter", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["unique_code"] == target_code
    assert data[0]["name"] == target_name


"""
Проверить фильтрацию единицы измерения по вложенной структуре через API
"""
def test_api_filter_range_nested(client):
    payload = {
        "filters": [
            {
                "field_name": "base.name",
                "filter_type": "EQUALS",
                "value": "Грамм"
            }
        ]
    }
    response = client.post("/api/range_model/filter", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(r["name"] == "Киллограм" for r in data)


"""
Проверить фильтрацию рецепта по вложенному ингредиенту
"""
def test_api_filter_receipt_by_nested_ingredient(client):
    payload = {"name": "Говядина", "filter_type": "LIKE"}
    response = client.post("/api/receipt_model/filter", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Борщ столичный"


"""
Проверить возврат 404 для неподдерживаемого типа сущности при фильтрации
"""
def test_api_filter_unknown_entity_404(client):
    payload = {"name": "Тест"}
    response = client.post("/api/unknown_entity/filter", json=payload)

    assert response.status_code == 404


"""
Проверить возврат 400 при передаче некорректного тела JSON в фильтрацию
"""
def test_api_filter_invalid_body_400(client):
    response = client.post(
        "/api/nomenclature_model/filter",
        data="not a json",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400


"""
Проверить формирование полной оборотно-сальдовой ведомости (ОСВ) через API
"""
def test_api_osv_full(client):
    response = client.post("/api/report/osv", json={})

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Проверка обязательных полей строки ОСВ
    first = data[0]
    assert "storage_name" in first
    assert "nomenclature_name" in first
    assert "turnover_in" in first
    assert "turnover_out" in first
    assert "final_balance" in first


"""
Проверить формирование ОСВ с фильтром по номенклатуре через API
"""
def test_api_osv_filtered(client):
    payload = {"name": "Свёкла", "filter_type": "EQUALS"}
    response = client.post("/api/report/osv", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["nomenclature_name"] == "Свёкла"
    assert data[0]["turnover_in"] == 50.0
    assert data[0]["turnover_out"] == 8.0
    assert data[0]["final_balance"] == 42.0


"""
Проверить фильтрацию сущности через альтернативный маршрут /api/filter/<entity>
"""
def test_api_filter_by_alias_route(client):
    payload = {"name": "Свёкла", "filter_type": "EQUALS"}
    response = client.post("/api/filter/nomenclature_model", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Свёкла"


"""
Проверить формирование ОСВ через алиас маршрута /api/osv
"""
def test_api_osv_alias(client):
    payload = {"name": "Картофель", "filter_type": "EQUALS"}
    response = client.post("/api/osv", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["nomenclature_name"] == "Картофель"
    assert data[0]["final_balance"] == 94.0
