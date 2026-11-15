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
    Ожидается код ответа 409 с пояснением причины блокировки.
    """
    # Ищем базовую единицу измерения 'Грамм'
    ranges_res = client.get("/api/entity/range_model")
    assert ranges_res.status_code == 200
    gram = next(r for r in ranges_res.json() if r["name"] == "Грамм")
    gram_code = gram["unique_code"]

    # Попытка удалить базовую единицу
    del_res = client.delete(f"/api/entity/range_model/{gram_code}")
    assert del_res.status_code == 409
    detail = del_res.json().get("detail", "")
    assert "Запрещено удалять сущность" in detail


def test_fail_delete_linked_group_model_dependency_rejected(client):
    """
    Запрет удаления группы номенклатуры, содержащей связанные товарные позиции.
    Ожидается код ответа 409 с описанием связанной номенклатуры.
    """
    # Ищем группу 'Овощи', к которой привязаны ингредиенты борща
    groups_res = client.get("/api/entity/group_model")
    assert groups_res.status_code == 200
    veg_group = next(g for g in groups_res.json() if g["name"] == "Овощи")
    veg_code = veg_group["unique_code"]

    # Попытка удалить связанную группу
    del_res = client.delete(f"/api/entity/group_model/{veg_code}")
    assert del_res.status_code == 409
    detail = del_res.json().get("detail", "")
    assert "Запрещено удалять сущность" in detail


def test_fail_change_code_linked_group_model_dependency_rejected(client):
    """
    Запрет изменения уникального кода связанной группы номенклатуры.
    Ожидается код ответа 409 с запретом на изменение идентификатора.
    """
    groups_res = client.get("/api/entity/group_model")
    assert groups_res.status_code == 200
    veg_group = next(g for g in groups_res.json() if g["name"] == "Овощи")
    veg_code = veg_group["unique_code"]

    # Попытка передать новый уникальный код в теле запроса PUT
    update_payload = {"name": "Овощи", "unique_code": "new_arbitrary_code_12345"}
    put_res = client.put(f"/api/entity/group_model/{veg_code}", json=update_payload)
    assert put_res.status_code == 409
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


def test_success_crud_nomenclature_model_full_lifecycle(client):
    """
    Полный жизненный цикл CRUD-операций для сущности nomenclature_model.
    Проверяются создание с разрешением связей, чтение, обновление и удаление.
    """
    groups_res = client.get("/api/entity/group_model")
    ranges_res = client.get("/api/entity/range_model")
    group_code = groups_res.json()[0]["unique_code"]
    range_code = ranges_res.json()[0]["unique_code"]

    # 1. CREATE
    create_payload = {"name": "Клубника свежая", "group_code": group_code, "range_code": range_code}
    create_res = client.post("/api/entity/nomenclature_model", json=create_payload)
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["name"] == "Клубника свежая"
    nom_code = created["unique_code"]

    # 2. READ ALL
    all_res = client.get("/api/entity/nomenclature_model")
    assert all_res.status_code == 200
    assert any(item["unique_code"] == nom_code for item in all_res.json())

    # 3. READ BY ID
    get_res = client.get(f"/api/entity/nomenclature_model/{nom_code}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Клубника свежая"

    # 4. UPDATE
    upd_res = client.put(
        f"/api/entity/nomenclature_model/{nom_code}",
        json={"name": "Клубника замороженная", "group_code": group_code, "range_code": range_code},
    )
    assert upd_res.status_code == 200
    assert upd_res.json()["name"] == "Клубника замороженная"

    # 5. DELETE
    del_res = client.delete(f"/api/entity/nomenclature_model/{nom_code}")
    assert del_res.status_code == 200

    # 6. READ AFTER DELETE (404)
    assert client.get(f"/api/entity/nomenclature_model/{nom_code}").status_code == 404


def test_success_crud_storage_model_full_lifecycle(client):
    """
    Полный жизненный цикл CRUD-операций для сущности storage_model (склад).
    """
    # 1. CREATE
    create_payload = {"name": "Холодильный цех", "address": "г. Иркутск, ул. Северная, д. 5"}
    create_res = client.post("/api/entity/storage_model", json=create_payload)
    assert create_res.status_code == 201
    storage_code = create_res.json()["unique_code"]

    # 2. READ ALL
    all_res = client.get("/api/entity/storage_model")
    assert all_res.status_code == 200
    assert any(s["unique_code"] == storage_code for s in all_res.json())

    # 3. READ BY ID
    get_res = client.get(f"/api/entity/storage_model/{storage_code}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Холодильный цех"

    # 4. UPDATE
    upd_res = client.put(
        f"/api/entity/storage_model/{storage_code}",
        json={"name": "Холодильный цех №2", "address": "г. Иркутск, ул. Северная, д. 7"},
    )
    assert upd_res.status_code == 200
    assert upd_res.json()["name"] == "Холодильный цех №2"

    # 5. DELETE
    del_res = client.delete(f"/api/entity/storage_model/{storage_code}")
    assert del_res.status_code == 200

    # 6. READ AFTER DELETE
    assert client.get(f"/api/entity/storage_model/{storage_code}").status_code == 404


def test_success_crud_receipt_model_full_lifecycle(client):
    """
    Полный жизненный цикл CRUD-операций для сущности receipt_model (технологическая карта/рецепт).
    """
    # 1. CREATE
    create_payload = {"name": "Морс брусничный", "comments": "Освежающий напиток", "items": []}
    create_res = client.post("/api/entity/receipt_model", json=create_payload)
    assert create_res.status_code == 201
    rec_code = create_res.json()["unique_code"]

    # 2. READ ALL
    all_res = client.get("/api/entity/receipt_model")
    assert all_res.status_code == 200
    assert any(r["unique_code"] == rec_code for r in all_res.json())

    # 3. READ BY ID
    get_res = client.get(f"/api/entity/receipt_model/{rec_code}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Морс брусничный"

    # 4. UPDATE
    upd_res = client.put(
        f"/api/entity/receipt_model/{rec_code}",
        json={"name": "Морс клюквенный", "comments": "Кислый напиток", "items": []},
    )
    assert upd_res.status_code == 200
    assert upd_res.json()["name"] == "Морс клюквенный"

    # 5. DELETE
    del_res = client.delete(f"/api/entity/receipt_model/{rec_code}")
    assert del_res.status_code == 200

    # 6. READ AFTER DELETE
    assert client.get(f"/api/entity/receipt_model/{rec_code}").status_code == 404


def test_fail_delete_nomenclature_used_in_receipt(client):
    """
    Запрет удаления номенклатуры, используемой в рецепте.
    Ожидается код 409 Conflict.
    """
    groups_res = client.get("/api/entity/group_model")
    ranges_res = client.get("/api/entity/range_model")
    group_code = groups_res.json()[0]["unique_code"]
    range_code = ranges_res.json()[0]["unique_code"]

    # Создаем номенклатуру
    nom_res = client.post(
        "/api/entity/nomenclature_model",
        json={"name": "Номенклатура для супа", "group_code": group_code, "range_code": range_code},
    )
    nom_code = nom_res.json()["unique_code"]

    # Создаем рецепт, использующий номенклатуру
    rec_res = client.post(
        "/api/entity/receipt_model",
        json={"name": "Суп фирменный", "comments": "Вкусный", "items": [nom_code]},
    )
    assert rec_res.status_code == 201
    rec_code = rec_res.json()["unique_code"]

    # Попытка удалить используемую номенклатуру должна быть отклонена
    del_nom_res = client.delete(f"/api/entity/nomenclature_model/{nom_code}")
    assert del_nom_res.status_code == 409
    assert "Запрещено удалять сущность" in del_nom_res.json().get("detail", "")

    # После удаления рецепта номенклатуру можно удалить
    del_rec_res = client.delete(f"/api/entity/receipt_model/{rec_code}")
    assert del_rec_res.status_code == 200

    del_nom_after = client.delete(f"/api/entity/nomenclature_model/{nom_code}")
    assert del_nom_after.status_code == 200


def test_recipe_and_ingredient_dependencies_locked(client):
    """
    Проверка блокировки удаления базового ингредиента (полуфабриката), на который ссылается составной ингредиент.
    """
    # Получаем рецепт "Борщ столичный"
    receipts_res = client.get("/api/entity/receipt_model")
    assert receipts_res.status_code == 200
    borsch = receipts_res.json()[0]

    # Находим свёклу для пассеровки (базовый ингредиент)
    borsch_domain = main.app_storage_manager.get_item("receipt_model", borsch["unique_code"])
    passerovka = next(i for i in borsch_domain.items if i.name == "Пассеровка свекольная")
    beet_base = passerovka.base
    assert beet_base is not None

    # Попытка удалить базовый ингредиент заблокирована обратным индексом связей
    is_linked, reason = main.app_storage_service.is_linked(beet_base.unique_code)
    assert is_linked == True
    assert "Пассеровка свекольная" in reason or "Борщ столичный" in reason


def test_rename_used_group_preserves_object_references_in_memory(client):
    """
    Переименование используемой группы номенклатуры сохраняет существующие ссылки в памяти.
    Связанные объекты номенклатуры видят актуальное наименование группы.
    """
    groups_res = client.get("/api/entity/group_model")
    meat_group = next(g for g in groups_res.json() if g["name"] == "Мясные продукты")
    meat_code = meat_group["unique_code"]

    # Переименовываем группу
    upd_res = client.put(f"/api/entity/group_model/{meat_code}", json={"name": "Мясные деликатесы"})
    assert upd_res.status_code == 200
    assert upd_res.json()["name"] == "Мясные деликатесы"

    # Проверяем объект номенклатуры "Говядина" прямо в памяти хранилища
    beef_obj = next(
        item for item in main.app_storage_manager.data["nomenclature_model"] if item.name == "Говядина"
    )
    assert beef_obj.group.name == "Мясные деликатесы"

    # Возвращаем исходное имя
    client.put(f"/api/entity/group_model/{meat_code}", json={"name": "Мясные продукты"})


def test_fail_create_or_update_with_occupied_code(client):
    """
    Отказ с кодом 409 Conflict при попытке создания или обновления с уже занятым уникальным кодом.
    """
    groups_res = client.get("/api/entity/group_model")
    existing_code = groups_res.json()[0]["unique_code"]

    # 1. Попытка создать сущность с уже занятым кодом
    create_conflict_res = client.post(
        "/api/entity/group_model", json={"name": "Дубликат", "unique_code": existing_code}
    )
    assert create_conflict_res.status_code == 409

    # Создаем две новые свободные группы
    g1 = client.post("/api/entity/group_model", json={"name": "Свободная 1"}).json()
    g2 = client.post("/api/entity/group_model", json={"name": "Свободная 2"}).json()

    # 2. Попытка переименовать g1 с присвоением кода g2
    upd_conflict_res = client.put(
        f"/api/entity/group_model/{g1['unique_code']}",
        json={"name": "Свободная 1 переименованная", "unique_code": g2["unique_code"]},
    )
    assert upd_conflict_res.status_code == 409

    # Очистка созданных сущностей
    client.delete(f"/api/entity/group_model/{g1['unique_code']}")
    client.delete(f"/api/entity/group_model/{g2['unique_code']}")


def test_delete_entity_after_last_reference_removed(client):
    """
    Возможность удалить объект после снятия последней входящей ссылки на него.
    """
    g = client.post("/api/entity/group_model", json={"name": "Временная группа"}).json()
    group_code = g["unique_code"]
    ranges_res = client.get("/api/entity/range_model").json()
    range_code = ranges_res[0]["unique_code"]

    nom = client.post(
        "/api/entity/nomenclature_model",
        json={"name": "Временная номенклатура", "group_code": group_code, "range_code": range_code},
    ).json()
    nom_code = nom["unique_code"]

    # Группу пока нельзя удалить
    assert client.delete(f"/api/entity/group_model/{group_code}").status_code == 409

    # Удаляем единственную ссылающуюся номенклатуру
    assert client.delete(f"/api/entity/nomenclature_model/{nom_code}").status_code == 200

    # Теперь группу можно успешно удалить
    assert client.delete(f"/api/entity/group_model/{group_code}").status_code == 200


def test_multiple_references_preserve_lock_until_all_removed(client):
    """
    Сохранение запрета на удаление, если удалена только одна из нескольких ссылок.
    """
    g = client.post("/api/entity/group_model", json={"name": "Группа для двух ссылок"}).json()
    group_code = g["unique_code"]
    ranges_res = client.get("/api/entity/range_model").json()
    range_code = ranges_res[0]["unique_code"]

    # Создаем две номенклатуры, ссылающиеся на одну группу
    nom1 = client.post(
        "/api/entity/nomenclature_model",
        json={"name": "Товар 1", "group_code": group_code, "range_code": range_code},
    ).json()
    nom2 = client.post(
        "/api/entity/nomenclature_model",
        json={"name": "Товар 2", "group_code": group_code, "range_code": range_code},
    ).json()

    # Удаляем Товар 1
    assert client.delete(f"/api/entity/nomenclature_model/{nom1['unique_code']}").status_code == 200

    # Группа все еще заблокирована Товаром 2!
    del_group_attempt = client.delete(f"/api/entity/group_model/{group_code}")
    assert del_group_attempt.status_code == 409

    # Удаляем Товар 2
    assert client.delete(f"/api/entity/nomenclature_model/{nom2['unique_code']}").status_code == 200

    # Теперь все ссылки сняты — группа успешно удаляется
    assert client.delete(f"/api/entity/group_model/{group_code}").status_code == 200


def test_switch_dependency_from_entity_a_to_b(client):
    """
    Изменение зависимости с объекта A на объект B корректно обновляет проверки обоих объектов:
    объект A освобождается, а объект B блокируется.
    """
    g_a = client.post("/api/entity/group_model", json={"name": "Группа А"}).json()
    g_b = client.post("/api/entity/group_model", json={"name": "Группа Б"}).json()
    code_a = g_a["unique_code"]
    code_b = g_b["unique_code"]

    ranges_res = client.get("/api/entity/range_model").json()
    range_code = ranges_res[0]["unique_code"]

    nom = client.post(
        "/api/entity/nomenclature_model",
        json={"name": "Перемещаемый товар", "group_code": code_a, "range_code": range_code},
    ).json()
    nom_code = nom["unique_code"]

    # Группа А заблокирована, Группа Б свободна
    assert client.delete(f"/api/entity/group_model/{code_a}").status_code == 409
    assert client.delete(f"/api/entity/group_model/{code_b}").status_code == 200

    # Восстановим Группу Б
    g_b2 = client.post("/api/entity/group_model", json={"name": "Группа Б2"}).json()
    code_b2 = g_b2["unique_code"]

    # Переключаем зависимость номенклатуры с А на Б2
    upd_res = client.put(
        f"/api/entity/nomenclature_model/{nom_code}",
        json={"name": "Перемещаемый товар", "group_code": code_b2, "range_code": range_code},
    )
    assert upd_res.status_code == 200

    # Теперь Группа А освободилась и может быть удалена
    assert client.delete(f"/api/entity/group_model/{code_a}").status_code == 200

    # А Группа Б2 теперь заблокирована
    assert client.delete(f"/api/entity/group_model/{code_b2}").status_code == 409

    # Очистка
    client.delete(f"/api/entity/nomenclature_model/{nom_code}")
    client.delete(f"/api/entity/group_model/{code_b2}")


def test_validation_error_leaves_data_and_index_intact(client):
    """
    Ошибка валидации оставляет объект, коллекцию и индекс в прежнем состоянии.
    """
    # Создаем тестовую единицу измерения
    r = client.post("/api/entity/range_model", json={"name": "Тестовая пачка", "value": 10, "base_code": ""}).json()
    r_code = r["unique_code"]

    # Пытаемся передать отрицательное значение коэффициента пересчета (нарушение валидации)
    bad_res = client.put(
        f"/api/entity/range_model/{r_code}",
        json={"name": "Некорректная пачка", "value": -10, "base_code": ""},
    )
    assert bad_res.status_code == 400

    # Проверяем, что исходный объект в хранилище не был поврежден
    get_res = client.get(f"/api/entity/range_model/{r_code}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Тестовая пачка"
    assert get_res.json()["value"] == 10

    # Удаляем тестовый объект
    client.delete(f"/api/entity/range_model/{r_code}")


def test_storage_rebuild_cleans_stale_index(client):
    """
    Повторная загрузка/очистка данных не оставляет устаревший индекс связей.
    """
    # Добавляем временную сущность
    g = client.post("/api/entity/group_model", json={"name": "Временная группа перед сбросом"}).json()
    g_code = g["unique_code"]

    # Очищаем и заново строим данные хранилища
    main.app_storage_manager.clear()
    main.app_storage_manager.build()

    # Индекс связей автоматически синхронизирован и не содержит устаревший код
    is_linked, _ = main.app_storage_service.is_linked(g_code)
    assert is_linked == False
    assert g_code not in main.app_storage_service.outgoing_index

