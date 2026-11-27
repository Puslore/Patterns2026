from typing import Any, Dict, Type
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.abstract_convertor import abstract_convertor
from Src.Logics.basic_convertor import basic_convertor
from datetime import datetime
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.list_convertor import list_convertor
from Src.Logics.dict_convertor import dict_convertor
from Src.Core.abstract_model import abstact_model
from Src.Core.entity_model import entity_model
from Src.Core.abstract_dto import abstract_dto
from Src.Logics.domain_convertor import domain_convertor
from Src.Core.validator import  operation_exception
from Src.Logics.mapping_factory import mapping_factory
from Src.Logics.dict_convertor import dict_convertor
from Src.Models.nomenclature_model import nomenclature_model

"""
Реализация фабрики для подбора нужного конвертора
"""
class convert_factory(abstract_convert_factory):
    # Маппитнг типов и конверторов
    __mapping: Dict[Type, Type[abstract_convertor]] = {}

    # Маппинг фабрика
    __mapping_factory: mapping_factory


    def __init__(self):
        super().__init__()
      
        self.__mapping_factory = mapping_factory()
        domain_conv = domain_convertor(self, self.__mapping_factory)
        self.__mapping = {
                    int: basic_convertor(),
                    float: basic_convertor(),
                    str: basic_convertor(),
                    dict: dict_convertor(self, self.__mapping_factory),
                    datetime: datetime_convertor(),
                    list: list_convertor(self, self.__mapping_factory),
                    entity_model: domain_conv, 
                    abstact_model: domain_conv,
                    nomenclature_model: domain_conv,
                    abstract_dto: domain_conv
                }

    # Singletone
    def __new__(cls):
        if not hasattr(cls, 'instance'):
              cls.instance = super(convert_factory, cls).__new__(cls)
        return cls.instance     
        

    """
    Создать требуемый конвертор
    """
    def create(self, source: Any) -> abstract_convertor:
        for source_type, convertor in self.__mapping.items():
            if isinstance(source, source_type):
                return convertor
        
        raise operation_exception(f"Указанный тип {type(source).__name__} не поддерживается!")