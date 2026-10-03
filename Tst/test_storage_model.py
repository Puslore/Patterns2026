import pytest

from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exception
from Src.Models.storage_model import storage_model
from Src.Models.organization_model import organization_model, ownership_form
from Src.Models.unit_model import NAME_MAX_LENGTH


def _make_organization() -> organization_model:
    """
    Вспомогательная функция: создает корректную организацию-владельца склада.
    """
    return organization_model(
        "ООО Ромашка", "7701234567", "044525225", "40702810000000000123",
        ownership_form.LIMITED_LIABILITY_COMPANY)


def test_storage_created_with_minimal_parameters_success():
    """
    Склад корректно создается только с наименованием: адрес и организация по умолчанию None.
    """
    # Действие
    store = storage_model("Центральный склад")

    # Проверка
    assert isinstance(store, abstract_model)
    assert store.name == "Центральный склад"
    assert store.address is None
    assert store.organization is None
    assert store.id != ""


def test_storage_created_with_all_parameters_success():
    """
    Склад корректно создается со всеми параметрами:
    наименование, адрес, организация-владелец и явный идентификатор.
    """
    # Подготовка
    org = _make_organization()

    # Действие
    store = storage_model("Склад цеха", "г. Москва, ул. Складская, 1", org, id="store-1")

    # Проверка
    assert store.id == "store-1"
    assert store.name == "Склад цеха"
    assert store.address == "г. Москва, ул. Складская, 1"
    assert store.organization is org


def test_setters_update_storage_fields_success():
    """
    Сеттеры address и organization обновляют значения при корректных данных.
    """
    # Подготовка
    store = storage_model("Склад")
    org = _make_organization()

    # Действие
    store.address = "г. Москва, ул. Ленина, 5"
    store.organization = org

    # Проверка
    assert store.address == "г. Москва, ул. Ленина, 5"
    assert store.organization is org


@pytest.mark.parametrize("name", ["", "   ", None, 42])
def test_raise_arguments_exception_when_name_invalid(name):
    """
    Пустое или некорректное наименование склада вызывает arguments_exception.
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        storage_model(name)


def test_raise_arguments_exception_when_name_longer_than_fifty():
    """
    Наименование склада ограничено 50 символами (обычное наименование).
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        storage_model("а" * (NAME_MAX_LENGTH + 1))


@pytest.mark.parametrize("address", ["", "   ", 42])
def test_raise_arguments_exception_when_address_invalid(address):
    """
    Пустой или некорректный адрес склада вызывает arguments_exception.
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        storage_model("Склад", address)


@pytest.mark.parametrize("bad_org", ["строка", 123, object()])
def test_raise_arguments_exception_when_organization_wrong_type(bad_org):
    """
    Владелец склада обязан быть экземпляром organization_model.
    """
    # Действие и проверка
    with pytest.raises(arguments_exception):
        storage_model("Склад", organization=bad_org)
