from Src.Core.common import common
from Src.Models.company_model import company_model
from Src.Models.receipt_model import receipt_model
from Src.Models.ingredient_model import ingredient_model
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model


def test_not_empty_common_get_entity_header():
    """
    Проверить работу метода get_entity_header класса common для формирования заголовков сущности.
    """
    # Подготовка
    model = company_model()

    # Действие
    result = common.get_entity_header(model)

    # Проверки
    assert len(result) > 0


def test_empty_common_get_entity_table():
    """
    Проверить работу метода get_entity_table класса common для сущности без табличной части.
    """
    model = company_model()
    
    # Действие
    result = common.get_entity_table(model)
    
    # Проверки
    assert len(result) == 0


def test_not_empty_aggregate_common_get_entity_table():  
    """
    Проверить работу метода get_entity_table класса common для агрегата с табличной частью.
    """
    # Подготовка
    receipt = receipt_model()
    ingredient_oil = ingredient_model()
    ingredient_oil.name = "Масло подсолнечное"
    ingredient_oil.range = range_model.create_litr()
    ingredient_oil.group = group_model.create_default_group()
    ingredient_oil.brutto = 10
    ingredient_oil.netto = 5
    receipt.add(ingredient_oil)

    # Действие
    result = common.get_entity_table(receipt)

    # Проверки
    assert len(result) > 0
