from Src.Logics.storage_manager import storage_manager
from Src.Core.validator import operation_exception
from Src.Models.settings_model import settings_model


"""
Проверить создание storage_manager. Нет исключения.
"""
def test_not_raise_storage_manager_build():
    # Подготовка
    settings = settings_model()
    manager = storage_manager(settings)

    # Действие и проверки
    try:
        manager.build()
        assert True
    except operation_exception :
         assert False
    except:
        assert False

"""
Проверить генерацию данных. Есть первый старт.
"""
def test_contains_data_storage_manager_build():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)

    # Действие
    result = manager.build()

    # Проверки
    assert result == True
    assert manager.data is not None
    assert len(manager.data) > 0 
    assert len(manager.data[ storage_manager.nomenclature_key() ]) > 0
    assert len(manager.data[ storage_manager.range_key() ]) > 0
    assert len(manager.data[ storage_manager.group_key() ]) > 0

"""
Проверить генерацию данных. Нет первого старта.
"""
def test_not_contains_data_storage_manager_build():
    # Подготовка
    settings = settings_model()
    settings.first_start = False
    manager = storage_manager(settings)

    # Действие
    result = manager.build()

    # Проверки
    assert result == False
    assert manager.data is not None
    assert len(manager.data) > 0 
    assert len(manager.data[ storage_manager.nomenclature_key() ]) == 0
    assert len(manager.data[ storage_manager.range_key() ]) == 0
    assert len(manager.data[ storage_manager.group_key() ]) == 0