from Src.Models.settings_model import settings_model
from Src.Logics.storage_manager import storage_manager
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_item_dto import filter_item_dto
from Src.Core.filter_type_enum import filter_type_enum
from Src.Logics.prototype import prototype
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model
from Src.Models.nomenclature_model import nomenclature_model
from datetime import datetime


"""
Проверить работу прототипа из примера преподавателя
"""
def test_contains_data_prototype():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()
    filter = filter_dto()
    item = filter_item_dto()

    item.__field_name = "name"
    item.__filter_type = "eq"
    item.__value = "Киллограм"
    filter.__filters = [ item ]
    pr = prototype( manager.data[ storage_manager.transaction_key() ] )

    # Действие
    result = pr.clone( filter )

    # Проверки
    assert len(result.__data) > 0


"""
Проверить фильтрацию номенклатуры по полному совпадению (EQUALS)
"""
def test_prototype_filter_nomenclature_equals():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()

    flt = filter_dto()
    flt.add_filter("name", filter_type_enum.EQUALS, "Свёкла")
    pr = prototype(manager.data[storage_manager.nomenclature_key()])

    # Действие
    result = pr.clone(flt)

    # Проверки
    assert len(result.data) == 1
    assert result.data[0].name == "Свёкла"


"""
Проверить фильтрацию номенклатуры по подстроке (LIKE)
"""
def test_prototype_filter_nomenclature_like():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()

    flt = filter_dto()
    flt.add_filter("name", filter_type_enum.LIKE, "мука")
    pr = prototype(manager.data[storage_manager.nomenclature_key()])

    # Действие
    result = pr.clone(flt)

    # Проверки
    assert len(result.data) == 1
    assert result.data[0].name == "Пшеничная мука"


"""
Проверить фильтрацию группы по уникальному коду
"""
def test_prototype_filter_group_unique_code():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()

    target_group = manager.data[storage_manager.group_key()][1]
    flt = filter_dto()
    flt.unique_code = target_group.unique_code

    pr = prototype(manager.data[storage_manager.group_key()])

    # Действие
    result = pr.clone(flt)

    # Проверки
    assert len(result.data) == 1
    assert result.data[0].unique_code == target_group.unique_code
    assert result.data[0].name == target_group.name


"""
Проверить фильтрацию единицы измерения по вложенной структуре (базовая единица измерения)
"""
def test_prototype_filter_range_nested_base():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()

    ranges = manager.data[storage_manager.range_key()]
    flt = filter_dto()
    # Поиск по свойству базовой единицы 'base.name'
    flt.add_filter("base.name", filter_type_enum.EQUALS, "Грамм")
    pr = prototype(ranges)

    # Действие
    result = pr.clone(flt)

    # Проверки
    assert len(result.data) >= 1
    assert any(r.name == "Киллограм" for r in result.data)


"""
Проверить рекурсивный поиск во вложенных структурах единиц измерения
"""
def test_prototype_filter_range_nested_recursive():
    # Подготовка
    gramm = range_model()
    gramm.name = "Грамм"

    kilo = range_model()
    kilo.name = "Килограмм"
    kilo.base = gramm

    ton = range_model()
    ton.name = "Тонна"
    ton.base = kilo

    # Ищем единицу, где во вложенной структуре есть "Грамм"
    flt = filter_dto()
    flt.add_filter("name", filter_type_enum.EQUALS, "Грамм")
    pr = prototype([ton])

    # Действие
    result = pr.clone(flt)

    # Проверки: Тонна должна быть найдена, так как ее вложенная базовая единица — Грамм
    assert len(result.data) == 1
    assert result.data[0].name == "Тонна"


