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

"""
Реализация абстрактной фабрики для маппинга данных
"""
class mapping_factory(abstract_mapping_factory):

    # Маппинг между Dto и Domain сущностью
    __mapping: Dict[Type, Type] = {}

    def __init__(self):
        super().__init__()
        self.__mapping = {
                    receipt_dto: receipt_model,
                    range_dto: range_model,
                    company_dto: company_model,
                    group_dto: group_model,
                    ingredient_dto : ingredient_model,
                    nomenclature_dto: nomenclature_model,
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
        for dto_type, domain_type in self.__mapping.items():
            if isinstance(source, domain_type):

                if isinstance(source, abstact_model):
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
        pass                                                
