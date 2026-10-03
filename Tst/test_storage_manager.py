import threading

import pytest

from Src.Core.abstract_manager import abstract_manager
from Src.Core.exception import arguments_exception
from Src.Core.storage_manager import storage_manager
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.storage_model import storage_model
from Src.Models.unit_model import unit_model


@pytest.fixture()
def manager():
    """
    Фикстура: предоставляет чистый экземпляр синглтона storage_manager.

    До теста синглтон сбрасывается и создается заново (первый старт с
    первичными данными), после теста - тоже сбрасывается, чтобы тесты
    не влияли друг на друга через общее состояние синглтона.
    """
    storage_manager.reset_instance()
    instance = storage_manager()
    yield instance
    storage_manager.reset_instance()


# ----------------------------------------------------------------------
# Шаблон Singleton
# ----------------------------------------------------------------------


def test_is_inherited_from_abstract_manager_success(manager):
    """
    storage_manager является наследником abstract_manager.
    """
    # Проверка
    assert isinstance(manager, abstract_manager)


def test_singleton_returns_same_instance_for_multiple_calls_success():
    """
    Повторные обращения к конструктору возвращают один и тот же объект.
    """
    # Подготовка
    storage_manager.reset_instance()

    # Действие
    first = storage_manager()
    second = storage_manager()
    third = storage_manager()

    # Проверка
    assert first is second is third

    # Очистка
    storage_manager.reset_instance()


def test_singleton_state_shared_between_references_success(manager):
    """
    Данные, добавленные через одну ссылку на синглтон, видны через другую.
    """
    # Подготовка
    another_reference = storage_manager()

    # Действие
    manager.add_storage(storage_model('Проверочный склад'))

    # Проверка
    assert another_reference is manager
    assert len(another_reference.find_by_name('storages', 'Проверочный склад')) == 1


def test_singleton_thread_safe_creation_success():
    """
    При параллельном создании из нескольких потоков экземпляр синглтона один.
    """
    # Подготовка
    storage_manager.reset_instance()
    instances: list[storage_manager] = []
    barrier = threading.Barrier(5)

    def create_instance() -> None:
        barrier.wait()
        instances.append(storage_manager())

    threads = [threading.Thread(target=create_instance) for _ in range(5)]

    # Действие
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # Проверка
    assert len(instances) == 5
    assert all(item is instances[0] for item in instances)

    # Очистка
    storage_manager.reset_instance()


def test_reset_instance_creates_new_object_success():
    """
    После reset_instance следующий вызов конструктора создает новый объект.
    """
    # Подготовка
    storage_manager.reset_instance()
    first = storage_manager()

    # Действие
    storage_manager.reset_instance()
    second = storage_manager()

    # Проверка
    assert first is not second

    # Очистка
    storage_manager.reset_instance()


# ----------------------------------------------------------------------
# CRUD-операции и уникальность элементов
# ----------------------------------------------------------------------


def test_add_and_get_storage_success(manager):
    """
    Добавленный склад возвращается по своему идентификатору тем же объектом.
    """
    # Подготовка
    new_storage = storage_model('Склад тест')

    # Действие
    added = manager.add_storage(new_storage)

    # Проверка
    assert added is new_storage
    assert manager.get_storage(new_storage.id) is new_storage
    assert new_storage in manager.storages


def test_add_duplicate_storage_id_raises_exception(manager):
    """
    Повторное добавление объекта с тем же id вызывает arguments_exception
    (каждый элемент хранилища уникален).
    """
    # Подготовка
    new_storage = storage_model('Уникальный склад')
    manager.add_storage(new_storage)
    duplicate = storage_model('Копия склада', id=new_storage.id)

    # Действие и проверка
    with pytest.raises(arguments_exception):
        manager.add_storage(duplicate)


