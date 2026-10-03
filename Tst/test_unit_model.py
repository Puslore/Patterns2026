import pytest

from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exception
from Src.Models.unit_model import unit_model, NAME_MAX_LENGTH


def test_base_unit_created_with_coefficient_one_success():
    """
    Базовая единица измерения ("грамм", 1) создается без базовой единицы,
    коэффициент равен 1, признак is_base == True.
    """
    # Подготовка и действие
    base_range = unit_model("грамм", 1)

    # Проверка
    assert isinstance(base_range, abstract_model)
    assert base_range.name == "грамм"
    assert base_range.coefficient == 1
    assert base_range.base_unit is None
    assert base_range.is_base is True


def test_derived_unit_created_with_base_unit_and_coefficient_success():
    """
    Производная единица ("кг", 1000, база="грамм") создается корректно:
    коэффициент 1000, базовая единица - "грамм", is_base == False.
    """
    # Подготовка
    base_range = unit_model("грамм", 1)

    # Действие
    new_range = unit_model("кг", 1000, base_range)

    # Проверка
    assert new_range.name == "кг"
    assert new_range.coefficient == 1000
    assert new_range.base_unit is base_range
    assert new_range.is_base is False


def test_to_base_converts_amount_through_chain_success():
    """
    Пересчет количества в базовую единицу цепочки: 2 кг = 2000 грамм.
    """
    # Подготовка
    base_range = unit_model("грамм", 1)
    new_range = unit_model("кг", 1000, base_range)

    # Действие
    result = new_range.to_base(2)

    # Проверка
    assert result == 2000


def test_setter_coefficient_updates_value_success():
    """
    Свойство coefficient можно изменить на положительное число для производной единицы.
    """
    # Подготовка
    base_range = unit_model("грамм", 1)
    new_range = unit_model("кг", 1000, base_range)

    # Действие
    new_range.coefficient = 500

    # Проверка
    assert new_range.coefficient == 500


def test_setter_name_trims_spaces_success():
    """
    Наименование единицы измерения нормализуется (обрезка пробелов) при установке.
    """
    # Действие
    unit = unit_model("  кг  ", 1000, unit_model("грамм", 1))

    # Проверка
    assert unit.name == "кг"


@pytest.mark.parametrize("coefficient", [0, -1, -0.5])
def test_raise_arguments_exception_when_base_unit_has_invalid_coefficient(coefficient):
    """
    Базовая единица измерения обязана иметь коэффициент 1.
    При коэффициенте <= 0 без базовой единицы выбрасывается arguments_exception.
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        unit_model("литр", coefficient)


def test_raise_arguments_exception_when_base_unit_coefficient_not_one():
    """
    Единица без базовой (базовая сама для себя) не может иметь коэффициент, отличный от 1.
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        unit_model("шт", 5)


@pytest.mark.parametrize("coefficient", ["abc", None, True, [1]])
def test_raise_arguments_exception_when_coefficient_wrong_type(coefficient):
    """
    Коэффициент пересчета обязан быть числом; иные типы вызывают arguments_exception.
    """
    # Подготовка
    base_range = unit_model("грамм", 1)

    # Действие и проверка
    with pytest.raises(arguments_exception):
        unit_model("кг", coefficient, base_range)


@pytest.mark.parametrize("name", ["", "   ", None, 123])
def test_raise_arguments_exception_when_name_invalid(name):
    """
    Пустое/некорректное наименование единицы измерения вызывает arguments_exception.
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        unit_model(name, 1)


def test_raise_arguments_exception_when_name_longer_than_fifty():
    """
    Обычное наименование единицы измерения ограничено 50 символами.
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        unit_model("а" * (NAME_MAX_LENGTH + 1), 1)


def test_name_of_fifty_characters_is_allowed_success():
    """
    Наименование ровно из 50 символов допустимо.
    """
    # Действие
    unit = unit_model("а" * NAME_MAX_LENGTH, 1)

    # Проверка
    assert len(unit.name) == NAME_MAX_LENGTH


@pytest.mark.parametrize("base_unit", ["строка", 123, object()])
def test_raise_arguments_exception_when_base_unit_wrong_type(base_unit):
    """
    В качестве базовой единицы можно передать только экземпляр unit_model.
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        unit_model("кг", 1000, base_unit)


def test_raise_arguments_exception_when_base_unit_is_self():
    """
    Единица измерения не может быть базовой для самой себя.
    """
    # Подготовка
    unit = unit_model("грамм", 1)

    # Действие и проверка
    with pytest.raises(arguments_exception):
        unit.base_unit = unit


def test_raise_arguments_exception_when_base_unit_chain_cycle():
    """
    Циклические ссылки в цепочке базовых единиц запрещены: а <- б <- а.
    """
    # Подготовка
    unit_a = unit_model("а", 1)
    unit_b = unit_model("б", 2, unit_a)

    # Действие и проверка
    with pytest.raises(arguments_exception):
        unit_a.base_unit = unit_b


def test_raise_arguments_exception_when_to_base_amount_wrong_type():
    """
    Количество для пересчета обязано быть числом, иначе - arguments_exception.
    """
    # Подготовка
    unit = unit_model("кг", 1000, unit_model("грамм", 1))

    # Действие и проверка
    with pytest.raises(arguments_exception):
        unit.to_base("два")
