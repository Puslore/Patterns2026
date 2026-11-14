import pytest
import main
from Src.Dtos.report_type_enum import report_type_enum
from Src.Models.settings_model import settings_model


@pytest.fixture
def client():
    """Фикстура для создания тестового HTTP-клиента приложения."""
    # Гарантируем инициализацию настроек и хранилища
    main.app_settings_manager.settings.first_start = True
    main.app_storage_manager.build()
    return main.api.test_client()


def test_success_get_report_formats(client):
    """
    Успешное получение списка всех форматов отчетов через API.
    Проверяется код ответа 200, формат JSON и наличие основных форматов.
    """
    # Действие
    response = client.get("/api/reports/formats")

    # Проверки
    assert response.status_code == 200
    formats = response.json()
    assert isinstance(formats, list)
    assert len(formats) >= 3
    names = [item["name"] for item in formats]
    assert "TXT" in names
    assert "CSV" in names
    assert "MARKDOWN" in names


def test_success_get_entities_list(client):
    """
    Успешное получение списка доступных доменных сущностей системы.
    Проверяется код ответа 200 и присутствие ключевых доменных моделей.
    """
    # Действие
    response = client.get("/api/get_entities")

    # Проверки
    assert response.status_code == 200
    entities = response.json()
    assert isinstance(entities, dict)
    assert "group_model" in entities
    assert "range_model" in entities
    assert "nomenclature_model" in entities
    assert "storage_model" in entities
    assert "receipt_model" in entities


def test_success_crud_group_model_full_lifecycle(client):
    """
    Полный жизненный цикл CRUD-операций для сущности group_model.
    Проверяются операции создания, чтения списка, чтения по ID, обновления и удаления.
    """
    # 1. CREATE
    create_payload = {"name": "Кондитерские изделия"}
    create_res = client.post("/api/entity/group_model", json=create_payload)
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["name"] == "Кондитерские изделия"
    unique_code = created_data["unique_code"]
    assert unique_code != ""

    # 2. READ ALL
    list_res = client.get("/api/entity/group_model")
    assert list_res.status_code == 200
    all_codes = [g["unique_code"] for g in list_res.json()]
    assert unique_code in all_codes

    # 3. READ BY ID
    get_res = client.get(f"/api/entity/group_model/{unique_code}")
    assert get_res.status_code == 200
    assert get_res.json()["unique_code"] == unique_code
    assert get_res.json()["name"] == "Кондитерские изделия"

    # 4. UPDATE
    update_payload = {"name": "Выпечка и сладости"}
    update_res = client.put(f"/api/entity/group_model/{unique_code}", json=update_payload)
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Выпечка и сладости"
    assert update_res.json()["unique_code"] == unique_code

    # 5. DELETE
    delete_res = client.delete(f"/api/entity/group_model/{unique_code}")
    assert delete_res.status_code == 200
    assert delete_res.json() == {"result": True}

    # 6. READ AFTER DELETE (должен вернуть 404)
    after_delete_res = client.get(f"/api/entity/group_model/{unique_code}")
    assert after_delete_res.status_code == 404


def test_success_crud_range_model_full_lifecycle(client):
    """
    Полный жизненный цикл CRUD-операций для сущности range_model (единица измерения).
    Проверяется создание независимой единицы измерения, ее модификация и удаление.
    """
    # 1. CREATE
    create_payload = {"name": "Коробка", "value": 1, "base_code": ""}
    create_res = client.post("/api/entity/range_model", json=create_payload)
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["name"] == "Коробка"
    unique_code = created_data["unique_code"]

    # 2. UPDATE
    update_payload = {"name": "Большая коробка", "value": 5, "base_code": ""}
    update_res = client.put(f"/api/entity/range_model/{unique_code}", json=update_payload)
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Большая коробка"
    assert update_res.json()["value"] == 5

    # 3. DELETE
    delete_res = client.delete(f"/api/entity/range_model/{unique_code}")
    assert delete_res.status_code == 200
    assert delete_res.json() == {"result": True}


def test_fail_delete_linked_range_model_dependency_rejected(client):
    """
    Запрет удаления единицы измерения, на которую ссылаются другие объекты (базовая единица 'Грамм').
    Ожидается код ответа 400 с пояснением причины блокировки.
    """
    # Ищем базовую единицу измерения 'Грамм'
    ranges_res = client.get("/api/entity/range_model")
    assert ranges_res.status_code == 200
    gram = next(r for r in ranges_res.json() if r["name"] == "Грамм")
    gram_code = gram["unique_code"]

    # Попытка удалить базовую единицу
    del_res = client.delete(f"/api/entity/range_model/{gram_code}")
    assert del_res.status_code == 400
    detail = del_res.json().get("detail", "")
    assert "Запрещено удалять сущность" in detail


def test_fail_delete_linked_group_model_dependency_rejected(client):
    """
    Запрет удаления группы номенклатуры, содержащей связанные товарные позиции.
    Ожидается код ответа 400 с описанием связанной номенклатуры.
    """
    # Ищем группу 'Овощи', к которой привязаны ингредиенты борща
    groups_res = client.get("/api/entity/group_model")
    assert groups_res.status_code == 200
    veg_group = next(g for g in groups_res.json() if g["name"] == "Овощи")
    veg_code = veg_group["unique_code"]

    # Попытка удалить связанную группу
    del_res = client.delete(f"/api/entity/group_model/{veg_code}")
    assert del_res.status_code == 400
    detail = del_res.json().get("detail", "")
    assert "Запрещено удалять сущность" in detail


def test_fail_change_code_linked_group_model_dependency_rejected(client):
    """
    Запрет изменения уникального кода связанной группы номенклатуры.
    Ожидается код ответа 400 с запретом на изменение идентификатора.
    """
    groups_res = client.get("/api/entity/group_model")
    assert groups_res.status_code == 200
    veg_group = next(g for g in groups_res.json() if g["name"] == "Овощи")
    veg_code = veg_group["unique_code"]

    # Попытка передать новый уникальный код в теле запроса PUT
    update_payload = {"name": "Овощи", "unique_code": "new_arbitrary_code_12345"}
    put_res = client.put(f"/api/entity/group_model/{veg_code}", json=update_payload)
    assert put_res.status_code == 400
    detail = put_res.json().get("detail", "")
    assert "Запрещено изменять код сущности" in detail


def test_fail_get_nonexistent_entity_returns_404(client):
    """
    Обращение к несуществующему объекту возвращает HTTP статус 404.
    """
    response = client.get("/api/entity/group_model/non_existent_code_999999")
    assert response.status_code == 404


def test_fail_create_entity_missing_body_returns_400(client):
    """
    Создание сущности без передаваемых данных возвращает HTTP статус 400.
    """
    response = client.post("/api/entity/group_model", data="")
    assert response.status_code == 400


def test_success_get_default_report_endpoint(client):
    """
    Генерация отчета по умолчанию для существующей сущности через API.
    Проверяется код ответа 200 и непустое текстовое содержимое.
    """
    ranges_res = client.get("/api/entity/range_model")
    assert ranges_res.status_code == 200
    item = ranges_res.json()[0]

    report_res = client.get(f"/api/get_default_report?entity=range_model&unique_code={item['unique_code']}")
    assert report_res.status_code == 200
    assert report_res.text != ""