@pytest.mark.parametrize('bad_value', ['string', 123, None])
def test_raise_arguments_exception_when_add_wrong_type_to_storages(bad_value, manager):
    """
    В хранилище складов нельзя добавить объект неверного типа.
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        manager.add_storage(bad_value)


def test_remove_storage_success(manager):
    """
    Удаление склада по id убирает объект из хранилища.
    """
    # Подготовка
    new_storage = storage_model('Временный склад')
    manager.add_storage(new_storage)

    # Действие
    manager.remove_storage(new_storage.id)

    # Проверка
    assert manager.get_storage(new_storage.id) is None
    assert new_storage not in manager.storages


def test_remove_missing_storage_does_not_raise_success(manager):
    """
    Удаление несуществующего id не является ошибкой.
    """
    # Действие и проверка без исключений
    manager.remove_storage('нет-такого-id')


def test_add_unit_group_nomenclature_success(manager):
    """
    Единица измерения, группа и номенклатура корректно добавляются и читаются.
    """
    # Подготовка
    base = unit_model('миллилитр базовый', 1)
    group = nomenclature_group_model('Группа теста', [base])
    item = nomenclature_model(name='Позиция теста', group=group, unit=base)

    # Действие
    manager.add_unit(base)
    manager.add_group(group)
    manager.add_nomenclature(item)

    # Проверка
    assert manager.get_unit(base.id) is base
    assert manager.get_group(group.id) is group
    assert manager.get_nomenclature(item.id) is item


def test_collections_are_independent(manager):
    """
    Хранилища разных видов сущностей независимы: одинаковый id в 'units'
    не мешает такому же id в 'storages'.
    """
    # Подготовка
    fixed_id = 'fixed-shared-id'
    new_unit = unit_model('Единица с фиксированным id', 1, id=fixed_id)
    new_storage = storage_model('Склад с фиксированным id', id=fixed_id)

    # Действие
    manager.add_unit(new_unit)
    manager.add_storage(new_storage)

    # Проверка
    assert manager.get_unit(fixed_id) is new_unit
    assert manager.get_storage(fixed_id) is new_storage


def test_get_with_empty_id_raises_exception(manager):
    """
    Пустой идентификатор при чтении вызывает arguments_exception.
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        manager.get_storage('')


def test_find_by_name_case_insensitive_success(manager):
    """
    Поиск по наименованию регистронезависимый и работает по всем хранилищам.
    """
    # Подготовка
    manager.add_unit(unit_model('Тестовая единица', 1))

    # Действие
    found = manager.find_by_name('units', 'тестовая ЕДИНИЦА')

    # Проверка
    assert len(found) == 1
    assert found[0].name == 'Тестовая единица'


def test_raise_arguments_exception_when_find_unknown_collection(manager):
    """
    Неизвестное имя хранилища при поиске вызывает arguments_exception.
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        manager.find_by_name('unknown_collection', 'что-то')


def test_clear_empties_all_collections(manager):
    """
    clear очищает все хранилища и сбрасывает признак первого старта.
    """
    # Проверка состояния до очистки (данные первого старта присутствуют)
    assert manager.initialized is True

    # Действие
    manager.clear()

    # Проверка
    assert manager.storages == []
    assert manager.units == []
    assert manager.groups == []
    assert manager.nomenclatures == []
    assert manager.initialized is False


# ----------------------------------------------------------------------
# Метод convert (реализация абстрактного метода)
# ----------------------------------------------------------------------


def test_convert_model_to_dict_success(manager):
    """
    Convert доменной модели возвращает словарь с типом, id и наименование.
    """
    # Подготовка
    new_unit = unit_model('Грамм конвертируемый', 1)

    # Действие
    result = manager.convert(new_unit)

    # Проверка
    assert isinstance(result, dict)
    assert result['type'] == 'unit_model'
    assert result['id'] == new_unit.id
    assert result['name'] == 'Грамм конвертируемый'


def test_convert_dict_to_storage_model_success(manager):
    """
    Convert словаря type='storage' создает корректный storage_model.
    """
    # Действие
    result = manager.convert({'type': 'storage', 'name': 'Склад из словаря',
                              'address': 'ул. Складская, 1'})

    # Проверка
    assert isinstance(result, storage_model)
    assert result.name == 'Склад из словаря'
    assert result.address == 'ул. Складская, 1'


def test_convert_dict_to_unit_model_success(manager):
    """
    Convert словаря type='unit' создает unit_model с коэффициентом и базовой единицей.
    """
    # Подготовка
    base = unit_model('базовая грамм', 1)

    # Действие
    result = manager.convert({'type': 'unit', 'name': 'кг из словаря',
                              'coefficient': 1000, 'base_unit': base})

    # Проверка
    assert isinstance(result, unit_model)
    assert result.coefficient == 1000
    assert result.base_unit is base


def test_convert_dict_to_group_and_nomenclature_success(manager):
    """
    Convert словарей type='group' и type='nomenclature' создает корректные модели.
    """
    # Подготовка
    base = unit_model('штука базовая', 1)

    # Действие
    group = manager.convert({'type': 'group', 'name': 'Группа из словаря',
                             'units': [base]})
    item = manager.convert({'type': 'nomenclature', 'name': 'Позиция из словаря',
                             'group': group, 'unit': base,
                             'full_name': 'Позиция из словаря полная'})

    # Проверка
    assert isinstance(group, nomenclature_group_model)
    assert group.units == [base]
    assert isinstance(item, nomenclature_model)
    assert item.group is group
    assert item.full_name == 'Позиция из словаря полная'


@pytest.mark.parametrize('bad_source', ['string', 123, None, [1]])
def test_raise_arguments_exception_when_convert_bad_source(bad_source, manager):
    """
    Convert не принимает источники, не являющиеся моделью или словарем.
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        manager.convert(bad_source)


