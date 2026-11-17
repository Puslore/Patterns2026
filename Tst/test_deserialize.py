from Src.Logics.convertor import convertor
from Src.Logics.storage_manager import storage_manager
from Src.Models.settings_model import settings_model
import json


"""
Выполнить десериализацию единиц измерения
""" 
def test_deserialize_range_model():
    # Подготовка
    source =  {"range_model": [
        {
            "base_code": "",
            "name": "Грамм",
            "type": "Src.Dtos.range_dto.range_dto",
            "unique_code": "1aff87893350487c8b78ff73ddd22270",
            "value": 1
        },
        {
            "base_code": "1aff87893350487c8b78ff73ddd22270",
            "name": "Коллограмм",
            "type": "Src.Dtos.range_dto.range_dto",
            "unique_code": "496fb570791f4d15b8e1dcfc6dec1bc9",
            "value": 1000
        },
        {
            "base_code": "",
            "name": "Штуки",
            "type": "Src.Dtos.range_dto.range_dto",
            "unique_code": "0c6822a1cd74454ab7d02d0145280005",
            "value": 1
        }
    ]}
    worker = convertor()

    # Действие
    result = worker.deserialize(source)

    # Проверки
    assert worker.is_error == False
    assert result is not None
    assert len(result) > 0

"""
Полный тест. Загрузка данных от storage_manager
"""
def test_deserialize_storage_manager():
    # Подготовка
    try:
        with open("storage_manager.json", 'r', encoding='utf-8') as file_instance:
            source = json.load(  file_instance )
            worker = convertor()

            # Действие
            result = worker.deserialize(source)

            # Проверки
            print (worker.error_text)
            assert worker.is_error == False
            assert result is not None
            assert len(result) > 0 
    except:
        assert False        
