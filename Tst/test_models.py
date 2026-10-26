from Src.Models.company_model import company_model
from Src.Models.storage_model import storage_model
from Src.Models.nomenclature_model import nomenclature_model
import uuid
from Src.Core.validator import argument_exception
from Src.Models.receipt_model import receipt_model
from Src.Models.ingredient_model import ingredient_model
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Models.settings_model import settings_model
import pytest

# Необходимо установить pip install pytest в терминале с подключенным Environment
# Далее, настройки
# {
#    "python.testing.pytestArgs": [
#        "Tst"
#    ],
#    "python.testing.unittestEnabled": false,
#    "python.testing.pytestEnabled": true
#}

#**ОжиданиеРезультата_НаименованиеМетодаКласса_КраткоеОписание**

# Провери создание основной модели
# Данные после создания должны быть пустыми
def test_empty_company_model_createmodel():
    # Подготовка
    model = company_model()

    # Действие

    # Проверки
    assert model.name == ""

# Проверить создание основной модели
# Данные меняем. Данные должны быть
def test_notEmpty_company_model_createmodel():
    # Подготовка
    model = company_model()
        
    # Действие
    model.name = "test"
        
    # Проверки
    assert model.name != ""

# Проверка на сравнение двух по значению одинаковых моделей
def test_equals_storage_model_create():
    # Подготовка
    id = uuid.uuid4().hex
    storage1 = storage_model()
    storage1.unique_code = id
    storage2 = storage_model()   
    storage2.unique_code = id

    # Действие 

    # Проверки
    assert storage1 == storage2

# Проверить создание номенклатуры и присвоение уникального кода
def test_equals_nomenclature_model_create():
    # Подготовка
    id = uuid.uuid4().hex
    item1 = nomenclature_model()
    item1.unique_code = id
    item2 = nomenclature_model()
    item2.unique_code = id

    # Действие

    # Проверки
    assert item1 == item2

# Проверить наличие исключения
# при передаче некорректного значения БИК
def test_raise_company_model_fail_bik():
    # Подготовка
    company = company_model()

    # Действие и проверка
    try:
        company.bik = -99999999999
        assert False
    except argument_exception :
        assert True
    except:
        assert False    

# Проверить создание рецепта
def test_add_receipt_model_create():
    # Подготовка
    receipt = receipt_model()
    ingredient_oil = ingredient_model()
    ingredient_oil.name = "Масло подсолнечное"
    ingredient_oil.range = range_model.create_litr()
    ingredient_oil.group = group_model.create_default_group()
    ingredient_oil.brutto = 10
    ingredient_oil.netto = 5
    

    # Действие
    receipt.add(ingredient_oil)

    # Проверки
    assert receipt.brutto == 10
    assert receipt.netto == 5

# Проверить создание сложного рецепта (блюдо в блюде)
def test_add_combo_receipt_model_create():
    # Подготовка
    receipt = receipt_model()

    ingredient_oil = ingredient_model()
    ingredient_oil.name = "Масло подсолнечное разливное"
    ingredient_oil.range = range_model.create_litr()
    ingredient_oil.group = group_model.create_default_group()
    ingredient_oil.brutto = 10
    ingredient_oil.netto = 5

    ingredient_oil_bottle = ingredient_model()
    ingredient_oil_bottle.name = "Масло подсолнечное упакованное"
    ingredient_oil_bottle.range = range_model.create_litr()
    ingredient_oil_bottle.group = ingredient_oil.group
    ingredient_oil_bottle.brutto = 2
    ingredient_oil_bottle.netto = 2
    # -> Блюдо в блюде
    ingredient_oil_bottle.base = ingredient_oil

    ingredient_tape = ingredient_model()
    ingredient_tape.name = "Подарочная упаковка"
    ingredient_tape.range = range_model.create_thing()
    ingredient_tape.brutto = 1

    # Действие
    receipt.add(ingredient_oil_bottle)
    receipt.add(ingredient_tape)

    # Проверки
    assert receipt.brutto == 13
    assert receipt.netto == 7
