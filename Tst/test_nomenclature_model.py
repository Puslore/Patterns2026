import pytest

from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exception
from Src.Models.nomenclature_model import nomenclature_model, FULL_NAME_MAX_LENGTH
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.unit_model import unit_model, NAME_MAX_LENGTH


def test_nomenclature_created_with_required_parameters_success():
    """
    Номенклатура корректно создается с обязательными параметрами:
    наименование, группа номенклатуры и единица измерения.
    Полное наименование по умолчанию None.
    """
    # Подготовка
    group = nomenclature_group_model("Сыпучие", [unit_model("грамм", 1)])
    unit_gramm = unit_model("грамм", 1)

    # Действие
    item = nomenclature_model("Мука", group, unit_gramm)

    # Проверка
    assert isinstance(item, abstract_model)
    assert item.name == "Мука"
    assert item.full_name is None
    assert item.group is group
    assert item.unit is unit_gramm
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
    group = nomenclature_group_model("Сыпучие", [unit_model("грамм", 1)])

    # Действие
    item = nomenclature_model(
        name="Мука",
        group=group,
        unit=unit_kg,
        full_name="Мука пшеничная высшего сорта 1кг",
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
    Свойства group и unit можно переопределить после создания через сеттеры.
    """
    # Подготовка
    item = nomenclature_model("Сахар", nomenclature_group_model("Сыпучие", [unit_model("грамм", 1)]), unit_model("грамм", 1))
    group = nomenclature_group_model("Бакалея", [unit_model("грамм", 1)])
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
    # Подготовка
    group = nomenclature_group_model("Масла", [unit_model("л", 1)])
    unit_l = unit_model("л", 1)

    # Действие
    item = nomenclature_model("Масло", group, unit_l, full_name="а" * FULL_NAME_MAX_LENGTH)

    # Проверка
    assert len(item.full_name) == FULL_NAME_MAX_LENGTH


@pytest.mark.parametrize("full_name", ["", "   ", 42])
def test_raise_arguments_exception_when_full_name_invalid(full_name):
    """
    Пустое или некорректное полное наименование вызывает arguments_exception.
    """
    # Подготовка
    group = nomenclature_group_model("Сыпучие", [unit_model("грамм", 1)])
    unit_gramm = unit_model("грамм", 1)

    # Действие и проверка
    with pytest.raises(arguments_exception):
        nomenclature_model("Мука", group, unit_gramm, full_name=full_name)


def test_full_name_none_means_absent_success():
    """
    Отсутствие полного наименования (None) допустимо - поле остается None.
    """
    # Подготовка
    group = nomenclature_group_model("Сыпучие", [unit_model("грамм", 1)])
    unit_gramm = unit_model("грамм", 1)

    # Действие
    item = nomenclature_model("Мука", group, unit_gramm)

    # Проверка
    assert item.full_name is None


def test_raise_arguments_exception_when_full_name_longer_than_two_hundred_fifty_five():
    """
    Полное наименование ограничено 255 символами.
    """
    # Подготовка
    group = nomenclature_group_model("Сыпучие", [unit_model("грамм", 1)])
    unit_gramm = unit_model("грамм", 1)

    # Действие и проверка
    with pytest.raises(arguments_exception):
        nomenclature_model("Мука", group, unit_gramm, full_name="а" * (FULL_NAME_MAX_LENGTH + 1))


@pytest.mark.parametrize("name", ["", "   ", None, 42])
def test_raise_arguments_exception_when_name_invalid(name):
    """
    Пустое или некорректное краткое наименование номенклатуры вызывает arguments_exception.
    """
    # Подготовка
    group = nomenclature_group_model("Сыпучие", [unit_model("грамм", 1)])
    unit_gramm = unit_model("грамм", 1)

    # Действие и проверка
    with pytest.raises(arguments_exception):
        nomenclature_model(name, group, unit_gramm)


def test_raise_arguments_exception_when_name_longer_than_fifty():
    """
    Краткое наименование номенклатуры ограничено 50 символами (обычное наименование).
    """
    # Подготовка
    group = nomenclature_group_model("Сыпучие", [unit_model("грамм", 1)])
    unit_gramm = unit_model("грамм", 1)

    # Действие и проверка
    with pytest.raises(arguments_exception):
        nomenclature_model("а" * (NAME_MAX_LENGTH + 1), group, unit_gramm)


@pytest.mark.parametrize("bad_group", ["строка", 123, None, unit_model("грамм", 1)])
def test_raise_arguments_exception_when_group_wrong_type(bad_group):
    """
    Группа номенклатуры обязательна и обязана быть экземпляром nomenclature_group_model.
    Передача None или значения другого типа вызывает arguments_exception.
    """
    # Подготовка
    unit_gramm = unit_model("грамм", 1)

    # Действие и проверка
    with pytest.raises(arguments_exception):
        nomenclature_model("Мука", bad_group, unit_gramm)


@pytest.mark.parametrize("bad_unit", ["строка", 123, None, nomenclature_group_model("Сыпучие", [unit_model("грамм", 1)])])
def test_raise_arguments_exception_when_unit_wrong_type(bad_unit):
    """
    Единица измерения обязательна и обязана быть экземпляром unit_model.
    Передача None или значения другого типа вызывает arguments_exception.
    """
    # Подготовка
    group = nomenclature_group_model("Сыпучие", [unit_model("грамм", 1)])

    # Действие и проверка
    with pytest.raises(arguments_exception):
        nomenclature_model("Мука", group, bad_unit)


def test_raise_type_error_when_required_parameters_missing():
    """
    Создание номенклатуры без обязательных group и unit невозможно -
    Python вызывает TypeError из-за отсутствующих обязательных аргументов.
    """
    # Действие и проверка
    with pytest.raises(TypeError):
        nomenclature_model("Мука")
