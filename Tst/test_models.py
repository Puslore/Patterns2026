from Src.Models.company_model import company_model
from Src.Models.storage_model import storage_model
from Src.Models.nomenclature_model import nomenclature_model
import uuid
import pytest
from Src.Core.validator import argument_exception


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


def test_group_setter_rejects_storage_model():
    """
    Сеттер группы номенклатуры отклоняет другую доменную модель.
    Склад не является группой номенклатуры и должен вызвать исключение
    валидации при присваивании.
    """
    item = nomenclature_model()

    with pytest.raises(argument_exception):
        item.group = storage_model()

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
