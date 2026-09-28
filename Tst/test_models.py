from Src.Models.company_model import company_model
from Src.Models.storage_model import storage_model
from Src.Models.nomenclature_model import nomenclature_model


# Необходимо установить pip install pytest в терминале с подключенным Environment
# Далее, настройки
# {
#    "python.testing.pytestArgs": [
#        "Tst"
#    ],
#    "python.testing.unittestEnabled": false,
#    "python.testing.pytestEnabled": true
#}


    # Провери создание основной модели
    # Данные после создания должны быть пустыми
    def test_empty_createmodel_companymodel(self):
        # Подготовка
        model = company_model()

        # Действие

        # Проверки
        assert model.name == ""


    # Проверить создание основной модели
    # Данные меняем. Данные должны быть
    def test_notEmpty_createmodel_companymodel(self):
        # Подготовка
        model = company_model()
        
        # Действие
        model.name = "test"
        
        # Проверки
        assert model.name != ""



    # Проверка на сравнение двух по значению одинаковых моделей
    def test_equals_storage_model_create(self):
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
    def test_equals_nomenclature_model_create(self):
        # Подготовка
        id = uuid.uuid4().hex
        item1 = nomenclature_model()
        item1.unique_code = id
        item2 = nomenclature_model()
        item2.unique_code = id

        # Действие

        # Проверки
        assert item1 == item2