def test_raise_arguments_exception_when_convert_unknown_type(manager):
    """
    Словарь с неизвестным полем type вызывает arguments_exception.
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        manager.convert({'type': 'spaceship', 'name': 'Enterprise'})


def test_raise_arguments_exception_when_convert_without_name(manager):
    """
    Словарь без корректного наименования вызывает arguments_exception.
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        manager.convert({'type': 'storage', 'name': '   '})


# ----------------------------------------------------------------------
# Первый старт: проверка сформированных первичных данных
# ----------------------------------------------------------------------


def test_first_start_marks_initialized_success(manager):
    """
    После первого создания экземпляра признак первого старта установлен.
    """
    # Проверка
    assert manager.initialized is True


def test_first_start_creates_expected_units_success(manager):
    """
    При первом старте сформированы ожидаемые единицы измерения:
    базовые (грамм, мл, шт) и производные (кг, л, дюжина) с корректными коэффициентами.
    """
    # Действие
    units = {unit.name: unit for unit in manager.units}

    # Проверка
    assert set(units) == {'грамм', 'кг', 'мл', 'л', 'шт', 'дюжина'}
    assert units['грамм'].is_base is True
    assert units['кг'].coefficient == 1000
    assert units['кг'].base_unit is units['грамм']
    assert units['л'].base_unit is units['мл']
    assert units['дюжина'].to_base(1) == 12
    # Все объекты уникальны по id
    ids = [unit.id for unit in manager.units]
    assert len(ids) == len(set(ids))


def test_first_start_creates_twelve_storages_success(manager):
    """
    При первом старте сформированы 12 складов: центральный, цех и 10 ресторанов.
    """
    # Проверка
    assert len(manager.storages) == 12
    names = {item.name for item in manager.storages}
    assert 'Центральный склад' in names
    assert 'Склад производственного цеха' in names
    assert 'Склад ресторана №1' in names
    assert 'Склад ресторана №10' in names
    # Каждый элемент уникален
    ids = [item.id for item in manager.storages]
    assert len(ids) == len(set(ids))


def test_first_start_creates_expected_groups_success(manager):
    """
    При первом старте сформированы четыре группы номенклатуры,
    каждая содержит непустой список единиц измерения из хранилища.
    """
    # Действие
    groups = {group.name: group for group in manager.groups}

    # Проверка
    assert set(groups) == {'Молочные продукты', 'Мясные продукты',
                           'Бакалея', 'Напитки'}
    stored_unit_ids = {unit.id for unit in manager.units}
    for group in groups.values():
        assert len(group.units) > 0
        assert all(unit.id in stored_unit_ids for unit in group.units)


def test_first_start_creates_expected_nomenclatures_success(manager):
    """
    При первом старте сформированы восемь позиций номенклатуры;
    каждая ссылается на существующие группу и единицу измерения.
    """
    # Подготовка
    expected_names = {'Молоко', 'Сметана', 'Говядина', 'Курица',
                      'Мука', 'Сахар', 'Соль', 'Вода'}
    group_ids = {group.id for group in manager.groups}
    unit_ids = {unit.id for unit in manager.units}

    # Действие
    names = {item.name for item in manager.nomenclatures}

    # Проверка
    assert names == expected_names
    for item in manager.nomenclatures:
        assert item.group.id in group_ids
        assert item.unit.id in unit_ids
        assert item.full_name is not None


def test_initialize_is_idempotent_success(manager):
    """
    Повторные вызовы initialize не удваивают первичные данные.
    """
    # Подготовка
    counts_before = (len(manager.storages), len(manager.units),
                     len(manager.groups), len(manager.nomenclatures))

    # Действие
    manager.initialize()
    manager.initialize()

    # Проверка
    counts_after = (len(manager.storages), len(manager.units),
                    len(manager.groups), len(manager.nomenclatures))
    assert counts_before == counts_after


def test_second_start_does_not_recreate_initial_data_success(manager):
    """
    Пользовательские данные не затираются, а первичные не дублируются
    при повторном обращении к синглтону (второй и последующие "старты").
    """
    # Подготовка
    manager.add_unit(unit_model('Ложка столовая', 15,
                                manager.find_by_name('units', 'мл')[0]))

    # Действие: повторное обращение к синглтону
    again = storage_manager()

    # Проверка
    assert again is manager
    assert len(again.units) == 7
    assert len(again.find_by_name('units', 'грамм')) == 1
