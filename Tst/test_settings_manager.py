from Src.Logics.settings_manager import settings_manager
from Src.Core.validator import operation_exception
import time

"""
Набор модульных тестов для проверки загрузки настроек
"""
def test_not_raise_settings_manager_load():
    # Подготовка
    manager = settings_manager()

    # Действие и проверки
    try:
        manager.load("./Tst/settings.json")
        assert True
    except operation_exception :
         assert False
    except:
        assert False  

"""
Проверить загрузку настроек. Настройки не пустые.
"""
def test_not_empty_settings_manager_load():
    # Подготовка
    manager = settings_manager()
    
    # Действие 
    try:
        manager.load("./Tst/settings.json")
    except:
          assert False  

    # Проверки
    assert manager.settings is not None

"""
Проверить работу шаблона Singletone
"""
def test_equals_settings_manager_create():
    # Подготовка
    instance1 = settings_manager()
    time.sleep(1)
    instance2 = settings_manager()

    # Действие

    # Проверка
    assert instance1 == instance2


"""
Проверить работу шаблона Singletone
"""
def test_equals_properties_settings_manager_create():
    # Подготовка
    instance1 = settings_manager()
    time.sleep(1)
    instance2 = settings_manager()

    # Действие

    # Проверка
    assert instance1.settings == instance2.settings

    

"""
Проверить загрузку и конвертацию данных
"""
def test_is_loaded_settings_manager_true():
# Подготовка
    manager = settings_manager()
    
    # Действие
    try:
        manager.load("./Tst/settings.json")
    except:
        assert False  

    # Проверки
    assert manager.is_loaded == True