import pytest
import main
from Src.Logics.logger_service import logger_service


@pytest.fixture
def client():
    """Фикстура для создания тестового HTTP-клиента приложения."""
    main.app_settings_manager.settings.first_start = True
    main.app_storage_manager.build()
    logger_service().clear()
    return main.api.test_client()


def test_crud_triggers_logging(client):
    """
    Проверка, что CRUD-операции над сущностями и вызовы Web-методов автоматически логируются.
    """
    logger = logger_service()
    logger.clear()

    # 1. Создание сущности -> логируется INFO
    payload = {"name": "Новая тестовая группа для лога"}
    response = client.post("/api/entity/group_model", json=payload)
    assert response.status_code == 201
    group_data = response.json()
    code = group_data["unique_code"]

    crud_logs = [l for l in logger.logs if l.subsystem == "storage_service"]
    assert len(crud_logs) >= 1
    create_log = crud_logs[-1]
    assert create_log.level == "INFO"
    assert "Создана сущность" in create_log.message
    assert code in create_log.message

    # Проверка, что вызов Web-метода также залогирован
    web_logs = [l for l in logger.logs if l.subsystem == "web_api"]
    assert len(web_logs) >= 2

    # 2. Обновление сущности -> логируется INFO
    update_payload = {"unique_code": code, "name": "Обновленная тестовая группа"}
    response_update = client.put(f"/api/entity/group_model/{code}", json=update_payload)
    assert response_update.status_code == 200

    crud_logs = [l for l in logger.logs if l.subsystem == "storage_service"]
    assert len(crud_logs) >= 2
    update_log = crud_logs[-1]
    assert update_log.level == "INFO"
    assert "Обновлена сущность" in update_log.message

    # 3. Удаление сущности -> логируется INFO
    response_delete = client.delete(f"/api/entity/group_model/{code}")
    assert response_delete.status_code == 200

    crud_logs = [l for l in logger.logs if l.subsystem == "storage_service"]
    assert len(crud_logs) >= 3
    delete_log = crud_logs[-1]
    assert delete_log.level == "INFO"
    assert "Удалена сущность" in delete_log.message


def test_crud_error_triggers_error_logging(client):
    """
    Проверка, что ошибки при выполнении CRUD-операций логируются с уровнем ERROR.
    """
    logger = logger_service()
    logger.clear()

    # Попытка удалить несуществующую сущность
    response = client.delete("/api/entity/group_model/non_existing_unique_code_123")
    assert response.status_code == 404

    crud_logs = [l for l in logger.logs if l.subsystem == "storage_service"]
    assert len(crud_logs) >= 1
    error_log = crud_logs[-1]
    assert error_log.level == "ERROR"
    assert "Ошибка удаления" in error_log.message


def test_api_get_logs_json_and_query_filter(client):
    """
    Проверка GET /api/log: получение логов в формате JSON с фильтрацией и сортировкой.
    """
    logger = logger_service()
    logger.clear()
    logger.info("auth", "Успешная авторизация")
    logger.error("storage_service", "Ошибка сохранения данных")
    logger.debug("network", "Пинг сервера 20мс")

    # Получение всех логов
    resp = client.get("/api/log")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 3

    # Фильтрация по level=ERROR
    resp_err = client.get("/api/log?level=ERROR")
    assert resp_err.status_code == 200
    err_data = resp_err.json()
    assert len(err_data) == 1
    assert err_data[0]["level"] == "ERROR"
    assert err_data[0]["subsystem"] == "storage_service"

    # Сортировка по subsystem desc
    resp_sort = client.get("/api/log?sort_by=subsystem&sort_order=desc")
    assert resp_sort.status_code == 200
    sort_data = resp_sort.json()
    assert sort_data[0]["subsystem"] == "storage_service"


def test_api_post_filter_logs(client):
    """
    Проверка POST /api/log с телом фильтрации.
    """
    logger = logger_service()
    logger.clear()
    logger.info("storage_service", "Создание записи 1")
    logger.info("storage_service", "Создание записи 2")
    logger.error("storage_service", "Ошибка записи 3")

    payload = {
        "filters": [
            {"field_name": "level", "filter_type": "EQUALS", "value": "INFO"}
        ],
        "sort_by": "message",
        "sort_order": "asc"
    }

    resp = client.post("/api/log", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert all(x["level"] == "INFO" for x in data)


def test_api_export_logs(client):
    """
    Проверка GET /api/log/export для форматов txt, csv, markdown.
    """
    logger = logger_service()
    logger.clear()
    logger.info("storage_service", "Создана новая позиция")
    logger.error("storage_service", "Конфликт уникального кода")

    # Экспорт в TXT
    resp_txt = client.get("/api/log/export?format=txt")
    assert resp_txt.status_code == 200
    assert "text/plain" in resp_txt.headers["content-type"]
    assert "Период" in resp_txt.text
    assert "attachment; filename=\"logs.txt\"" in resp_txt.headers.get("content-disposition", "")

    # Экспорт в CSV
    resp_csv = client.get("/api/log/export?format=csv")
    assert resp_csv.status_code == 200
    assert "text/csv" in resp_csv.headers["content-type"]
    assert "attachment; filename=\"logs.csv\"" in resp_csv.headers.get("content-disposition", "")
    assert "storage_service;INFO;Создана новая позиция" in resp_csv.text

    # Экспорт в MARKDOWN
    resp_md = client.get("/api/log/export?format=markdown")
    assert resp_md.status_code == 200
    assert "text/markdown" in resp_md.headers["content-type"]
    assert "| Период | Название подсистемы | Тип сообщения | Сообщение |" in resp_md.text
