from Src.Logics.storage_manager import storage_manager
from Src.Models.settings_model import settings_model
from Src.Dtos.receipt_dto import receipt_dto
from Src.Dtos.range_dto import range_dto
from Src.Dtos.nomenclature_dto import nomenclature_dto
from Src.Dtos.ingredient_dto import ingredient_dto
import pytest

def test_receipt_dto_from_storage_manager_build():
    """
    Проверить получение рецепта из storage_manager, 
    его преобразование в receipt_dto и сравнение количественных показателей.
    """
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()

    # Действие
    domain = manager.data[storage_manager.receipt_key()][0]
    dto = receipt_dto().from_domain_model(domain)

    # Проверки
    assert dto.name == domain.name
    assert dto.brutto == domain.brutto
    assert dto.netto == domain.netto
    assert dto.comments == domain.comments
    assert len(dto.items) == len(domain.items)


def test_range_dto_from_storage_manager_build():
    """
    Проверить получение единицы измерения из storage_manager, 
    ее преобразование в range_dto и сравнение показателей.
    """
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()

    # Действие
    domain = manager.data[storage_manager.range_key()][0]
    dto = range_dto().from_domain_model(domain)

    # Проверки
    assert dto.name == domain.name
    assert dto.value == domain.value
    if  domain.base is not None:
        assert dto.base_code == domain.base.unique_code 


def test_ingredient_dto_from_storage_manager_build():
    """
    Проверить получение ингредиента из состава рецепта, 
    его преобразование в ingredient_dto и сравнение показателей.
    """
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()

    # Действие
    domain = manager.data[storage_manager.receipt_key()][0].items[0]
    dto = ingredient_dto().from_domain_model(domain)

    # Проверки
    assert dto.name == domain.name
    assert dto.brutto == domain.brutto
    assert dto.netto == domain.netto


def test_nomenclature_dto_from_storage_manager_build():
    """
    Проверить получение номенклатуры из storage_manager, 
    ее преобразование в nomenclature_dto и сравнение показателей.
    """
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    manager.build()

    # Действие
    domain = manager.data[storage_manager.nomenclature_key()][0]
    dto = nomenclature_dto().from_domain_model(domain)

    # Проверки
    assert dto.name == domain.name
    assert dto.range_code == domain.range.unique_code