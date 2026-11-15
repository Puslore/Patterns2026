from Src.Logics.settings_manager import settings_manager
from Src.Core.validator import operation_exception
import time
from Src.Dtos.report_type_enum import report_type_enum

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


"""
Проверить загрузку default_report_type
"""
def test_default_report_type_settings_manager_true(): 
    # Подготовка
    manager = settings_manager()
        
    # Действие
    manager.load("./Tst/settings.json")
    
    # Проверки
    assert manager.settings.default_report_type == report_type_enum.CSV


def test_settings_loaded_directly_via_common_deserializer():
    """
    Проверить, что настройки загружаются непосредственно через общий механизм десериализации convertor.
    """
    from Src.Logics.convertor import convertor
    from Src.Models.settings_model import settings_model
    import json

    with open("./Tst/settings.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    worker = convertor()
    result = worker.deserialize(data)

    assert result is not None
    assert isinstance(result, settings_model)
    assert result.company.name == "ООО Ромашка"
    assert result.boss_name == "Воловиков Александр Сергеевич"


def test_settings_manager_preserves_last_valid_settings_on_error(tmp_path):
    """
    При ошибке загрузки настроек сохраняются последние корректные настройки.
    """
    manager = settings_manager()
    manager.load("./Tst/settings.json")
    valid_boss = manager.settings.boss_name
    valid_company = manager.settings.company.name
    assert valid_boss != ""

    # Создаем поврежденный файл настроек
    bad_file = tmp_path / "bad_settings.json"
    bad_file.write_text("{ invalid json syntax ...", encoding="utf-8")

    # Попытка загрузить поврежденный файл должна выбросить operation_exception
    try:
        manager.load(str(bad_file))
        assert False, "Ожидалось исключение operation_exception"
    except operation_exception:
        pass

    # Проверяем, что настройки остались прежними
    assert manager.settings.boss_name == valid_boss
    assert manager.settings.company.name == valid_company
