from Src.Models.settings_model import settings_model
from Src.Logics.storage_manager import storage_manager
from Src.Dtos.filter_dto import filter_dto
from Src.Core.filter_type_enum import filter_type_enum
from Src.Logics.osv_prototype import osv_prototype


"""
Проверить формирование полной оборотно-сальдовой ведомости (ОСВ) через Прототип
"""
def test_create_full_osv():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()

    transactions = manager.data[storage_manager.transaction_key()]
    pr = osv_prototype(transactions)

    # Действие: формирование ОСВ без фильтра
    osv_items = pr.clone().data

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
Проверить формирование ОСВ с фильтрацией по номенклатуре через Прототип
"""
def test_create_osv_filtered_by_nomenclature():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()

    transactions = manager.data[storage_manager.transaction_key()]
    pr = osv_prototype(transactions)

    # Фильтр только по свёкле
    flt = filter_dto()
    flt.add_filter("nomenclature.name", filter_type_enum.EQUALS, "Свёкла")

    # Действие
    osv_items = pr.clone(flt).data

    # Проверки
    assert len(osv_items) == 1
    row = osv_items[0]
    assert row.nomenclature_name == "Свёкла"
    assert row.turnover_in == 50.0
    assert row.turnover_out == 8.0
    assert row.final_balance == 42.0


"""
Проверить формирование ОСВ с фильтрацией по части наименования (LIKE) через Прототип
"""
def test_create_osv_filtered_by_like():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()

    transactions = manager.data[storage_manager.transaction_key()]
    pr = osv_prototype(transactions)

    flt = filter_dto()
    flt.name = "Картоф"
    flt.filter_type = filter_type_enum.LIKE

    # Действие
    osv_items = pr.clone(flt).data

    # Проверки
    assert len(osv_items) == 1
    assert osv_items[0].nomenclature_name == "Картофель"


"""
Проверить преобразование строки ОСВ в словарь to_dict
"""
def test_osv_item_dto_to_dict():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()

    transactions = manager.data[storage_manager.transaction_key()]
    pr = osv_prototype(transactions)

    flt = filter_dto()
    flt.name = "Говядина"
    osv_items = pr.clone(flt).data

    assert len(osv_items) == 1
    d = osv_items[0].to_dict()

    assert isinstance(d, dict)
    assert d["nomenclature_name"] == "Говядина"
    assert d["turnover_in"] == 40.0
    assert d["turnover_out"] == 7.0
    assert d["final_balance"] == 33.0
    assert d["storage_name"] == "Основной склад"
