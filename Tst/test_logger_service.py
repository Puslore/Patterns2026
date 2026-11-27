from datetime import datetime, timedelta
import pytest
from Src.Core.log_level_enum import log_level_enum
from Src.Core.validator import argument_exception
from Src.Models.log_model import log_model
from Src.Dtos.log_dto import log_dto
from Src.Logics.logger_service import logger_service


def test_log_level_enum():
    """Проверка работы перечисления уровней логирования."""
    assert log_level_enum.INFO.value == "INFO"
    assert log_level_enum.ERROR.value == "ERROR"
    assert log_level_enum.DEBUG.value == "DEBUG"
    assert log_level_enum.from_value("info") == log_level_enum.INFO
    assert log_level_enum.from_value("error") == log_level_enum.ERROR
    assert log_level_enum.from_value("debug") == log_level_enum.DEBUG
    assert log_level_enum.from_value(None) == log_level_enum.INFO


def test_log_model_fields_and_validation():
    """Проверка полей и валидации модели log_model."""
    item = log_model.create("test_subsystem", log_level_enum.INFO, "Тестовое сообщение")
    assert item.subsystem == "test_subsystem"
    assert item.level == "INFO"
    assert item.message == "Тестовое сообщение"
    assert isinstance(item.period, datetime)
    assert len(item.unique_code) > 0

    # Проверка строковой даты
    item.period = "2026-11-24 15:30:00"
    assert item.period.year == 2026
    assert item.period.month == 11
    assert item.period.day == 24

    with pytest.raises(argument_exception):
        item.subsystem = ""

    with pytest.raises(argument_exception):
        item.message = ""

    with pytest.raises(argument_exception):
        item.period = "невалидная дата"


def test_log_dto_conversion():
    """Проверка конвертации log_model <-> log_dto."""
    model = log_model.create("storage", "ERROR", "Сбой при удалении")
    dto = log_dto().from_domain_model(model)

    assert dto.unique_code == model.unique_code
    assert dto.subsystem == "storage"
    assert dto.level == "ERROR"
    assert dto.message == "Сбой при удалении"
    assert len(dto.period) > 0

    cache = {}
    restored = dto.mapping(cache)
    assert restored.unique_code == model.unique_code
    assert restored.subsystem == "storage"
    assert restored.level == "ERROR"
    assert restored.message == "Сбой при удалении"


def test_logger_service_add_and_clear():
    """Проверка добавления логов и очистки в logger_service."""
    svc = logger_service()
    svc.clear()
    assert len(svc.logs) == 0

    svc.info("subsystem_a", "Инфо 1")
    svc.error("subsystem_b", "Ошибка 1")
    svc.debug("subsystem_a", "Отладка 1")

    assert len(svc.logs) == 3
    assert svc.logs[0].level == "INFO"
    assert svc.logs[1].level == "ERROR"
    assert svc.logs[2].level == "DEBUG"

    svc.clear()
    assert len(svc.logs) == 0


def test_logger_service_filtering_and_sorting():
    """Проверка фильтрации через Прототип и сортировки в logger_service."""
    svc = logger_service()
    svc.clear()

    l1 = svc.info("storage", "Создана номенклатура")
    l1.period = datetime(2026, 11, 20, 10, 0, 0)

    l2 = svc.error("storage", "Ошибка удаления склада")
    l2.period = datetime(2026, 11, 22, 12, 0, 0)

    l3 = svc.debug("auth", "Вход пользователя")
    l3.period = datetime(2026, 11, 21, 11, 0, 0)

    # Фильтр по подсистеме
    filtered = svc.get_logs(filter_data={"filters": [{"field_name": "subsystem", "filter_type": "EQUALS", "value": "storage"}]})
    assert len(filtered) == 2
    assert all(x.subsystem == "storage" for x in filtered)

    # Фильтр по уровню ERROR
    filtered_err = svc.get_logs(filter_data={"filters": [{"field_name": "level", "filter_type": "EQUALS", "value": "ERROR"}]})
    assert len(filtered_err) == 1
    assert filtered_err[0].message == "Ошибка удаления склада"

    # Сортировка по дате (asc)
    sorted_asc = svc.get_logs(sort_by="period", sort_order="asc")
    assert sorted_asc[0].period == datetime(2026, 11, 20, 10, 0, 0)
    assert sorted_asc[1].period == datetime(2026, 11, 21, 11, 0, 0)
    assert sorted_asc[2].period == datetime(2026, 11, 22, 12, 0, 0)

    # Сортировка по дате (desc)
    sorted_desc = svc.get_logs(sort_by="period", sort_order="desc")
    assert sorted_desc[0].period == datetime(2026, 11, 22, 12, 0, 0)
    assert sorted_desc[2].period == datetime(2026, 11, 20, 10, 0, 0)


def test_logger_service_export_txt_csv_markdown():
    """Проверка экспорта логов в текстовый, CSV и markdown форматы."""
    svc = logger_service()
    svc.clear()
    svc.info("subsystem_1", "Действие успешно")
    svc.error("subsystem_2", "Произошла ошибка")

    logs = svc.logs

    # TXT
    res_txt = svc.export(logs, "txt")
    assert "text/plain" in res_txt.format
    assert "Период" in res_txt.text
    assert "subsystem_1" in res_txt.text
    assert "Действие успешно" in res_txt.text

    # CSV
    res_csv = svc.export(logs, "csv")
    assert "text/csv" in res_csv.format
    assert "Период;Название подсистемы;Тип сообщения;Сообщение" in res_csv.text
    assert "subsystem_1;INFO;Действие успешно" in res_csv.text

    # MARKDOWN
    res_md = svc.export(logs, "markdown")
    assert "text/markdown" in res_md.format
    assert "| Период | Название подсистемы | Тип сообщения | Сообщение |" in res_md.text
    assert "| subsystem_1 | INFO | Действие успешно |" in res_md.text

    # Неподдерживаемый формат
    with pytest.raises(argument_exception):
        svc.export(logs, "unknown_format")


def test_logger_service_observes_all_required_operations():
    """
    Проверка, что logger_service как Наблюдатель (abstract_observabile) перехватывает все 4 типа операций:
    1. CRUD-операции
    2. Складские операции
    3. Вызовы Web-методов
    4. Изменение параметров настроек
    """
    from Src.Logics.observer import observer
    from Src.Core.event_type import event_type

    svc = logger_service()
    svc.clear()

    # 1. CRUD операция через observer
    observer.create(event_type.create_entity(), {
        "subsystem": "storage_service",
        "level": log_level_enum.INFO,
        "message": "Создана доменная модель группы"
    })

    # 2. Складская операция через observer
    observer.create(event_type.warehouse_operation(), {
        "subsystem": "storage_manager",
        "level": log_level_enum.INFO,
        "message": "Поступление товара: Свёкла, 50 кг"
    })

    # 3. Вызов Web-метода через observer
    observer.create(event_type.web_request(), {
        "subsystem": "web_api",
        "level": log_level_enum.INFO,
        "message": "Вызов Web-метода GET /api/entity/group_model"
    })

    # 4. Изменение настроек через observer
    observer.create(event_type.change_settings())

    logs = svc.logs
    assert len(logs) == 4

    subsystems = [x.subsystem for x in logs]
    assert "storage_service" in subsystems
    assert "storage_manager" in subsystems
    assert "web_api" in subsystems
    assert "settings_manager" in subsystems

    assert any("Создана доменная модель" in x.message for x in logs)
    assert any("Поступление товара" in x.message for x in logs)
    assert any("Вызов Web-метода" in x.message for x in logs)
    assert any("Изменены параметры настроек" in x.message for x in logs)

