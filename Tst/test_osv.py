from datetime import datetime

import pytest

from Src.Core.filter_type_enum import filter_type_enum
from Src.Core.validator import argument_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.osv_item_dto import osv_item_dto
from Src.Logics.osv_service import osv_service
from Src.Logics.storage_manager import storage_manager
from Src.Models.settings_model import settings_model


def create_osv_service() -> osv_service:
    """
    Подготовить сервис ОСВ на полном наборе доменных данных.
    """
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    return osv_service(manager)


"""
Проверить формирование полной оборотно-сальдовой ведомости (ОСВ) через сервис
"""
def test_create_full_osv():
    # Подготовка
    service = create_osv_service()

    # Действие: формирование ОСВ без фильтра
    osv_items = service.build_items()

    # Проверки
    assert len(osv_items) > 0
    # Проверка балансового равенства: Конечный остаток = Начальный + Приход - Расход
    for row in osv_items:
        assert row.final_balance == row.initial_balance + row.turnover_in - row.turnover_out
        assert row.storage_name == "Основной склад"

    # Ищем строку по свёкле (приход 50, расход 8, остаток 42)
    beet_row = next((r for r in osv_items if r.nomenclature_name == "Свёкла"), None)
    assert beet_row is not None
    assert beet_row.turnover_in == 50.0
    assert beet_row.turnover_out == 8.0
    assert beet_row.final_balance == 42.0

    # Ищем строку по картофелю (приход 100, расход 6, остаток 94)
    potato_row = next((r for r in osv_items if r.nomenclature_name == "Картофель"), None)
    assert potato_row is not None
    assert potato_row.turnover_in == 100.0
    assert potato_row.turnover_out == 6.0
    assert potato_row.final_balance == 94.0

    # Ищем строку по говядине (приход 40, расход 7, остаток 33)
    beef_row = next((r for r in osv_items if r.nomenclature_name == "Говядина"), None)
    assert beef_row is not None
    assert beef_row.turnover_in == 40.0
    assert beef_row.turnover_out == 7.0
    assert beef_row.final_balance == 33.0


"""
Проверить формирование ОСВ с фильтрацией по номенклатуре
"""
def test_create_osv_filtered_by_nomenclature():
    # Подготовка
    service = create_osv_service()

    # Фильтр только по свёкле
    flt = filter_dto()
    flt.add_filter("nomenclature.name", filter_type_enum.EQUALS, "Свёкла")

    # Действие
    osv_items = service.build_items(flt)

    # Проверки
    assert len(osv_items) == 1
    row = osv_items[0]
    assert row.nomenclature_name == "Свёкла"
    assert row.turnover_in == 50.0
    assert row.turnover_out == 8.0
    assert row.final_balance == 42.0


"""
Проверить формирование ОСВ с фильтрацией по части наименования (LIKE)
"""
def test_create_osv_filtered_by_like():
    # Подготовка
    service = create_osv_service()

    flt = filter_dto()
    flt.name = "Картоф"
    flt.filter_type = filter_type_enum.LIKE

    # Действие
    osv_items = service.build_items(flt)

    # Проверки
    assert len(osv_items) == 1
    assert osv_items[0].nomenclature_name == "Картофель"


"""
Проверить расчет начальных остатков и оборотов за указанный период
"""
def test_osv_period_initial_and_turnover():
    # Подготовка
    service = create_osv_service()

    # Действие: период с 5 по 30 ноября
    osv_items = service.build_items(
        {"start_date": "2026-11-05", "end_date": "2026-11-30"}
    )
    rows = {row.nomenclature_name: row for row in osv_items}

    # Проверки: на 5 ноября уже были поступления, в период попали только списания
    assert rows["Свёкла"].initial_balance == 50.0
    assert rows["Свёкла"].turnover_in == 0.0
    assert rows["Свёкла"].turnover_out == 8.0
    assert rows["Свёкла"].final_balance == 42.0

    assert rows["Картофель"].initial_balance == 100.0
    assert rows["Картофель"].turnover_out == 6.0
    assert rows["Картофель"].final_balance == 94.0

    assert rows["Говядина"].initial_balance == 40.0
    assert rows["Говядина"].turnover_out == 7.0
    assert rows["Говядина"].final_balance == 33.0

    assert rows["Яйцо (шт)"].initial_balance == 100.0
    assert rows["Яйцо (шт)"].final_balance == 100.0

    assert rows["Пшеничная мука"].initial_balance == 60.0
    assert rows["Пшеничная мука"].final_balance == 60.0


"""
Проверить, что дата начала периода включается в начальный остаток
"""
def test_osv_period_start_inclusive():
    # Подготовка
    service = create_osv_service()

    # Действие: период из одного дня, когда были только поступления
    osv_items = service.build_items(
        {"start_date": "2026-11-01", "end_date": "2026-11-01"}
    )
    rows = {row.nomenclature_name: row for row in osv_items}

    # Проверки
    assert set(rows.keys()) == {"Свёкла", "Картофель", "Говядина"}
    assert rows["Свёкла"].initial_balance == 50.0
    assert rows["Свёкла"].turnover_in == 0.0
    assert rows["Свёкла"].final_balance == 50.0
    assert rows["Картофель"].initial_balance == 100.0
    assert rows["Говядина"].initial_balance == 40.0


"""
Проверить десериализацию периода из DTO фильтра
"""
def test_filter_dto_parses_period():
    # Действие
    dto = filter_dto().from_dict(
        {"start_date": "2026-11-05", "end_date": "2026-11-30"}
    )

    # Проверки
    assert dto.start_date.date() == datetime(2026, 11, 5).date()
    assert dto.end_date.date() == datetime(2026, 11, 30).date()


"""
Проверить ошибку при некорректном периоде
"""
def test_osv_invalid_period():
    # Подготовка
    service = create_osv_service()

    # Действие и проверка
    with pytest.raises(argument_exception):
        service.build_items(
            {"start_date": "2026-11-30", "end_date": "2026-11-01"}
        )


"""
Проверить сериализацию и обратную десериализацию строки ОСВ
"""
def test_osv_serialization_roundtrip():
    # Подготовка
    service = create_osv_service()

    # Действие: сервис сериализует строки через конвертор
    data = service.build({"name": "Говядина", "filter_type": "EQUALS"})

    # Проверки
    assert len(data) == 1
    assert data[0]["nomenclature_name"] == "Говядина"
    assert data[0]["final_balance"] == 33.0
    assert "type" in data[0]

    restored = osv_item_dto().from_dict(data[0])
    assert restored.nomenclature_name == "Говядина"
    assert restored.turnover_in == 40.0
    assert restored.turnover_out == 7.0
    assert restored.final_balance == 33.0


"""
Проверить преобразование строки ОСВ в словарь to_dict
"""
def test_osv_item_dto_to_dict():
    # Подготовка
    service = create_osv_service()

    flt = filter_dto()
    flt.name = "Говядина"
    osv_items = service.build_items(flt)

    assert len(osv_items) == 1
    d = osv_items[0].to_dict()

    assert isinstance(d, dict)
    assert d["nomenclature_name"] == "Говядина"
    assert d["turnover_in"] == 40.0
    assert d["turnover_out"] == 7.0
    assert d["final_balance"] == 33.0
    assert d["storage_name"] == "Основной склад"
