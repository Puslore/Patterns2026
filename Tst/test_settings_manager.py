from Src.Logics.settings_manager import settings_manager
from Src.Core.validator import operation_exception
import time

"""
Проверить загрузку настроек. Нет исключения.
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
    manager.load("./Tst/settings.json")

    # Проверки
    assert manager.is_loaded == True


def test_default_settings_use_integer_inn_and_string_bank_accounts():
    """
    Настройки по умолчанию сохраняют ИНН как целое число, а счета как строки.
    Строковое представление банковских счетов сохраняет все двадцать цифр,
    включая возможные ведущие нули.
    """
    manager = settings_manager()

    result = manager._settings_manager__create_default_data()

    assert result.company.inn == 7707083893
    assert isinstance(result.company.inn, int)
    assert result.company.corr_account == "30101810400000000225"
    assert result.company.account == "40812810400000000225"
    assert result.boss_name
    assert result.account_name