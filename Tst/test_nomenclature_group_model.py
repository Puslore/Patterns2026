import pytest

from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exception
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.unit_model import unit_model, NAME_MAX_LENGTH


def test_group_created_with_minimal_parameters_success():
    """
    Группа номенклатуры корректно создается только с наименованием:
    единицы измерения пусты, id генерируется автоматически.
    """
    # Действие
    group = nomenclature_group_model("Молочные продукты")

    # Проверка
    assert isinstance(group, abstract_model)
    assert group.name == "Молочные продукты"
    assert group.units == []
    assert group.id != ""


def test_group_created_with_all_parameters_success():
    """
    Группа номенклатуры корректно создается со всеми параметрами:
    наименование, список единиц измерения и явный идентификатор.
    """
    # Подготовка
    unit_gramm = unit_model("грамм", 1)
    unit_kg = unit_model("кг", 1000, unit_gramm)

    # Действие
    group = nomenclature_group_model("Сыпучие", [unit_gramm, unit_kg], id="group-1")

    # Проверка
    assert group.id == "group-1"
    assert len(group.units) == 2
    assert group.units[0] is unit_gramm
    assert group.units[1] is unit_kg


def test_add_unit_included_in_group_success():
    """
    Метод add_unit добавляет единицу измерения в группу.
    """
    # Подготовка
    group = nomenclature_group_model("Овощи")
    unit_pcs = unit_model("шт", 1)

    # Действие
    group.add_unit(unit_pcs)

    # Проверка
    assert group.units == [unit_pcs]


def test_units_property_returns_copy_success():
    """
    Свойство units возвращает копию списка: изменение копии не влияет на группу.
    """
    # Подготовка
    group = nomenclature_group_model("Овощи", [unit_model("шт", 1)])

    # Действие
    copied = group.units
    copied.clear()

    # Проверка
    assert len(group.units) == 1


@pytest.mark.parametrize("name", ["", "   ", None, 42])
def test_raise_arguments_exception_when_name_invalid(name):
    """
    Пустое или некорректное наименование группы вызывает arguments_exception.
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        nomenclature_group_model(name)


def test_raise_arguments_exception_when_name_longer_than_fifty():
    """
    Наименование группы ограничено 50 символами (обычное наименование).
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        nomenclature_group_model("а" * (NAME_MAX_LENGTH + 1))


@pytest.mark.parametrize("bad_unit", ["строка", 123, None])
def test_raise_arguments_exception_when_add_unit_wrong_type(bad_unit):
    """
    В группу можно добавлять только экземпляры unit_model.
    """
    # Подготовка
    group = nomenclature_group_model("Овощи")

    # Действие и проверка
    with pytest.raises(arguments_exception):
        group.add_unit(bad_unit)


def test_raise_arguments_exception_when_duplicate_unit_added():
    """
    Повторное добавление той же единицы измерения в группу запрещено.
    """
    # Подготовка
    unit_pcs = unit_model("шт", 1)
    group = nomenclature_group_model("Овощи", [unit_pcs])

    # Действие и проверка
    with pytest.raises(arguments_exception):
        group.add_unit(unit_pcs)
