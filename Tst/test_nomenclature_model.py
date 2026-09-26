import pytest

from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exception
from Src.Models.nomenclature_model import nomenclature_model, FULL_NAME_MAX_LENGTH
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.unit_model import unit_model, NAME_MAX_LENGTH


def test_nomenclature_created_with_minimal_parameters_success():
    """
    Номенклатура корректно создается только с кратким наименованием:
    полное наименование, группа и единица измерения по умолчанию None.
    """
    # Действие
    item = nomenclature_model("Мука")

    # Проверка
    assert isinstance(item, abstract_model)
    assert item.name == "Мука"
    assert item.full_name is None
    assert item.group is None
    assert item.unit is None
    assert item.id != ""


def test_nomenclature_created_with_all_parameters_success():
    """
    Номенклатура корректно создается со всеми параметрами:
    краткое и полное наименования, группа номенклатуры, единица измерения, id.
    Модель включает в себя другие модели: nomenclature_group_model и unit_model.
    """
    # Подготовка
    unit_gramm = unit_model("грамм", 1)
    unit_kg = unit_model("кг", 1000, unit_gramm)
    group = nomenclature_group_model("Сыпучие")

    # Действие
    item = nomenclature_model(
        name="Мука",
        full_name="Мука пшеничная высшего сорта 1кг",
        group=group,
        unit=unit_kg,
        id="nom-1",
    )

    # Проверка
    assert item.id == "nom-1"
    assert item.name == "Мука"
    assert item.full_name == "Мука пшеничная высшего сорта 1кг"
    assert item.group is group
    assert item.unit is unit_kg


def test_setters_assign_nested_models_success():
    """
    Свойства group и unit можно установить после создания через сеттеры.
    """
    # Подготовка
    item = nomenclature_model("Сахар")
    group = nomenclature_group_model("Сыпучие")
    unit_pcs = unit_model("шт", 1)

    # Действие
    item.group = group
    item.unit = unit_pcs
    item.full_name = "Сахар-песок пищевой"

    # Проверка
    assert item.group is group
    assert item.unit is unit_pcs
    assert item.full_name == "Сахар-песок пищевой"


def test_full_name_of_two_hundred_fifty_five_characters_is_allowed_success():
    """
    Полное наименование длиной ровно 255 символов допустимо.
    """
    # Действие
    item = nomenclature_model("Масло", full_name="а" * FULL_NAME_MAX_LENGTH)

    # Проверка
    assert len(item.full_name) == FULL_NAME_MAX_LENGTH


@pytest.mark.parametrize("full_name", ["", "   ", 42])
def test_raise_arguments_exception_when_full_name_invalid(full_name):
    """
    Пустое или некорректное полное наименование вызывает arguments_exception.
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        nomenclature_model("Мука", full_name=full_name)


def test_full_name_none_means_absent_success():
    """
    Отсутствие полного наименования (None) допустимо - поле остается None.
    """
    # Действие
    item = nomenclature_model("Мука")

    # Проверка
    assert item.full_name is None


def test_raise_arguments_exception_when_full_name_longer_than_two_hundred_fifty_five():
    """
    Полное наименование ограничено 255 символами.
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        nomenclature_model("Мука", full_name="а" * (FULL_NAME_MAX_LENGTH + 1))


@pytest.mark.parametrize("name", ["", "   ", None, 42])
def test_raise_arguments_exception_when_name_invalid(name):
    """
    Пустое или некорректное краткое наименование номенклатуры вызывает arguments_exception.
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        nomenclature_model(name)


def test_raise_arguments_exception_when_name_longer_than_fifty():
    """
    Краткое наименование номенклатуры ограничено 50 символами (обычное наименование).
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        nomenclature_model("а" * (NAME_MAX_LENGTH + 1))


@pytest.mark.parametrize("bad_group", ["строка", 123, unit_model("грамм", 1)])
def test_raise_arguments_exception_when_group_wrong_type(bad_group):
    """
    Группа номенклатуры обязана быть экземпляром nomenclature_group_model.
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        nomenclature_model("Мука", group=bad_group)


@pytest.mark.parametrize("bad_unit", ["строка", 123, nomenclature_group_model("Сыпучие")])
def test_raise_arguments_exception_when_unit_wrong_type(bad_unit):
    """
    Единица измерения обязана быть экземпляром unit_model.
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        nomenclature_model("Мука", unit=bad_unit)