"""
Проверить поиск во вложенной структуре групп (группа - группа владелец)
"""
def test_prototype_filter_group_nested_parent():
    # Подготовка
    parent_group = group_model.create("Продукты питания")
    child_group = group_model.create("Молочная продукция")
    child_group.parent = parent_group

    flt = filter_dto()
    flt.add_filter("parent.name", filter_type_enum.EQUALS, "Продукты питания")
    pr = prototype([child_group])

    # Действие
    result = pr.clone(flt)

    # Проверки
    assert len(result.data) == 1
    assert result.data[0].name == "Молочная продукция"

    # Проверка через рекурсивный поиск по имени группы-владельца
    flt_recursive = filter_dto()
    flt_recursive.add_filter("name", filter_type_enum.EQUALS, "Продукты питания")
    result_rec = pr.clone(flt_recursive)
    assert len(result_rec.data) == 1


"""
Проверить фильтрацию рецепта по вложенным ингредиентам
"""
def test_prototype_filter_receipt_by_nested_ingredient():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()

    receipts = manager.data[storage_manager.receipt_key()]
    flt = filter_dto()
    # Ищем рецепт, содержащий ингредиент со словом 'Говядина'
    flt.add_filter("name", filter_type_enum.LIKE, "Говядина")
    pr = prototype(receipts)

    # Действие
    result = pr.clone(flt)

    # Проверки: Борщ содержит говядину, поэтому рецепт должен быть найден
    assert len(result.data) == 1
    assert result.data[0].name == "Борщ столичный"


"""
Проверить фильтрацию транзакций по номенклатуре и складу
"""
def test_prototype_filter_transactions():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()

    transactions = manager.data[storage_manager.transaction_key()]
    flt = filter_dto()
    flt.add_filter("nomenclature.name", filter_type_enum.EQUALS, "Свёкла")
    pr = prototype(transactions)

    # Действие
    result = pr.clone(flt)

    # Проверки: должно быть 2 транзакции по свёкле (приход 50 и расход 8)
    assert len(result.data) == 2
    assert all(t.nomenclature.name == "Свёкла" for t in result.data)


"""
Проверить возврат всех данных при пустом фильтре
"""
def test_prototype_clone_empty_filter():
    # Подготовка
    items = [group_model.create("А"), group_model.create("Б")]
    pr = prototype(items)

    # Действие
    result_none = pr.clone(None)
    result_empty = pr.clone(filter_dto())

    # Проверки
    assert len(result_none.data) == 2
    assert len(result_empty.data) == 2


"""
Проверить поиск по цепочке базовых единиц измерения (base.base.name)
"""
def test_prototype_filter_range_nested_base_chain():
    # Подготовка
    gramm = range_model()
    gramm.name = "Грамм"

    kilo = range_model()
    kilo.name = "Киллограм"
    kilo.base = gramm

    ton = range_model()
    ton.name = "Тонна"
    ton.base = kilo

    flt = filter_dto()
    flt.add_filter("base.name", filter_type_enum.EQUALS, "Грамм")
    pr = prototype([ton])

    # Действие
    result = pr.clone(flt)

    # Проверки: базовая единица находится на втором уровне вложенности
    assert len(result.data) == 1
    assert result.data[0].name == "Тонна"


"""
Проверить фильтрацию транзакций по дате через операторы сравнения
"""
def test_prototype_filter_transactions_by_period():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()

    transactions = manager.data[storage_manager.transaction_key()]

    flt = filter_dto()
    flt.add_filter(
        "period",
        filter_type_enum.LESS_EQUAL,
        datetime(2026, 11, 1, 23, 59),
    )

    # Действие
    result = prototype(transactions).clone(flt)

    # Проверки: за 1 ноября было три поступления
    assert len(result.data) == 3
    assert all(item.period.day == 1 for item in result.data)


"""
Проверить поиск по группе-владельцу через алиас owner
"""
def test_prototype_filter_group_nested_owner():
    # Подготовка
    parent_group = group_model.create("Продукты питания")
    child_group = group_model.create("Молочные продукты")
    child_group.owner = parent_group

    flt = filter_dto()
    flt.add_filter("owner.name", filter_type_enum.EQUALS, "Продукты питания")
    pr = prototype([child_group])

    # Действие
    result = pr.clone(flt)

    # Проверки
    assert len(result.data) == 1
    assert result.data[0].name == "Молочные продукты"
