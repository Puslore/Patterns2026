from Src.Models.settings_model import settings_model
from Src.Logics.storage_manager import storage_manager
from Src.Dtos.filter_dto import filter_dto, filter_item_dto
from Src.Logics.prototype import prototype


"""
Проверить работу прототипа
"""
def test_contains_data_prototype():
    # Подготовка
    settings = settings_model()
    settings.first_start = True
    manager = storage_manager(settings)
    result = manager.build()
    filter = filter_dto()
    item = filter_item_dto()

    item.__field_name = "name"
    item.__filter_type = "eq"
    item.__value = "Киллограм"
    filter.__filters = [ item  ]
    pr = prototype( manager.data[ storage_manager.transaction_key() ] )

    # Действие
    result = pr.clone( filter )
        
    # Проверки
    assert len(result.__data) > 0
    
