from Src.Core.abstract_mapping_factory import abstract_mapping_factory
from typing import Any, Dict, Type
from Src.Core.abstract_model import abstact_model
from Src.Core.abstract_dto import abstract_dto
from Src.Dtos.receipt_dto import receipt_dto
from Src.Models.receipt_model import receipt_model
from Src.Dtos.range_dto import range_dto 
from Src.Models.range_model import range_model
from Src.Dtos.company_dto import company_dto
from Src.Models.company_model import company_model
from Src.Dtos.group_dto import group_dto
from Src.Models.group_model import group_model
from Src.Dtos.ingredient_dto import ingredient_dto
from Src.Models.ingredient_model import ingredient_model
from Src.Dtos.nomenclature_dto import nomenclature_dto
from Src.Models.nomenclature_model import nomenclature_model
from Src.Core.entity_model import entity_model
from Src.Dtos.storage_dto import storage_dto
from Src.Models.storage_model import storage_model
from Src.Dtos.settings_dto import settings_dto
from Src.Models.settings_model import settings_model
from Src.Dtos.transaction_dto import transaction_dto
from Src.Models.transaction_model import transaction_model
from Src.Dtos.log_dto import log_dto
from Src.Models.log_model import log_model


"""
Реализация абстрактной фабрики для маппинга данных
"""
class storage_cache(dict):
    """Словарь кеша десериализации, прозрачно разрешающий ссылки на зарегистрированные объекты хранилища."""

    def _get_storage(self):
        try:
            from Src.Logics.storage_manager import storage_manager
            if hasattr(storage_manager, "instance"):
                return storage_manager.instance
        except Exception:
            pass
        return None

    def _find_in_storage(self, key: str):
        storage = self._get_storage()
        if storage is not None and hasattr(storage, "data"):
            for collection in storage.data.values():
                for item in collection:
                    if getattr(item, "unique_code", None) == key:
                        return item
                    if hasattr(item, "items"):
                        for sub in item.items:
                            if getattr(sub, "unique_code", None) == key:
                                return sub
                    if hasattr(item, "ingredients"):
                        for sub in item.ingredients:
                            if getattr(sub, "unique_code", None) == key:
                                return sub
        return None

    def __contains__(self, key):
        if super().__contains__(key):
            return True
        return self._find_in_storage(str(key).strip()) is not None

    def __getitem__(self, key):
        if super().__contains__(key):
            return super().__getitem__(key)
        item = self._find_in_storage(str(key).strip())
        if item is not None:
            super().__setitem__(key, item)
            return item
        raise KeyError(key)

    def get(self, key, default=None):
        if super().__contains__(key):
            return super().__getitem__(key)
        item = self._find_in_storage(str(key).strip())
        if item is not None:
            super().__setitem__(key, item)
            return item
        return default

    def keys(self):
        k = set(super().keys())
        storage = self._get_storage()
        if storage is not None and hasattr(storage, "data"):
            for collection in storage.data.values():
                for item in collection:
                    code = getattr(item, "unique_code", None)
                    if code:
                        k.add(code)
                    if hasattr(item, "items"):
                        for sub in item.items:
                            sub_code = getattr(sub, "unique_code", None)
                            if sub_code:
                                k.add(sub_code)
                    if hasattr(item, "ingredients"):
                        for sub in item.ingredients:
                            sub_code = getattr(sub, "unique_code", None)
                            if sub_code:
                                k.add(sub_code)
        return k


class mapping_factory(abstract_mapping_factory):

    # Маппинг между Dto и Domain сущностью
    __mapping: Dict[Type, Type] = {}

    # Кеш для десериализации
    __cache: storage_cache = storage_cache()

    def __init__(self):
        super().__init__()
        self.__mapping = {
                    receipt_dto: receipt_model,
                    range_dto: range_model,
                    company_dto: company_model,
                    group_dto: group_model,
                    ingredient_dto : ingredient_model,
                    nomenclature_dto: nomenclature_model,
                    storage_dto:storage_model,
                    settings_dto: settings_model,
                    transaction_dto: transaction_model,
                    log_dto: log_model,
                    # Обычные типы
                    int:int,
                    float:float,
                    bool: bool,
                    str: str,
                    list: list
                }

    # Singletone
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(mapping_factory, cls).__new__(cls)
        return cls.instance      

    """
    Сконвертировать доменную модель в Dto
    """
    def to_dto(self, source: object) -> object:
        if(source is None):
            return None

        for dto_type, domain_type in self.__mapping.items():
            if isinstance(source, domain_type):

                if isinstance(source, (abstact_model, entity_model)):
                    # Это доменный тип
                    return dto_type().from_domain_model( source )
                else:
                    # Это обычный тип
                    return source
                                        
        return None
    
    
    """
    Сконвертировать Dto в доменную модель
    """
    def to_model(self, source: object) -> object:
        if(source is None):
            return None
        
        for dto_type, domain_type in self.__mapping.items():
            if isinstance(source, dto_type):
        
                if isinstance(source, abstract_dto):
                        # Это Dto тип
                        return source.mapping( self.__cache  )
                else:
                        # Это обычный тип
                        return source
                                                
        return None  


    """
    Текущий кеш
    """
    @property
    def cache(self) -> dict:
         return self.__cache                                              

    """
    Маппинг типов DTO и моделей
    """
    @property
    def mapping(self) -> Dict[Type, Type]:
        return self.__mapping

    """
    Получить DTO-класс по строковому имени доменной сущности
    """
    def get_dto_type(self, entity_name: str) -> Type:
        for dto_cls, domain_cls in self.__mapping.items():
            if hasattr(domain_cls, "__name__") and domain_cls.__name__ == entity_name:
                return dto_cls
        return None

    """
    Получить полное имя класса DTO по строковому имени доменной сущности
    """
    def get_dto_type_name(self, entity_name: str) -> str:
        dto_cls = self.get_dto_type(entity_name)
        if dto_cls is not None:
            return f"{dto_cls.__module__}.{dto_cls.__name__}"
        return ""

    """
    Получить класс доменной модели по строковому имени сущности
    """
    def get_domain_type(self, entity_name: str) -> Type:
        for dto_cls, domain_cls in self.__mapping.items():
            if hasattr(domain_cls, "__name__") and domain_cls.__name__ == entity_name:
                return domain_cls
        return None                                              
